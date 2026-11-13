"""Visuais didáticos do Painel 3: curva de H0 com o p-valor e IC × H0 × população."""
import altair as alt
import numpy as np
import pandas as pd
from scipy import stats

AZUL, VERMELHO, VERDE, CINZA = "#1f77b4", "#d62728", "#2ca02c", "#7f7f7f"


def grafico_distribuicao(estat: float, alt_h: str, prop: bool, alpha: float, n: int) -> alt.Chart:
    """Curva da estatística sob H0 (normal ou t): área vermelha = p-valor, linha azul = valor observado."""
    dist = stats.norm if prop else stats.t(df=n - 1)
    nome = "z" if prop else "t"
    lim = max(4.0, abs(estat) + 1.0)
    xs = np.linspace(-lim, lim, 700)
    base = pd.DataFrame({"x": xs, "densidade": dist.pdf(xs)})

    if alt_h == "greater":
        regiao = xs >= estat
        crit = [dist.ppf(1 - alpha)]
    elif alt_h == "less":
        regiao = xs <= estat
        crit = [dist.ppf(alpha)]
    else:
        regiao = np.abs(xs) >= abs(estat)
        c = dist.ppf(1 - alpha / 2)
        crit = [-c, c]
    area = base[regiao].copy()
    area["trecho"] = (area["x"] > 0).astype(int)  # separa as duas caudas no teste bilateral

    eixo_x = alt.X("x:Q", title=f"{nome} (erros-padrão a partir de H₀)", scale=alt.Scale(domain=[-lim, lim]))
    curva = alt.Chart(base).mark_area(color=CINZA, opacity=0.18, line={"color": CINZA}).encode(
        eixo_x, alt.Y("densidade:Q", axis=None))
    cauda = alt.Chart(area).mark_area(color=VERMELHO, opacity=0.55).encode(
        eixo_x, alt.Y("densidade:Q"), detail="trecho:N")
    regra_crit = alt.Chart(pd.DataFrame({"x": crit})).mark_rule(color=CINZA, strokeDash=[5, 4]).encode(x="x:Q")
    regra_obs = alt.Chart(pd.DataFrame({"x": [estat], "rotulo": [f"{nome} observado = {estat:.2f}"]})).mark_rule(
        color=AZUL, strokeWidth=3).encode(x="x:Q")
    texto = alt.Chart(pd.DataFrame({"x": [estat], "y": [float(dist.pdf(0))], "rotulo": [f"{nome} = {estat:.2f}"]})).mark_text(
        color=AZUL, dy=-8, fontWeight="bold", align="center").encode(x="x:Q", y=alt.Y("y:Q"), text="rotulo:N")
    return (curva + cauda + regra_crit + regra_obs + texto).properties(
        height=230, title=f"Se H₀ fosse verdadeira, a estatística {nome} cairia nesta curva")
