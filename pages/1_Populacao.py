import streamlit as st

from dados import carregar_populacao, checar_dados
from descritiva import painel_descritivo

st.set_page_config(page_title="Painel 1 — População", page_icon="🏫", layout="wide")
checar_dados()
st.info(
    "**Objetivo:** conhecer a população completa (todas as escolas em atividade com dados completos). "
    "Os valores aqui são os **parâmetros verdadeiros** (μ, p): no Painel 3 eles servem de gabarito para "
    "avaliar o que a amostra consegue estimar."
)
painel_descritivo(carregar_populacao(), "Painel 1 — Análise descritiva da população", "pop", base="população")
