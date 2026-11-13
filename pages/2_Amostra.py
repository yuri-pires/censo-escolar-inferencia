import pandas as pd
import streamlit as st

from dados import QUALITATIVAS, QUANTITATIVAS, carregar_amostra, carregar_populacao, checar_dados
from descritiva import painel_descritivo

st.set_page_config(page_title="Painel 2 — Amostra", page_icon="🏫", layout="wide")
checar_dados()
pop, am = carregar_populacao(), carregar_amostra()

st.info(
    "**Objetivo:** descrever a amostra aleatória simples sorteada, com as mesmas medidas e gráficos do Painel 1. "
    "Na prática só teríamos estes dados; aqui podemos checar o quanto a amostra reproduz a população."
)
painel_descritivo(am, "Painel 2 — Análise descritiva da amostra", "am", base="amostra")

st.divider()
st.header("População × amostra")
st.markdown(
    "A tabela lista, para cada medida, o valor na **população** (parâmetro), o valor na **amostra** (estatística) "
    "e a **diferença** entre eles. Em uma AAS as diferenças vêm só do acaso (**erro amostral**); não há viés de seleção. "
    "Espere diferenças pequenas nas médias e proporções, e maiores no desvio-padrão das variáveis assimétricas, "
    "porque poucas escolas muito grandes podem ou não ter caído na amostra."
)
linhas = []
for col, rot in QUANTITATIVAS.items():
    linhas.append({"Medida": f"Média — {rot}", "População": pop[col].mean(), "Amostra": am[col].mean()})
    linhas.append({"Medida": f"Mediana — {rot}", "População": pop[col].median(), "Amostra": am[col].median()})
    linhas.append({"Medida": f"Desvio-padrão — {rot}", "População": pop[col].std(), "Amostra": am[col].std()})
for col, rot in QUALITATIVAS.items():
    linhas.append({"Medida": f"Proporção — {rot}", "População": pop[col].mean(), "Amostra": am[col].mean()})
comp = pd.DataFrame(linhas).set_index("Medida")
comp["Diferença"] = comp["Amostra"] - comp["População"]
st.dataframe(comp.style.format(precision=3), width="stretch")
st.caption("Diferenças pequenas refletem variabilidade amostral esperada de uma AAS; outra semente daria valores diferentes.")
