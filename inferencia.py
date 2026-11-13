"""Funções puras de inferência (sem Streamlit), testáveis isoladamente."""
from dataclasses import dataclass

import numpy as np
from scipy import stats

ALTERNATIVAS = {"two-sided": "≠", "greater": ">", "less": "<"}


@dataclass
class Resultado:
    estimativa: float
    ic: tuple
    estatistica: float
    p_valor: float
    rejeita: bool
    condicoes: dict  # nome da condição -> (ok, detalhe)
    n: int
    erro_padrao_teste: float


def _p_valor(estat: float, dist, alternativa: str) -> float:
    if alternativa == "greater":
        return float(dist.sf(estat))
    if alternativa == "less":
        return float(dist.cdf(estat))
    return float(2 * dist.sf(abs(estat)))


def teste_proporcao(x: int, n: int, p0: float, alternativa: str = "two-sided",
                    alpha: float = 0.05, confianca: float = 0.95, N: int | None = None) -> Resultado:
    """IC (Wald, usa p̂) + teste z (usa p0 no erro-padrão), como no ch5B."""
    p_hat = x / n
    z_crit = stats.norm.ppf(1 - (1 - confianca) / 2)
    ep_ic = np.sqrt(p_hat * (1 - p_hat) / n)
    ic = (p_hat - z_crit * ep_ic, p_hat + z_crit * ep_ic)

    ep0 = np.sqrt(p0 * (1 - p0) / n)
    z = (p_hat - p0) / ep0
    p = _p_valor(z, stats.norm, alternativa)
    cond = {
        "Independência (AAS)": (True if N is None else n < 0.10 * N, "n < 10% de N" if N else "AAS"),
        "Sucesso/falha (IC): n·p̂ ≥ 10 e n·(1−p̂) ≥ 10": (n * p_hat >= 10 and n * (1 - p_hat) >= 10,
                                                      f"{n*p_hat:.0f} e {n*(1-p_hat):.0f}"),
        "Sucesso/falha (teste): n·p₀ ≥ 10 e n·(1−p₀) ≥ 10": (n * p0 >= 10 and n * (1 - p0) >= 10,
                                                          f"{n*p0:.0f} e {n*(1-p0):.0f}"),
    }
    return Resultado(p_hat, ic, float(z), p, p < alpha, cond, n, float(ep0))


def teste_media(dados, mu0: float, alternativa: str = "two-sided",
                alpha: float = 0.05, confianca: float = 0.95, N: int | None = None) -> Resultado:
    """IC e teste t de uma amostra (gl = n−1), como no ch5A."""
    x = np.asarray(dados, dtype=float)
    n = len(x)
    xbar, s = x.mean(), x.std(ddof=1)
    ep = s / np.sqrt(n)
    t_crit = stats.t.ppf(1 - (1 - confianca) / 2, df=n - 1)
    ic = (xbar - t_crit * ep, xbar + t_crit * ep)
    t = (xbar - mu0) / ep
    p = _p_valor(t, stats.t(df=n - 1), alternativa)
    assim = float(stats.skew(x))
    cond = {
        "Independência (AAS)": (True if N is None else n < 0.10 * N, "n < 10% de N" if N else "AAS"),
        "Tamanho da amostra (n ≥ 30)": (n >= 30, f"n = {n}"),
        "Assimetria moderada (|assimetria| < 2) ou n grande": (abs(assim) < 2 or n >= 100,
                                                              f"assimetria = {assim:.2f}"),
    }
    return Resultado(float(xbar), ic, float(t), p, p < alpha, cond, n, float(ep))


def cobertura_ic_proporcao(pop_serie, n: int, p_verdadeiro: float, confianca: float = 0.95,
                           reps: int = 1000, seed: int = 0) -> float:
    """Fração de IC (Wald) de reps amostras AAS que contém a proporção populacional."""
    rng = np.random.default_rng(seed)
    v = pop_serie.to_numpy()
    z = stats.norm.ppf(1 - (1 - confianca) / 2)
    acertos = 0
    for _ in range(reps):
        p_hat = rng.choice(v, size=n, replace=False).mean()
        ep = np.sqrt(p_hat * (1 - p_hat) / n)
        acertos += (p_hat - z * ep) <= p_verdadeiro <= (p_hat + z * ep)
    return acertos / reps


def cobertura_ic_media(pop_serie, n: int, mu_verdadeiro: float, confianca: float = 0.95,
                       reps: int = 1000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    v = pop_serie.to_numpy(dtype=float)
    t_crit = stats.t.ppf(1 - (1 - confianca) / 2, df=n - 1)
    acertos = 0
    for _ in range(reps):
        a = rng.choice(v, size=n, replace=False)
        m, ep = a.mean(), a.std(ddof=1) / np.sqrt(n)
        acertos += (m - t_crit * ep) <= mu_verdadeiro <= (m + t_crit * ep)
    return acertos / reps
