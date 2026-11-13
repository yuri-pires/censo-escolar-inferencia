"""Painel descritivo reutilizado para população (painel 1) e amostra (painel 2)."""
import altair as alt
import pandas as pd
import streamlit as st

from dados import CATEGORICAS, QUALITATIVAS, QUANTITATIVAS, fmt_dec, fmt_milhar


def tabela_quantitativas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = {}
    for col, rotulo in QUANTITATIVAS.items():
        s = df[col]
        linhas[rotulo] = {
            "N": len(s), "Média": s.mean(), "Mediana": s.median(), "Desvio-padrão": s.std(),
            "Mínimo": s.min(), "Q1": s.quantile(0.25), "Q3": s.quantile(0.75),
            "Máximo": s.max(), "Assimetria": s.skew(),
        }
    return pd.DataFrame(linhas).T


def tabela_proporcoes(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        rotulo: {"Sim (n)": int(df[col].sum()), "Proporção": df[col].mean()}
        for col, rotulo in QUALITATIVAS.items()
    }).T


def painel_descritivo(df: pd.DataFrame, titulo: str, chave: str, base: str = "população") -> None:
    """Renderiza o painel completo. `chave` evita colisão de widgets entre painéis.
    `base` ("população" ou "amostra") só ajusta os textos explicativos."""
    st.header(titulo)
    st.markdown(
        f"Este painel descreve **apenas os dados da {base}**: cada linha é uma escola. "
        "A ordem é: (1) indicadores-resumo, (2) variáveis numéricas (tamanho das escolas), "
        "(3) variáveis de sim/não (infraestrutura) e (4) distribuição por categorias. "
        "Os filtros abaixo restringem tudo o que aparece nesta página."
    )

    # --- Filtros interativos (afetam só a visualização do painel) ---
    c1, c2 = st.columns(2)
    regioes = c1.multiselect("Região", sorted(df["NO_REGIAO"].unique()), default=sorted(df["NO_REGIAO"].unique()), key=f"reg_{chave}")
    deps = c2.multiselect("Dependência", sorted(df["DEPENDENCIA"].unique()), default=sorted(df["DEPENDENCIA"].unique()), key=f"dep_{chave}")
    d = df[df["NO_REGIAO"].isin(regioes) & df["DEPENDENCIA"].isin(deps)]
    if d.empty:
        st.warning("Nenhum registro para os filtros escolhidos.")
        return

    # --- Indicadores ---
    st.caption(f"Escolas consideradas após os filtros: {fmt_milhar(len(d))} de {fmt_milhar(len(df))}.")
    k = st.columns(4)
    k[0].metric("Escolas", fmt_milhar(len(d)))
    k[1].metric("Média de matrículas", fmt_dec(d["QT_MAT_BAS"].mean(), 1))
    k[2].metric("Mediana de matrículas", fmt_dec(d["QT_MAT_BAS"].median(), 0))
    k[3].metric("% com biblioteca", f"{fmt_dec(d['IN_BIBLIOTECA'].mean() * 100, 1)}%")

    # --- Quantitativas ---
    st.subheader("Variáveis quantitativas")
    st.markdown(
        "A tabela resume o **tamanho** das escolas. **Média** e **mediana** indicam o valor típico; "
        "o **desvio-padrão** mede o quanto as escolas variam em torno da média; **Q1/Q3** delimitam os 50% centrais. "
        "A **assimetria** positiva indica cauda longa à direita: poucas escolas muito grandes puxam a média para "
        "cima da mediana. Isso importa para a inferência (ver Painel 3)."
    )
    st.dataframe(tabela_quantitativas(d).style.format(precision=2), width="stretch")

    st.markdown(
        "**Como ler os gráficos:** o histograma mostra quantas escolas há em cada faixa de valores; "
        "o boxplot abaixo resume mediana (linha central), quartis (caixa) e valores extremos (pontos)."
    )
    var = st.selectbox("Variável para o gráfico", list(QUANTITATIVAS), format_func=QUANTITATIVAS.get, key=f"var_{chave}")
    corte = d[var].quantile(0.99)
    dv = d[d[var] <= corte]
    hist = (alt.Chart(dv).mark_bar().encode(
        alt.X(f"{var}:Q", bin=alt.Bin(maxbins=40), title=QUANTITATIVAS[var]),
        alt.Y("count()", title="Escolas"),
    ).properties(height=260))
    box = (alt.Chart(dv).mark_boxplot(extent="min-max").encode(
        alt.X(f"{var}:Q", title=QUANTITATIVAS[var]),
    ).properties(height=90))
    st.altair_chart(hist & box, width="stretch")
    st.caption(f"Gráficos limitados ao percentil 99 ({fmt_dec(corte, 0)}) para legibilidade; as medidas da tabela usam todos os dados.")

    # --- Qualitativas ---
    st.subheader("Variáveis qualitativas")
    st.markdown(
        "Cada característica é um **sim/não** por escola. A coluna *Proporção* é a fração de escolas que "
        "**têm** a característica (frequência de “sim” ÷ total). É esse tipo de variável que usamos para "
        "estimar e testar **proporções** no Painel 3."
    )
    prop = tabela_proporcoes(d)
    st.dataframe(prop.style.format({"Proporção": "{:.1%}", "Sim (n)": "{:,.0f}"}), width="stretch")
    graf = prop.reset_index().rename(columns={"index": "Característica"})
    barras = alt.Chart(graf).mark_bar().encode(
        alt.X("Proporção:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        alt.Y("Característica:N", sort="-x", title=None),
        tooltip=["Característica", alt.Tooltip("Proporção:Q", format=".1%")],
    ).properties(height=220)
    st.altair_chart(barras, width="stretch")

    st.markdown(
        "**Distribuição por categoria:** quantas escolas (e que fração do total) pertencem a cada grupo, "
        "para entender a composição da base."
    )
    cat = st.selectbox("Distribuição categórica", list(CATEGORICAS), format_func=CATEGORICAS.get, key=f"cat_{chave}")
    freq = d[cat].value_counts().rename_axis(CATEGORICAS[cat]).reset_index(name="Escolas")
    freq["Proporção"] = freq["Escolas"] / freq["Escolas"].sum()
    col_t, col_g = st.columns([1, 1])
    col_t.dataframe(freq.style.format({"Proporção": "{:.1%}", "Escolas": "{:,.0f}"}), hide_index=True, width="stretch")
    col_g.altair_chart(
        alt.Chart(freq).mark_bar().encode(x=alt.X(f"{CATEGORICAS[cat]}:N", sort="-y", title=None), y="Escolas:Q").properties(height=220),
        width="stretch",
    )
