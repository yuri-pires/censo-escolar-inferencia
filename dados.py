"""Constantes e carregamento compartilhados pelo app."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DIR = Path(__file__).parent
POP_CSV = DIR / "dados" / "populacao.csv"
AMOSTRA_CSV = DIR / "dados" / "amostra.csv"
META_JSON = DIR / "dados" / "metadados.json"

FONTE = "INEP — Microdados do Censo Escolar da Educação Básica 2024"
LINK_FONTE = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar"

# Variáveis binárias (1 = sim) usadas nas análises de proporção
QUALITATIVAS = {
    "IN_BIBLIOTECA": "Possui biblioteca",
    "IN_INTERNET": "Possui internet",
    "IN_LABORATORIO_INFORMATICA": "Possui laboratório de informática",
    "IN_QUADRA_ESPORTES": "Possui quadra de esportes",
    "IN_ACESSIBILIDADE_RAMPAS": "Possui rampas de acessibilidade",
    "IN_ALIMENTACAO": "Oferece alimentação",
    "IN_TEMPO_INTEGRAL": "Escola de tempo integral (≥ 25% das matrículas)",
}
# Variáveis categóricas para segmentação
CATEGORICAS = {
    "DEPENDENCIA": "Dependência administrativa",
    "LOCALIZACAO": "Localização",
    "NO_REGIAO": "Região",
}
QUANTITATIVAS = {
    "QT_MAT_BAS": "Matrículas na educação básica",
    "QT_DOC_BAS": "Docentes na educação básica",
    "QT_TUR_BAS": "Turmas na educação básica",
    "PCT_INTEGRAL": "% de matrículas em tempo integral",
}

DEPENDENCIA = {1: "Federal", 2: "Estadual", 3: "Municipal", 4: "Privada"}
LOCALIZACAO = {1: "Urbana", 2: "Rural"}


@st.cache_data
def carregar_populacao() -> pd.DataFrame:
    return pd.read_csv(POP_CSV)


@st.cache_data
def carregar_amostra() -> pd.DataFrame:
    return pd.read_csv(AMOSTRA_CSV)


@st.cache_data
def carregar_metadados() -> dict:
    return json.loads(META_JSON.read_text(encoding="utf-8"))


def checar_dados() -> bool:
    """Mostra instrução amigável se os arquivos ainda não foram gerados."""
    if POP_CSV.exists() and AMOSTRA_CSV.exists() and META_JSON.exists():
        return True
    st.error("Arquivos de dados não encontrados. Rode `python preparar_amostra.py` primeiro.")
    st.stop()


def fmt_milhar(n) -> str:
    """55702 -> '55.702' (padrão pt-BR)."""
    return f"{n:,.0f}".replace(",", ".")


def fmt_dec(x, casas=2) -> str:
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
