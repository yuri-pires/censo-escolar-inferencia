# Censo Escolar 2024 — População × Amostra

Trabalho final de estatística: inferência a partir de uma amostra aleatória simples (AAS) das escolas
brasileiras de educação básica, com 3 painéis em Streamlit.

| Item | Link |
|---|---|
| Dashboard online | _(preencher após publicar no Streamlit Cloud)_ |
| Vídeo de apresentação | _(preencher após subir no YouTube)_ |
| Dados originais (INEP) | [Microdados do Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) |

## O que o painel mostra

1. **Página inicial** — base de dados, população, parâmetros do cálculo amostral e variáveis.
2. **Painel 1 · População** — estatística descritiva das 178.997 escolas.
3. **Painel 2 · Amostra** — estatística descritiva das 384 escolas sorteadas e comparação com a população.
4. **Painel 3 · Inferência** — intervalos de confiança e testes de hipóteses (2 de média e 2 de proporção),
   com valores de referência reais (Censo 2023 e Meta 6 do PNE) e conferência com a população.

## Metodologia

- **População:** escolas em atividade (`TP_SITUACAO_FUNCIONAMENTO == 1`) com matrículas, docentes e turmas
  informados — N = 178.997.
- **Tamanho da amostra:** n₀ = z²·p(1−p)/e², com correção para população finita.
  Confiança 95%, erro 5%, p = 0,5 ⇒ **n = 384** (função `tamanho_amostra` em `preparar_amostra.py`).
- **Sorteio:** AAS sem reposição, semente fixa `20241` (reproduzível).
- **Variáveis derivadas:** `PCT_INTEGRAL` (% de matrículas em tempo integral) e `IN_TEMPO_INTEGRAL`
  (escola com ≥ 25% das matrículas em tempo integral).

## Como rodar

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Os arquivos `dados/populacao.csv`, `dados/amostra.csv` e `dados/metadados.json` já estão no repositório,
então **não é preciso baixar nada** para rodar o painel.

### Regenerar a população e a amostra (opcional)

Baixe os microdados do Censo Escolar 2024 no site do INEP (link acima), extraia o CSV e rode:

```bash
python preparar_amostra.py --csv caminho/para/microdados_ed_basica_2024.csv
```

O CSV bruto (~200 MB) é ignorado pelo git.

## Estrutura

```
app.py                  # página inicial
pages/
  1_Populacao.py        # painel 1
  2_Amostra.py          # painel 2
  3_Inferencia.py       # painel 3 (hipóteses, ICs, testes, comparação)
descritiva.py           # painel_descritivo(), reutilizado nos painéis 1 e 2
inferencia.py           # IC e testes (z para proporção, t para média) + simulação de cobertura
visual.py               # gráfico da curva sob H0 com a área do p-valor
dados.py                # constantes e carregamento dos dados
preparar_amostra.py     # filtra a população, calcula n e sorteia a AAS
dados/                  # populacao.csv, amostra.csv, metadados.json
```

## Limitações

- O valor de referência de 88,5% de escolas públicas com internet vem de uma reportagem sobre o Censo 2023;
  a definição exata de "internet" no documento oficial não foi confirmada.
- O limite de 25% de matrículas em tempo integral é uma aproximação, por escola, da meta nacional do PNE.
- Não rejeitar H₀ não prova que H₀ seja verdadeira.
