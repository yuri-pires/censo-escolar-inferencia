import streamlit as st

from dados import FONTE, LINK_FONTE, QUALITATIVAS, QUANTITATIVAS, carregar_metadados, checar_dados, fmt_dec, fmt_milhar

st.set_page_config(page_title="Censo Escolar 2024 — Inferência", page_icon="🏫", layout="wide")
checar_dados()
meta = carregar_metadados()

st.title("🏫 Censo Escolar 2024 — População × Amostra")
st.markdown(
    "Trabalho final de estatística: amostragem, intervalos de confiança e testes de hipóteses "
    "aplicados às escolas brasileiras. Use o menu lateral para navegar pelos **três painéis**."
)

st.header("1. Base de dados")
st.markdown(
    f"- **Fonte:** {FONTE} — [link de acesso]({LINK_FONTE})\n"
    "- **Contexto:** levantamento anual e obrigatório do INEP sobre as escolas de educação básica do país "
    "(infraestrutura, matrículas, docentes e turmas), usado no planejamento e na avaliação de políticas educacionais.\n"
    f"- **Arquivo original:** {fmt_milhar(meta['n_linhas_arquivo_original'])} observações e {meta['n_colunas_arquivo_original']} variáveis.\n"
    f"- **População de interesse:** escolas em atividade em 2024 com matrículas, docentes e turmas informados "
    f"(**N = {fmt_milhar(meta['N_populacao'])}**). Filtro: `{meta['filtro']}`.\n"
    "- **Unidade amostral:** a escola."
)
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Variáveis qualitativas (1 = sim)**")
    st.table({"Variável": list(QUALITATIVAS), "Descrição": list(QUALITATIVAS.values())})
with c2:
    st.markdown("**Variáveis quantitativas**")
    st.table({"Variável": list(QUANTITATIVAS), "Descrição": list(QUANTITATIVAS.values())})
st.caption(
    "Variáveis derivadas: `PCT_INTEGRAL` = matrículas em tempo integral (infantil + fundamental + médio) ÷ `QT_MAT_BAS` × 100; "
    "`IN_TEMPO_INTEGRAL` = 1 quando `PCT_INTEGRAL` ≥ 25%, o mesmo critério usado para classificar uma escola como de tempo "
    "integral na Meta 6 do PNE."
)
st.caption("Também usadas para segmentação: NO_REGIAO, SG_UF, dependência administrativa e localização (urbana/rural).")

st.header("2. Dimensionamento e seleção da amostra")
st.markdown(
    f"- **Confiança:** {meta['confianca']:.0%} (padrão em estudos descritivos; z ≈ 1,96).\n"
    f"- **Margem de erro:** {meta['margem_erro']:.0%} (compromisso entre precisão e custo).\n"
    f"- **Proporção no dimensionamento:** p = {meta['p_dimensionamento']} — caso mais conservador, pois maximiza p(1−p) "
    "e garante a margem para qualquer proporção.\n"
    f"- **Fórmula:** n₀ = z²·p(1−p)/e²; com correção para população finita n = n₀ / (1 + (n₀−1)/N).\n"
    f"- **Resultado: n = {fmt_milhar(meta['n_amostra'])} escolas** (conferir na calculadora da USP/Bauru).\n"
    f"- **Seleção:** amostra aleatória simples sem reposição (`DataFrame.sample`, semente `{meta['seed']}`), "
    "de modo que toda escola tem probabilidade n/N de ser sorteada. O procedimento está em `preparar_amostra.py`."
)
