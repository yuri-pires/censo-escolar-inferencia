"""Prepara a população, dimensiona n e seleciona a AAS.

Uso:
    python preparar_amostra.py --csv ../microdados_censo_escolar_2024_defeso/dados/microdados_ed_basica_2024.csv

Gera em dados/: populacao.csv, amostra.csv e metadados.json (parâmetros e procedimento).
"""
import argparse
import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import norm

SEED = 20241  # semente fixa: a amostra é reproduzível
CONFIANCA = 0.95
MARGEM_ERRO = 0.05
P_DIMENSIONAMENTO = 0.5  # caso mais conservador: maximiza p(1-p)

COLUNAS = [
    "CO_ENTIDADE", "SG_UF", "NO_REGIAO", "TP_DEPENDENCIA", "TP_LOCALIZACAO",
    "IN_BIBLIOTECA", "IN_INTERNET", "IN_LABORATORIO_INFORMATICA", "IN_QUADRA_ESPORTES",
    "IN_ACESSIBILIDADE_RAMPAS", "IN_ALIMENTACAO",
    "QT_MAT_BAS", "QT_DOC_BAS", "QT_TUR_BAS",
    "QT_MAT_INF_INT", "QT_MAT_FUND_INT", "QT_MAT_MED_INT",  # matrículas em tempo integral por etapa
]
COLS_INTEGRAL = ["QT_MAT_INF_INT", "QT_MAT_FUND_INT", "QT_MAT_MED_INT"]
LIMIAR_INTEGRAL = 25.0  # % mínimo de matrículas em tempo integral para a escola ser "de tempo integral" (PNE, Meta 6)
DEPENDENCIA = {1: "Federal", 2: "Estadual", 3: "Municipal", 4: "Privada"}
LOCALIZACAO = {1: "Urbana", 2: "Rural"}


def tamanho_amostra(N: int, confianca: float, e: float, p: float) -> int:
    """n0 = z² p(1-p) / e²; correção para população finita: n = n0 / (1 + (n0-1)/N)."""
    z = norm.ppf(1 - (1 - confianca) / 2)
    n0 = z**2 * p * (1 - p) / e**2
    return math.ceil(n0 / (1 + (n0 - 1) / N))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="caminho do microdados_ed_basica_2024.csv")
    args = ap.parse_args()
    saida = Path(__file__).parent / "dados"
    saida.mkdir(exist_ok=True)

    bruto = pd.read_csv(args.csv, sep=";", encoding="latin-1", usecols=COLUNAS + ["TP_SITUACAO_FUNCIONAMENTO"], low_memory=False)
    n_bruto, n_colunas_orig = len(bruto), len(pd.read_csv(args.csv, sep=";", encoding="latin-1", nrows=0).columns)

    # População: escolas em atividade (situação 1) com matrículas e docentes informados
    pop = bruto[bruto["TP_SITUACAO_FUNCIONAMENTO"] == 1].drop(columns="TP_SITUACAO_FUNCIONAMENTO")
    pop = pop.dropna(subset=["QT_MAT_BAS", "QT_DOC_BAS", "QT_TUR_BAS"]).reset_index(drop=True)
    # Tempo integral: soma das etapas (vazio = 0) e participação sobre as matrículas da escola
    pop["QT_MAT_INTEGRAL"] = pop[COLS_INTEGRAL].fillna(0).sum(axis=1)
    pop["PCT_INTEGRAL"] = (pop["QT_MAT_INTEGRAL"] / pop["QT_MAT_BAS"].where(pop["QT_MAT_BAS"] > 0) * 100).round(4)
    pop["IN_TEMPO_INTEGRAL"] = (pop["PCT_INTEGRAL"] >= LIMIAR_INTEGRAL).astype(int)
    pop = pop.drop(columns=COLS_INTEGRAL + ["QT_MAT_INTEGRAL"])
    pop["DEPENDENCIA"] = pop["TP_DEPENDENCIA"].map(DEPENDENCIA)
    pop["LOCALIZACAO"] = pop["TP_LOCALIZACAO"].map(LOCALIZACAO)
    pop = pop.drop(columns=["TP_DEPENDENCIA", "TP_LOCALIZACAO"])
    N = len(pop)

    n = tamanho_amostra(N, CONFIANCA, MARGEM_ERRO, P_DIMENSIONAMENTO)
    # AAS sem reposição: cada escola tem a mesma probabilidade n/N de entrar
    amostra = pop.sample(n=n, replace=False, random_state=SEED)

    pop.to_csv(saida / "populacao.csv", index=False)
    amostra.to_csv(saida / "amostra.csv", index=False)
    meta = {
        "fonte": "INEP — Microdados do Censo Escolar da Educação Básica 2024",
        "n_linhas_arquivo_original": n_bruto,
        "n_colunas_arquivo_original": n_colunas_orig,
        "N_populacao": N,
        "n_amostra": n,
        "confianca": CONFIANCA,
        "margem_erro": MARGEM_ERRO,
        "p_dimensionamento": P_DIMENSIONAMENTO,
        "seed": SEED,
        "filtro": "TP_SITUACAO_FUNCIONAMENTO == 1 e QT_MAT_BAS, QT_DOC_BAS, QT_TUR_BAS preenchidos",
    }
    (saida / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"População N={N} | amostra n={n} (seed={SEED}) | arquivos em {saida}")


if __name__ == "__main__":
    main()
