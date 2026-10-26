"""Algoritmo genético DEAP para una ruta de distribución educativa en Atlautla.

Los ocho puntos de entrega son hipotéticos, elegidos sobre nodos reales de OSM.
La matriz de costos usa caminos mínimos de la red vial incluida en Act5.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from deap import base, creator, tools

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Act5"))
from act5_rutas import cargar_red, extremos, punto

BASE = Path(__file__).resolve().parent
OUT = BASE / "resultados"
SEMILLA = 42
POBLACION = 80
GENERACIONES = 30
PROB_CRUCE = .85
PROB_MUTACION = .25
PARADAS = 8


def elegir_paradas(g: nx.Graph, deposito: str) -> list[str]:
    """Ocho puntos hipotéticos elegidos con semilla fija sobre la red real."""
    candidatos = sorted(n for n in g.nodes if n != deposito)
    return [deposito, *random.Random(2026).sample(candidatos, PARADAS)]


def matriz_distancias(g: nx.Graph, puntos: list[str]) -> list[list[float]]:
    return [[round(nx.shortest_path_length(g, a, b, weight="weight"), 3)
             for b in puntos] for a in puntos]


def longitud(cromosoma: list[int], matriz: list[list[float]]) -> float:
    """Costo del ciclo depósito -> ocho puntos -> depósito, en metros."""
    if sorted(cromosoma) != list(range(1, len(matriz))):
        raise ValueError("El cromosoma debe ser una permutación de las paradas 1..8")
    visita = [0, *cromosoma, 0]
    return sum(matriz[a][b] for a, b in zip(visita, visita[1:]))


def vecino_cercano(matriz: list[list[float]]) -> list[int]:
    pendiente = set(range(1, len(matriz)))
    ruta = []
    actual = 0
    while pendiente:
        siguiente = min(pendiente, key=lambda n: (matriz[actual][n], n))
        ruta.append(siguiente)
        pendiente.remove(siguiente)
        actual = siguiente
    return ruta


def optimo_exacto(matriz: list[list[float]]) -> tuple[float, list[int]]:
    """Held-Karp para ocho paradas; referencia de validación, no parte del AG."""
    n = len(matriz) - 1
    dp = {}
    for j in range(1, n+1):
        dp[(1 << (j-1), j)] = (matriz[0][j], [j])
    for mask in range(1, 1 << n):
        for j in range(1, n+1):
            if not mask & (1 << (j-1)) or mask == 1 << (j-1):
                continue
            previo = mask ^ (1 << (j-1))
            candidatos = [(dp[(previo,k)][0] + matriz[k][j], dp[(previo,k)][1] + [j])
                          for k in range(1,n+1) if previo & (1 << (k-1))]
            dp[(mask,j)] = min(candidatos, key=lambda x: x[0])
    return min(((dp[((1 << n)-1,j)][0] + matriz[j][0], dp[((1 << n)-1,j)][1])
                for j in range(1,n+1)), key=lambda x:x[0])


def cruce_ordenado(a: list[int], b: list[int]) -> tuple[list[int],list[int]]:
    """DEAP cxOrdered indexa desde cero; los índices externos son 1..8."""
    copia_a, copia_b = [v-1 for v in a], [v-1 for v in b]
    tools.cxOrdered(copia_a, copia_b)
    a[:], b[:] = [v+1 for v in copia_a], [v+1 for v in copia_b]
    return a, b


def algoritmo_genetico(matriz: list[list[float]], semilla: int = SEMILLA) -> dict:
    random.seed(semilla)
    if not hasattr(creator, "FitnessMinFIA"):
        creator.create("FitnessMinFIA", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "RutaFIA"):
        creator.create("RutaFIA", list, fitness=creator.FitnessMinFIA)
    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(1, len(matriz)), len(matriz)-1)
    toolbox.register("individual", tools.initIterate, creator.RutaFIA, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", lambda ind: (longitud(ind, matriz),))
    toolbox.register("mate", cruce_ordenado)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=.12)
    toolbox.register("select", tools.selTournament, tournsize=3)
    poblacion = toolbox.population(n=POBLACION)
    for ind in poblacion:
        ind.fitness.values = toolbox.evaluate(ind)
    hof = tools.HallOfFame(1)
    hof.update(poblacion)
    historia = [{"generacion":0,
                 "mejor_m":round(hof[0].fitness.values[0],3),
                 "media_m":round(statistics.mean(i.fitness.values[0] for i in poblacion),3)}]
    for gen in range(1, GENERACIONES+1):
        elite = [toolbox.clone(x) for x in tools.selBest(poblacion, 2)]
        hijos = [toolbox.clone(x) for x in toolbox.select(poblacion, POBLACION-2)]
        for a,b in zip(hijos[::2], hijos[1::2]):
            if random.random() < PROB_CRUCE:
                toolbox.mate(a,b)
                del a.fitness.values, b.fitness.values
        for ind in hijos:
            if random.random() < PROB_MUTACION:
                toolbox.mutate(ind)
                if ind.fitness.valid:
                    del ind.fitness.values
        for ind in hijos:
            if not ind.fitness.valid:
                ind.fitness.values = toolbox.evaluate(ind)
        poblacion = elite + hijos
        hof.update(poblacion)
        historia.append({"generacion":gen,
                         "mejor_m":round(hof[0].fitness.values[0],3),
                         "media_m":round(statistics.mean(i.fitness.values[0] for i in poblacion),3)})
    return {"ruta":list(hof[0]), "distancia_m":round(hof[0].fitness.values[0],3),
            "historia":historia}


def trazo_completo(g: nx.Graph, puntos: list[str], orden: list[int]) -> list[str]:
    paradas = [0, *orden, 0]
    ruta = []
    for a,b in zip(paradas,paradas[1:]):
        tramo = nx.shortest_path(g,puntos[a],puntos[b],weight="weight")
        ruta.extend(tramo if not ruta else tramo[1:])
    return ruta


def graficar(g: nx.Graph, puntos: list[str], resultado: dict, exacto: float) -> None:
    OUT.mkdir(exist_ok=True)
    h = resultado["historia"]
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.plot([x["generacion"] for x in h],[x["mejor_m"] for x in h],
            color="#eb7447",lw=2,label="Mejor histórico")
    ax.plot([x["generacion"] for x in h],[x["media_m"] for x in h],
            color="#0d8c9d",lw=1.6,label="Media de población")
    ax.axhline(exacto,color="#223a59",ls="--",label="Óptimo exacto (control)")
    ax.set(xlabel="Generación",ylabel="Distancia del circuito (m)",
           title="AG DEAP: 30 generaciones")
    ax.legend(); ax.grid(alpha=.2); fig.tight_layout()
    fig.savefig(OUT/"act6_convergencia.png",dpi=180);plt.close(fig)

    ruta=trazo_completo(g,puntos,resultado["ruta"])
    fig,ax=plt.subplots(figsize=(8,7))
    for a,b in g.edges:
        x,y=punto(g,a),punto(g,b)
        ax.plot([x[1],y[1]],[x[0],y[0]],color="#d2dce4",lw=.5)
    coords=[punto(g,n) for n in ruta]
    ax.plot([v[1] for v in coords],[v[0] for v in coords],color="#eb7447",lw=2.3)
    for i,n in enumerate(puntos):
        lat,lon=punto(g,n)
        ax.scatter(lon,lat,color="#17365d",s=40,zorder=5)
        ax.annotate("Base" if i==0 else str(i),(lon,lat),xytext=(4,5),textcoords="offset points")
    ax.set(xlabel="Longitud",ylabel="Latitud",title="Circuito de distribución sobre red vial real")
    ax.set_aspect("equal",adjustable="datalim");fig.tight_layout()
    fig.savefig(OUT/"act6_ruta.png",dpi=180);plt.close(fig)


def ejecutar() -> dict:
    g,fuente=cargar_red()
    deposito,_=extremos(g)
    puntos=elegir_paradas(g,deposito)
    matriz=matriz_distancias(g,puntos)
    resultado=algoritmo_genetico(matriz)
    base=vecino_cercano(matriz)
    optimo,orden_optimo=optimo_exacto(matriz)
    graficar(g,puntos,resultado,optimo)
    trazo=trazo_completo(g,puntos,resultado["ruta"])
    datos={"caso":"Brigada hipotética de entrega de materiales educativos en Atlautla",
           "origen_red":fuente["url"],"paradas_hipoteticas":True,
           "semilla_seleccion_paradas":2026,
           "parametros":{"semilla":SEMILLA,"poblacion":POBLACION,
                         "generaciones":GENERACIONES,"prob_cruce":PROB_CRUCE,
                         "prob_mutacion":PROB_MUTACION,"prob_gen_mutacion":.12,
                         "seleccion":"torneo de 3","cruce":"cxOrdered",
                         "mutacion":"mutShuffleIndexes","elitismo":2},
           "puntos":[{"nombre":"Base" if i==0 else f"Punto {i}","id":n,
                      "latlon":punto(g,n)} for i,n in enumerate(puntos)],
           "matriz_distancias_m":matriz,
           "ruta_ga":resultado["ruta"],"distancia_ga_m":resultado["distancia_m"],
           "historia":resultado["historia"],
           "ruta_vecino_cercano":base,"distancia_vecino_cercano_m":round(longitud(base,matriz),3),
           "ruta_optima_control":orden_optimo,"distancia_optima_control_m":round(optimo,3),
           "brecha_optima_pct":round(100*(resultado["distancia_m"]-optimo)/optimo,2),
           "coordenadas_trazo_ga":[punto(g,n) for n in trazo]}
    (OUT/"act6_resultados.json").write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"distancia_ga_m":datos["distancia_ga_m"],
                      "distancia_vecino_cercano_m":datos["distancia_vecino_cercano_m"],
                      "distancia_optima_control_m":datos["distancia_optima_control_m"],
                      "brecha_optima_pct":datos["brecha_optima_pct"]},indent=2))
    return datos


if __name__=="__main__":
    ejecutar()
