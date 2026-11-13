import numpy as np
import pandas as pd
import streamlit as st

from dados import QUALITATIVAS, QUANTITATIVAS, carregar_amostra, carregar_populacao, checar_dados, fmt_dec
from inferencia import cobertura_ic_media, cobertura_ic_proporcao, teste_media, teste_proporcao
from visual import grafico_distribuicao

st.set_page_config(page_title="Painel 3 — Inferência", page_icon="🏫", layout="wide")
checar_dados()
pop, am = carregar_populacao(), carregar_amostra()

# ---------------------------------------------------------------------------
# As quatro perguntas. Todas têm valor de comparação com fonte pública.
# ---------------------------------------------------------------------------
SO_PUBLICAS = {"nome": "escolas públicas", "fn": lambda d: d[d["DEPENDENCIA"] != "Privada"]}

HIPOTESES = [
    {"tipo": "media", "var": "QT_MAT_BAS", "ref": 265.0, "alt": "two-sided", "escopo": None,
     "curto": "Matrículas por escola", "rot_ref": "Em 2023",
     "pergunta": "A média de matrículas por escola mudou desde 2023?",
     "sim": "Sim, a média de matrículas por escola mudou desde 2023.",
     "nao": "Não dá para afirmar que a média de matrículas por escola mudou desde 2023.",
     "veredito": {"sim": "Mudou", "nao": "Sem mudança comprovada"},
     "ref_curta": "Censo Escolar 2023: 47,3 milhões de matrículas ÷ 178,5 mil escolas ≈ 265",
     "afirmacao": "a média de matrículas por escola em 2024 é diferente da de 2023 (265)",
     "origem": (
         "**Valor de referência: μ₀ = 265 matrículas por escola (Censo Escolar 2023, INEP).**  \n"
         "Como foi obtido: 47.304.632 matrículas ÷ 178,5 mil escolas ≈ 265,0.  \n"
         "Por que é comparável: a soma de `QT_MAT_BAS` na nossa população (47,06 milhões) bate com o total oficial "
         "de 2024 (47,1 milhões), ou seja, a variável tem a mesma definição.  \n"
         "Limitação: 178,5 mil é um número arredondado, então μ₀ tem incerteza de cerca de ±0,1.  \n"
         "Fonte: [Apresentação INEP — Censo Escolar 2023]"
         "(https://goias.gov.br/educacao/wp-content/uploads/sites/40/2024/02/apresentacao_coletiva-783.pdf)."
     )},
    {"tipo": "proporcao", "var": "IN_INTERNET", "ref": 0.885, "alt": "greater", "escopo": SO_PUBLICAS,
     "curto": "Internet nas escolas públicas", "rot_ref": "Em 2023",
     "pergunta": "A internet nas escolas públicas avançou desde 2023?",
     "sim": "Sim, a internet nas escolas públicas avançou desde 2023.",
     "nao": "Não dá para afirmar que a internet nas escolas públicas avançou desde 2023.",
     "veredito": {"sim": "Avançou", "nao": "Avanço não comprovado"},
     "ref_curta": "Censo Escolar 2023 (MEC): 88,5% das escolas públicas tinham internet",
     "afirmacao": "mais de 88,5% das escolas públicas têm internet (houve avanço desde 2023)",
     "origem": (
         "**Valor de referência: p₀ = 0,885 (88,5% das escolas públicas com internet em 2023, MEC/INEP).**  \n"
         "Escopo: escola pública = federal + estadual + municipal. As privadas ficaram de fora porque já estavam "
         "perto de 100%, e o dado oficial citado é só das públicas.  \n"
         "Pergunta: houve avanço de 2023 para 2024? Por isso o teste é unilateral (H₁: p > p₀).  \n"
         "Ressalva: o número vem de reportagem sobre o Censo 2023; vale conferir a definição de “internet” no resumo "
         "técnico do INEP.  \n"
         "Fonte: [Olhar Digital — Censo 2023](https://olhardigital.com.br/2024/02/23/pro/"
         "censo-2023-escolas-estao-mais-conectadas-com-excecao-da-regiao-norte/)."
     )},
    {"tipo": "proporcao", "var": "IN_TEMPO_INTEGRAL", "ref": 0.50, "alt": "less", "escopo": SO_PUBLICAS,
     "curto": "Meta de tempo integral (PNE)", "rot_ref": "Meta do PNE",
     "pergunta": "A meta de tempo integral do PNE (50% das escolas públicas) foi atingida?",
     "sim": "Não, a meta não foi atingida: menos de 50% das escolas públicas são de tempo integral.",
     "nao": "Não dá para afirmar que a meta de tempo integral do PNE não foi atingida.",
     "veredito": {"sim": "Meta NÃO atingida", "nao": "Sem evidência de falha"},
     "ref_curta": "Meta 6 do PNE (Lei 13.005/2014): no mínimo 50% das escolas públicas em tempo integral",
     "afirmacao": "menos de 50% das escolas públicas são de tempo integral, ou seja, a Meta 6 do PNE não foi atingida",
     "origem": (
         "**Valor de referência: p₀ = 0,50, a meta do Plano Nacional de Educação (Lei 13.005/2014, Meta 6).**  \n"
         "A meta manda “oferecer educação em tempo integral em, no mínimo, 50% das escolas públicas”, atendendo pelo "
         "menos 25% dos alunos. Uma escola conta como de tempo integral quando pelo menos **25% dos alunos** estão em "
         "jornada de 7 horas ou mais.  \n"
         "Como medimos: `IN_TEMPO_INTEGRAL` = 1 quando as matrículas em tempo integral são ≥ 25% das matrículas da "
         "escola. O escopo são as escolas públicas (federais, estaduais e municipais).  \n"
         "Pergunta: a meta foi cumprida? Por isso o teste é unilateral (H₁: p < 0,50).  \n"
         "Ressalvas: o indicador oficial exclui EJA e educação profissional do cálculo e inclui atividades "
         "complementares; a nossa medida usa as matrículas em tempo integral do Censo sobre o total `QT_MAT_BAS`. "
         "Na rede pública isso dá 21,1% das matrículas, contra 22,9% no dado oficial de 2024, ou seja, é uma boa aproximação.  \n"
         "Fontes: [Meta 6 do PNE (MPCE)](https://mpce.mp.br/?p=106924); "
         "[Lei 13.005/2014](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l13005.htm)."
     )},
    {"tipo": "media", "var": "PCT_INTEGRAL", "ref": 25.0, "alt": "two-sided", "escopo": SO_PUBLICAS,
     "curto": "% de tempo integral por escola", "rot_ref": "Patamar do PNE",
     "pergunta": "A escola pública média está no patamar de 25% de alunos em tempo integral?",
     "sim": "Não, a escola pública média foge do patamar de 25% de alunos em tempo integral.",
     "nao": "Sim, a escola pública média está no patamar de 25% (não há diferença comprovada).",
     "veredito": {"sim": "Fora do patamar", "nao": "No patamar de 25%"},
     "ref_curta": "Patamar de 25% da Meta 6 do PNE (mínimo de alunos em tempo integral)",
     "afirmacao": "a escola pública média tem um percentual de matrículas em tempo integral diferente de 25%",
     "origem": (
         "**Valor de referência: μ₀ = 25% de matrículas em tempo integral (patamar da Meta 6 do PNE).**  \n"
         "O PNE usa 25% em dois lugares: como porcentagem mínima de alunos atendidos e como corte para classificar uma "
         "escola como de tempo integral. Aqui perguntamos se a **escola pública média** está nesse patamar.  \n"
         "Variável: `PCT_INTEGRAL` = % das matrículas da escola em tempo integral (média simples entre escolas, sem "
         "ponderar pelo tamanho).  \n"
         "Ressalva: a meta oficial de 25% é sobre o total de alunos do país, enquanto aqui comparamos a média das "
         "porcentagens por escola; os dois números são parecidos, mas não idênticos. A variável é muito assimétrica "
         "(muitas escolas com 0% e muitas com 100%).  \n"
         "Fontes: [Meta 6 do PNE (MPCE)](https://mpce.mp.br/?p=106924); "
         "[Lei 13.005/2014](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l13005.htm)."
     )},
]

SIMB = {"two-sided": "≠", "greater": ">", "less": "<"}
PALAVRA = {"two-sided": "diferente de", "greater": "maior que", "less": "menor que"}


def subconjuntos(h):
    """Aplica o escopo da hipótese (ex.: só escolas públicas) à população e à amostra."""
    if h["escopo"]:
        return h["escopo"]["fn"](pop), h["escopo"]["fn"](am)
    return pop, am


def rotulo_de(h):
    base = (QUALITATIVAS if h["tipo"] == "proporcao" else QUANTITATIVAS)[h["var"]]
    return f"{base} — {h['escopo']['nome']}" if h["escopo"] else base


def unidade(h):
    """(escala, sufixo, casas) para exibir o valor: proporção vira %, PCT_INTEGRAL já está em %."""
    if h["tipo"] == "proporcao":
        return 100, "%", 1
    if h["var"] == "PCT_INTEGRAL":
        return 1, "%", 1
    return 1, "", 1


# ---------------------------------------------------------------------------
# Parâmetros globais (barra lateral)
# ---------------------------------------------------------------------------
st.sidebar.header("Parâmetros globais")
alpha = st.sidebar.selectbox("Nível de significância (α)", [0.01, 0.05, 0.10], index=1)
confianca = 1 - alpha
st.sidebar.caption("α é a probabilidade máxima de rejeitar H₀ quando ela é verdadeira (erro tipo I).")
st.sidebar.caption(f"A margem de erro (IC) usa confiança de {confianca:.0%} (= 1 − α).")


def calcular(i, h):
    prop = h["tipo"] == "proporcao"
    pop_h, am_h = subconjuntos(h)
    ref = float(st.session_state.get(f"ref{i}", h["ref"]))  # valor editado nos detalhes técnicos, se houver
    if prop:
        x = int(am_h[h["var"]].sum())
        r = teste_proporcao(x, len(am_h), ref, h["alt"], alpha, confianca, len(pop_h))
    else:
        x = None
        r = teste_media(am_h[h["var"]], ref, h["alt"], alpha, confianca, len(pop_h))
    ver = float(pop_h[h["var"]].mean())
    esc, suf, cas = unidade(h)
    return {"i": i, "h": h, "prop": prop, "pop_h": pop_h, "am_h": am_h, "n": len(am_h), "N": len(pop_h),
            "ref": ref, "x": x, "r": r, "ver": ver, "cobre": r.ic[0] <= ver <= r.ic[1],
            "dentro": r.ic[0] <= ref <= r.ic[1], "esc": esc, "suf": suf, "cas": cas}


def fu(R, v):
    """Formata um valor na unidade de exibição da hipótese (ex.: 0,890 -> '89,0%')."""
    return fmt_dec(v * R["esc"], R["cas"]) + R["suf"]


def fp(p):
    return "menor que 0,001" if p < 0.001 else fmt_dec(p, 3)


RES = [calcular(i, h) for i, h in enumerate(HIPOTESES, 1)]

# ---------------------------------------------------------------------------
# Topo: como decidimos + as 4 respostas
# ---------------------------------------------------------------------------
st.title("Painel 3 — O que a amostra nos diz sobre todas as escolas?")
st.markdown(
    f"Sorteamos **{len(am)} escolas** e usamos só elas para responder a **4 perguntas** sobre todas as escolas do Brasil. "
    "Os valores de comparação vêm de fontes públicas (Censo Escolar 2023 e Meta 6 do PNE)."
)
st.info(
    "**Como decidimos, em 3 passos**\n\n"
    "1. A amostra dá **um valor** (ex.: 32,7% das escolas).\n"
    "2. Comparamos com um **valor de referência** de fonte pública (ex.: meta de 50%).\n"
    "3. Perguntamos: a diferença é **grande demais para ser só acaso** do sorteio? "
    "Se sim, **rejeitamos H₀**: diferença comprovada. Se não, **não rejeitamos H₀**: não dá para afirmar que há diferença.\n\n"
    f"*“Grande demais” = p-valor < α = {fmt_dec(alpha, 2)}. H₀ é a hipótese de que nada mudou (a amostra é igual à referência).*",
    icon="💡",
)

st.header("As 4 respostas")
cols = st.columns(4)
for col, R in zip(cols, RES):
    h, r = R["h"], R["r"]
    with col.container(border=True):
        st.markdown(f"**{R['i']}. {h['curto']}**")
        st.markdown(f"### {fu(R, r.estimativa)}")
        st.caption(f"amostra · {h['rot_ref'].lower() if h['rot_ref'] != 'Meta do PNE' else 'meta do PNE'}: {fu(R, R['ref'])}")
        if r.rejeita:
            st.markdown(f"🔴 **{h['veredito']['sim']}**")
        else:
            st.markdown(f"⚪ **{h['veredito']['nao']}**")
st.caption("🔴 diferença comprovada pela amostra · ⚪ diferença não comprovada (pode ser só acaso). Detalhes de cada pergunta logo abaixo.")


# ---------------------------------------------------------------------------
# Uma seção por pergunta: resposta, gráfico simples, conferência
# ---------------------------------------------------------------------------
def pv_txt(r):
    """Ex.: 'p-valor = 0,329, maior ou igual a α = 0,05'."""
    p = "p-valor < 0,001" if r.p_valor < 0.001 else f"p-valor = {fmt_dec(r.p_valor, 3)}"
    return f"{p}, {'menor que' if r.rejeita else 'maior ou igual a'} α = {fmt_dec(alpha, 2)}"


for R in RES:
    h, r, i, prop = R["h"], R["r"], R["i"], R["prop"]
    param = "p" if prop else "μ"
    alt = h["alt"]
    est, lo, hi, ref_t, ver_t = (fu(R, v) for v in (r.estimativa, r.ic[0], r.ic[1], R["ref"], R["ver"]))

    st.divider()
    st.header(f"{i}. {h['pergunta']}")
    st.caption(f"Comparamos com: {h['ref_curta']}. Escolas na amostra usadas: {R['n']}"
               + (f" ({h['escopo']['nome']})." if h["escopo"] else "."))

    # Raciocínio em 3 blocos: valor da amostra, referência, comparação
    maior = r.estimativa > R["ref"]
    dif = abs(r.estimativa - R["ref"]) * R["esc"]
    dif_txt = f"{fmt_dec(dif, R['cas'])} p.p." if R["suf"] == "%" else f"{fmt_dec(dif, R['cas'])} matrículas"
    quais = " públicas" if h["escopo"] else ""
    como = (f"{R['x']} de {R['n']} escolas{quais} têm a característica ({R['x']} ÷ {R['n']})" if prop
            else f"média das {R['n']} escolas{quais} da amostra")
    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.caption("① O QUE A AMOSTRA DEU")
        st.markdown(f"## {est}")
        st.caption(f"Como obtivemos: {como}.")
    with c2.container(border=True):
        st.caption("② COM O QUE COMPARAMOS")
        st.markdown(f"## {ref_t}")
        st.caption(f"{h['ref_curta']}.")
    with c3.container(border=True):
        st.caption("③ COMPARAÇÃO")
        st.markdown(f"## {est} {'>' if maior else '<'} {ref_t}")
        st.caption(f"A amostra ficou {dif_txt} {'acima' if maior else 'abaixo'} da referência. "
                   f"Margem de erro da amostra: {lo} a {hi}.")

    # Decisão: por que rejeitamos ou não
    if r.rejeita:
        st.error(
            f"**Por isso, rejeitamos H₀.** A diferença de {dif_txt} é grande demais para ser só acaso do sorteio "
            f"({pv_txt(r)}).\n\n**Resposta: {h['sim']}**", icon="🔴")
    else:
        st.info(
            f"**Por isso, não rejeitamos H₀.** A diferença de {dif_txt} é pequena diante da margem de erro e pode ser só "
            f"acaso do sorteio ({pv_txt(r)}). Isso não prova que sejam iguais.\n\n**Resposta: {h['nao']}**", icon="⚪")
    st.markdown(
        f"**Conferindo com todas as escolas:** o valor real é **{ver_t}**, "
        f"{'**dentro**' if R['cobre'] else '**fora**'} da margem de erro"
        + (" ✅ a amostra acertou." if R["cobre"] else f" (esta amostra foi uma das ~{format(alpha, '.0%')} que erram).")
    )

    # Detalhes técnicos (recolhidos)
    with st.expander("Ver os cálculos desta pergunta (opcional)"):
        st.success(h["origem"], icon="✅")
        casas_ref = 3 if prop else 1
        st.number_input(
            f"Valor de comparação ({param}₀)", value=float(h["ref"]), key=f"ref{i}",
            min_value=0.01 if prop else None, max_value=0.99 if prop else None,
            step=0.005 if prop else 1.0, format="%.3f" if prop else "%.1f",
            help="Já vem preenchido com o valor da hipótese. Altere só para experimentar; a página é atualizada.",
        )
        st.latex(rf"H_0: {param} = {fmt_dec(R['ref'], casas_ref)} \qquad H_1: {param} {SIMB[alt]} {fmt_dec(R['ref'], casas_ref)}")
        st.caption(
            f"**H₀ (hipótese nula):** {'a proporção' if prop else 'a média'} em 2024 é igual ao valor de comparação: nada mudou.  \n"
            f"**H₁ (hipótese alternativa):** {'a proporção' if prop else 'a média'} em 2024 é {PALAVRA[alt]} "
            f"{fmt_dec(R['ref'], casas_ref)}."
        )
        c = st.columns(4)
        c[0].metric("Estimativa pontual", fmt_dec(r.estimativa, 4 if prop else 2))
        c[1].metric(f"IC {confianca:.0%}", f"[{fmt_dec(r.ic[0], 3 if prop else 1)} ; {fmt_dec(r.ic[1], 3 if prop else 1)}]")
        c[2].metric("Estatística (z)" if prop else "Estatística (t)", fmt_dec(r.estatistica, 3))
        c[3].metric("p-valor", f"{r.p_valor:.4g}")
        g1, g2 = st.columns([3, 2])
        with g1:
            st.altair_chart(grafico_distribuicao(r.estatistica, alt, prop, alpha, R["n"]), width="stretch")
        with g2:
            st.markdown(
                "**Como ler a curva:** se H₀ fosse verdadeira, a estatística cairia quase sempre perto de **0**. "
                "A linha azul é o valor que a amostra deu. A **área vermelha é o p-valor**: quanto menor, mais raro "
                "seria o resultado sob H₀. As linhas tracejadas marcam a partir de onde se rejeita H₀ com este α."
            )
        n_txt = (f"{R['n']} escolas {h['escopo']['nome'].replace('escolas ', '')} dentro das {len(am)} sorteadas"
                 if h["escopo"] else f"{R['n']} escolas na amostra")
        if prop:
            ep_ic = np.sqrt(r.estimativa * (1 - r.estimativa) / R["n"])
            st.markdown(
                f"**Passo a passo (ordem do cálculo):**\n"
                f"1. **n** = {n_txt}; **x** (dessas, as que têm a característica) = {R['x']}\n"
                f"2. **p̂** = x / n = {R['x']} / {R['n']} = **{fmt_dec(r.estimativa, 4)}**\n"
                f"3. **Erro-padrão do teste** (usa p₀ = {fmt_dec(R['ref'], 3)}): √(p₀(1−p₀)/n) = **{fmt_dec(r.erro_padrao_teste, 4)}**\n"
                f"4. **z** = (p̂ − p₀) / EP = ({fmt_dec(r.estimativa, 4)} − {fmt_dec(R['ref'], 3)}) / "
                f"{fmt_dec(r.erro_padrao_teste, 4)} = **{fmt_dec(r.estatistica, 3)}**\n"
                f"5. **p-valor** = área da cauda além de z = **{r.p_valor:.4g}** → comparado com α = {fmt_dec(alpha, 2)}\n"
                f"6. **IC**: p̂ ± z*·√(p̂(1−p̂)/n) = {fmt_dec(r.estimativa, 4)} ± z*·{fmt_dec(ep_ic, 4)} "
                f"→ [{fmt_dec(r.ic[0], 3)} ; {fmt_dec(r.ic[1], 3)}] (o IC usa p̂, o teste usa p₀)"
            )
        else:
            s = float(R["am_h"][h["var"]].std(ddof=1))
            st.markdown(
                f"**Passo a passo (ordem do cálculo):**\n"
                f"1. **n** = {n_txt}; **x̄** (média da amostra) = **{fmt_dec(r.estimativa, 2)}**; "
                f"**s** (desvio-padrão da amostra) = {fmt_dec(s, 2)}\n"
                f"2. **Erro-padrão** = s / √n = {fmt_dec(s, 2)} / √{R['n']} = **{fmt_dec(r.erro_padrao_teste, 2)}**\n"
                f"3. **t** = (x̄ − μ₀) / EP = ({fmt_dec(r.estimativa, 2)} − {fmt_dec(R['ref'], 1)}) / "
                f"{fmt_dec(r.erro_padrao_teste, 2)} = **{fmt_dec(r.estatistica, 3)}** (gl = n − 1 = {R['n'] - 1})\n"
                f"4. **p-valor** = área da cauda além de t = **{r.p_valor:.4g}** → comparado com α = {fmt_dec(alpha, 2)}\n"
                f"5. **IC**: x̄ ± t*·EP → [{fmt_dec(r.ic[0], 1)} ; {fmt_dec(r.ic[1], 1)}]"
            )
        st.markdown("**Condições de aplicação** (✅ = atendida)")
        for nome, (ok, det) in r.condicoes.items():
            st.markdown(f"- {'✅' if ok else '❌'} {nome} — {det}")

# ---------------------------------------------------------------------------
# Comparação população × amostra (simples)
# ---------------------------------------------------------------------------
st.divider()
st.header("A amostra acertou? Comparação com todas as escolas")
st.markdown(
    "Como temos os dados de **todas** as escolas, dá para conferir: o valor real ficou dentro da margem de erro da amostra? "
    "A pequena diferença entre os dois é o **erro amostral**: a variação natural de sortear 384 escolas em vez de olhar todas."
)
resumo = pd.DataFrame([{
    "Pergunta": f"{R['i']}. {R['h']['curto']}",
    "Valor real (todas as escolas)": fu(R, R["ver"]),
    "Amostra mostrou": fu(R, R["r"].estimativa),
    "Margem de erro": f"{fu(R, R['r'].ic[0])} a {fu(R, R['r'].ic[1])}",
    "Valor real dentro da margem?": "✅ sim" if R["cobre"] else "❌ não",
} for R in RES]).set_index("Pergunta")
st.dataframe(resumo, width="stretch")

with st.expander("📖 Guia dos símbolos e da ordem dos cálculos (opcional)"):
    st.markdown(
        "Antes dos cálculos, três coisas são **definidas por nós, sem olhar a amostra**: a pergunta (H₀ e H₁), o valor de "
        "comparação (p₀ ou μ₀) e o nível de significância (α). Só depois calculamos o que vem da amostra."
    )
    st.markdown(
        """
| Símbolo | O que é | De onde vem | Como usamos |
|---|---|---|---|
| **n** | Tamanho da amostra: quantas escolas estamos analisando | Contagem de linhas da amostra (nas perguntas 2, 3 e 4, só as escolas públicas) | Entra no erro-padrão: quanto maior o n, menor o erro-padrão e mais precisa a estimativa |
| **x** *(só proporção)* | Quantas escolas da amostra têm a característica | Soma da coluna de 0/1 na amostra | Numerador da proporção: p̂ = x / n |
| **p̂** *(p-chapéu)* | Proporção observada na amostra. É a **estimativa pontual** | Calculada: x / n | Melhor palpite para a proporção real; centro do IC; entra no z |
| **x̄** *(só média)* | Média observada na amostra. É a **estimativa pontual** | Calculada com os valores da amostra | Melhor palpite para a média real; centro do IC; entra no t |
| **s** *(só média)* | Desvio-padrão da amostra: o quanto as escolas variam entre si | Calculado com os valores da amostra | Entra no erro-padrão da média: EP = s / √n |
| **p₀ / μ₀** | **Valor de comparação** de H₀ | **Não vem da amostra.** Fonte externa (Censo 2023, meta do PNE) | Ponto de comparação: medimos a que distância a estimativa está dele |
| **α** | Nível de significância: a chance máxima que aceitamos de rejeitar H₀ quando ela é verdadeira | Escolhido por nós antes (barra lateral, 0,05) | Corte da decisão; define a confiança do IC: 1 − α |
| **EP** | Erro-padrão: o quanto a estimativa varia de uma amostra para outra | √(p₀(1−p₀)/n) para proporção; s/√n para média | A "régua" que mede distâncias |
| **z / t** | Estatística de teste: distância entre a estimativa e H₀, **em erros-padrão** | (estimativa − comparação) / EP | Quanto maior em valor absoluto, mais evidência contra H₀ |
| **gl** *(só média)* | Graus de liberdade = n − 1 | Calculado a partir do n | Define a forma da curva t |
| **p-valor** | Probabilidade de obter algo tão distante (ou mais) se H₀ fosse verdadeira | Área da cauda da curva normal (proporção) ou t (média) | Comparado com α para decidir |
| **z\\* / t\\*** | Valor crítico do IC (≈ 1,96 para 95%) | Tabela da normal ou t para a confiança 1 − α | Multiplica o EP para formar a margem de erro |
| **IC** | Intervalo de confiança: a **margem de erro** | Estimativa ± z\\*·EP (ou t\\*·EP) | Mostra a incerteza e permite comparar com H₀ e com a população |
| **p / μ** *(sem índice)* | Valor **verdadeiro** na população | Calculado com a população inteira | Usado só no fim, para conferir se a amostra acertou |
"""
    )
    aba_p, aba_m = st.tabs(["Ordem: teste para proporção (p)", "Ordem: teste para média (μ)"])
    with aba_p:
        st.markdown(
            """
1. **Conte e calcule a estimativa pontual:** conte n e x na amostra e calcule **p̂ = x / n**.
2. **Verifique as condições:** n·p₀ ≥ 10 e n·(1 − p₀) ≥ 10 (teste), o mesmo com p̂ (IC); amostra aleatória.
3. **Erro-padrão do teste**, usando p₀: **EP = √( p₀(1 − p₀) / n )**.
4. **Estatística de teste:** **z = (p̂ − p₀) / EP**.
5. **p-valor:** a área da cauda da curva normal além de z (≠ duas caudas, > cauda direita, < cauda esquerda).
6. **Decida:** **p-valor < α** → rejeite H₀; **p-valor ≥ α** → não rejeite H₀.
7. **IC** (usa p̂, e não p₀): **p̂ ± z\\* · √( p̂(1 − p̂) / n )**.
8. **Compare com a população:** o valor real **p** está dentro do IC?
"""
        )
    with aba_m:
        st.markdown(
            """
1. **Estimativa e variação:** calcule **x̄** e **s**, e conte **n**.
2. **Condições:** amostra aleatória, n ≥ 30 e, se a distribuição for muito assimétrica, n grande.
3. **Erro-padrão:** **EP = s / √n**.
4. **Estatística de teste:** **t = (x̄ − μ₀) / EP**, com **gl = n − 1**.
5. **p-valor:** a área da cauda da curva t além de t.
6. **Decida:** **p-valor < α** → rejeite H₀; **p-valor ≥ α** → não rejeite H₀.
7. **IC:** **x̄ ± t\\* · EP**.
8. **Compare com a população:** a média real **μ** está dentro do IC?
"""
        )
    st.info(
        "**Armadilhas comuns:** (1) no teste de proporção, o erro-padrão usa **p₀**, e o do IC usa **p̂**; "
        "(2) “não rejeitar H₀” **não prova** que H₀ é verdadeira; "
        "(3) o valor real da população **não** entra nos cálculos do teste, só na conferência final; "
        "(4) α deve ser escolhido **antes** de ver o p-valor."
    )

with st.expander("🎲 Simulação: e se sorteássemos outra amostra? (variabilidade amostral)"):
    st.markdown(
        f"Sorteando milhares de amostras do mesmo tamanho, em quantas a margem de erro de {confianca:.0%} contém o valor "
        "real? A teoria prevê perto de 95% (ideia do ch4B)."
    )
    reps = st.slider("Número de amostras simuladas", 200, 2000, 500, step=100)
    if st.button("Simular cobertura"):
        with st.spinner("Simulando..."):
            linhas = []
            for R in RES:
                serie = R["pop_h"][R["h"]["var"]]
                if R["prop"]:
                    cob = cobertura_ic_proporcao(serie, R["n"], serie.mean(), confianca, reps)
                else:
                    cob = cobertura_ic_media(serie, R["n"], serie.mean(), confianca, reps)
                linhas.append({"Pergunta": f"{R['i']}. {R['h']['curto']}", "Cobertura observada": cob})
        st.dataframe(pd.DataFrame(linhas).set_index("Pergunta").style.format("{:.1%}"), width="stretch")
    st.caption(
        "Por que não dá 95% exatos? São estimativas por simulação e a aproximação normal é imperfeita para variáveis "
        "assimétricas ou proporções próximas de 0 ou 1."
    )

st.subheader("Limitações")
st.markdown(
    "- **Acaso do sorteio:** outra amostra daria outros números; cerca de 5% das margens de erro de 95% não contêm o valor real.\n"
    "- **“Não dá para afirmar” não é “é igual”:** com 384 escolas, diferenças pequenas podem passar despercebidas.\n"
    "- **Perguntas 2, 3 e 4** usam só as escolas públicas da amostra (cerca de 280), então têm menos precisão.\n"
    "- **Variáveis assimétricas:** matrículas têm poucas escolas enormes e o % de tempo integral é polarizado (muitas escolas com 0% e muitas com 100%).\n"
    "- **Valores de comparação:** vêm do Censo 2023 e da Meta 6 do PNE; o indicador oficial de tempo integral tem pequenas diferenças de cálculo em relação ao nosso, e o dado de internet vem de reportagem sobre o MEC.\n"
    "- A população é o conjunto de escolas em atividade com dados completos."
)
