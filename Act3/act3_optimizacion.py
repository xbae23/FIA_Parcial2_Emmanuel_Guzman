"""Minimización reproducible de Rastrigin en dos dimensiones."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
OUT = BASE / "resultados"
LIMITE = 5.12


def objetivo(x: tuple[float, float]) -> float:
    """Rastrigin: f(x,y)=20+x²+y²-10(cos(2πx)+cos(2πy)); mínimo 0."""
    return 20 + sum(v * v - 10 * math.cos(2 * math.pi * v) for v in x)


def limitar(x: tuple[float, float]) -> tuple[float, float]:
    return tuple(max(-LIMITE, min(LIMITE, v)) for v in x)


def hill_climbing(inicio: tuple[float, float], paso: float = 0.1,
                  max_iter: int = 500) -> tuple[tuple[float, float], list[float]]:
    """Descenso de mejor vecino en malla; termina al no mejorar."""
    actual = limitar(inicio)
    historial = [objetivo(actual)]
    for _ in range(max_iter):
        vecinos = [limitar((actual[0] + dx, actual[1] + dy))
                   for dx, dy in ((paso, 0), (-paso, 0), (0, paso), (0, -paso))]
        mejor = min(vecinos, key=objetivo)
        if objetivo(mejor) >= objetivo(actual) - 1e-12:
            break
        actual = mejor
        historial.append(objetivo(actual))
    return actual, historial


def simulated_annealing(inicio: tuple[float, float], semilla: int,
                        t0: float = 10.0, enfriamiento: float = 0.995,
                        iteraciones: int = 2000, sigma: float = 0.25
                        ) -> tuple[tuple[float, float], list[float]]:
    """Acepta empeoramientos con probabilidad exp(-delta/T); conserva el mejor."""
    rng = random.Random(semilla)
    actual = limitar(inicio)
    mejor = actual
    historial = [objetivo(mejor)]
    for i in range(iteraciones):
        temperatura = t0 * enfriamiento ** i
        candidato = limitar((actual[0] + rng.gauss(0, sigma),
                             actual[1] + rng.gauss(0, sigma)))
        delta = objetivo(candidato) - objetivo(actual)
        if delta <= 0 or rng.random() < math.exp(-delta / temperatura):
            actual = candidato
        if objetivo(actual) < objetivo(mejor):
            mejor = actual
        historial.append(objetivo(mejor))
    return mejor, historial


def ejecutar() -> dict:
    OUT.mkdir(exist_ok=True)
    inicio = (3.8, 3.8)
    hc_x, hc_hist = hill_climbing(inicio)
    sa_x, sa_hist = simulated_annealing(inicio, semilla=42)
    semillas = range(30)
    valores_hc = []
    valores_sa = []
    for semilla in semillas:
        rng = random.Random(semilla)
        punto = (rng.uniform(-LIMITE, LIMITE), rng.uniform(-LIMITE, LIMITE))
        valores_hc.append(objetivo(hill_climbing(punto)[0]))
        valores_sa.append(objetivo(simulated_annealing(punto, semilla)[0]))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(range(len(hc_hist)), hc_hist, label="Hill Climbing: mejor valor", linewidth=2)
    ax.plot(range(len(sa_hist)), sa_hist, label="Simulated Annealing: mejor valor", linewidth=2)
    ax.set(xlabel="Iteracion", ylabel="f(x, y) (menor es mejor)", title="Convergencia desde (3.8, 3.8)")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "act3_convergencia.png", dpi=180)
    plt.close(fig)
    datos = {
        "funcion": "Rastrigin 2D", "dominio": [-LIMITE, LIMITE],
        "inicio_comun": inicio,
        "parametros": {"hc_paso": 0.1, "hc_max_iter": 500,
                       "sa_t0": 10.0, "sa_enfriamiento": 0.995,
                       "sa_iteraciones": 2000, "sa_sigma": 0.25, "sa_semilla_ejemplo": 42},
        "ejemplo": {"hill_climbing": {"x": hc_x, "valor": objetivo(hc_x), "iteraciones": len(hc_hist)-1},
                    "simulated_annealing": {"x": sa_x, "valor": objetivo(sa_x), "iteraciones": len(sa_hist)-1}},
        "30_inicios": {"media_hc": sum(valores_hc)/30, "media_sa": sum(valores_sa)/30,
                       "mediana_hc": sorted(valores_hc)[14:16],
                       "mediana_sa": sorted(valores_sa)[14:16],
                       "exitos_hc_f_menor_1": sum(v < 1 for v in valores_hc),
                       "exitos_sa_f_menor_1": sum(v < 1 for v in valores_sa),
                       "valores_hc": valores_hc, "valores_sa": valores_sa},
    }
    (OUT / "act3_resultados.json").write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    return datos


if __name__ == "__main__":
    ejecutar()

