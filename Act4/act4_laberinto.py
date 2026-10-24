"""BFS y DFS iterativos sobre un laberinto de celdas libres."""
from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

BASE = Path(__file__).resolve().parent
OUT = BASE / "resultados"
MAPA = [
    "S........G",
    ".########.",
    ".#....#...",
    ".#.#..#.#.",
    ".#.#....#.",
    ".#......#.",
    "..........",
]


def construir_grafo(mapa: list[str] = MAPA) -> tuple[nx.Graph, tuple[int,int], tuple[int,int]]:
    if not mapa or len({len(fila) for fila in mapa}) != 1:
        raise ValueError("Mapa vacio o no rectangular")
    grafo = nx.Graph()
    inicio = meta = None
    for y, fila in enumerate(mapa):
        for x, celda in enumerate(fila):
            if celda == "#":
                continue
            grafo.add_node((y, x))
            if celda == "S": inicio = (y, x)
            if celda == "G": meta = (y, x)
            for previo in ((y-1, x), (y, x-1)):
                if previo in grafo:
                    grafo.add_edge((y, x), previo)
    if inicio is None or meta is None:
        raise ValueError("Falta S o G")
    return grafo, inicio, meta


def buscar(grafo: nx.Graph, inicio: tuple[int,int], meta: tuple[int,int],
           metodo: str) -> tuple[list[tuple[int,int]], int, int]:
    """Devuelve ruta, nodos expandidos y máximo de frontera."""
    if metodo not in {"BFS", "DFS"}:
        raise ValueError("Metodo debe ser BFS o DFS")
    frontera = deque([inicio])
    padres = {inicio: None}
    expandidos = 0
    max_frontera = 1
    while frontera:
        actual = frontera.popleft() if metodo == "BFS" else frontera.pop()
        expandidos += 1
        if actual == meta:
            ruta = []
            while actual is not None:
                ruta.append(actual)
                actual = padres[actual]
            return list(reversed(ruta)), expandidos, max_frontera
        vecinos = sorted(grafo.neighbors(actual))
        # En DFS la pila visita primero el vecino mayor en orden (fila, columna).
        for vecino in vecinos:
            if vecino not in padres:
                padres[vecino] = actual
                frontera.append(vecino)
        max_frontera = max(max_frontera, len(frontera))
    return [], expandidos, max_frontera


def dibujar_mapa(rutas: dict[str,list[tuple[int,int]]]) -> None:
    fig, ejes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, (nombre, ruta) in zip(ejes, [("Laberinto", []), *rutas.items()]):
        for y, fila in enumerate(MAPA):
            for x, celda in enumerate(fila):
                color = "#26384a" if celda == "#" else "#edf3f7"
                if (y, x) in ruta: color = "#f4aa72"
                if celda == "S": color = "#56b98f"
                if celda == "G": color = "#6a82d9"
                ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=color, edgecolor="white"))
        ax.set_xlim(0, len(MAPA[0])); ax.set_ylim(len(MAPA), 0)
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(nombre)
    fig.tight_layout()
    fig.savefig(OUT / "act4_rutas.png", dpi=180)
    plt.close(fig)


def ejecutar() -> dict:
    OUT.mkdir(exist_ok=True)
    grafo, inicio, meta = construir_grafo()
    datos = {"mapa": MAPA, "estados_libres": grafo.number_of_nodes(),
             "aristas": grafo.number_of_edges(), "inicio": inicio, "meta": meta}
    rutas = {}
    for metodo in ("BFS", "DFS"):
        t0 = time.perf_counter_ns()
        ruta, expandidos, max_frontera = buscar(grafo, inicio, meta, metodo)
        tiempo_us = (time.perf_counter_ns() - t0) / 1000
        rutas[metodo] = ruta
        datos[metodo] = {"ruta": ruta, "pasos": len(ruta)-1,
                         "nodos_expandidos": expandidos, "max_frontera": max_frontera,
                         "tiempo_microsegundos_una_ejecucion": tiempo_us}
    dibujar_mapa(rutas)
    pos = {(y,x):(x,-y) for y,x in grafo.nodes}
    fig, ax = plt.subplots(figsize=(11, 7))
    nx.draw(grafo, pos, ax=ax, node_size=80, node_color="#87aeca", edge_color="#b3c2cc")
    ax.set_title("Grafo de estados: una celda libre = un nodo")
    fig.tight_layout(); fig.savefig(OUT / "act4_grafo.png", dpi=170); plt.close(fig)
    (OUT / "act4_resultados.json").write_text(json.dumps(datos, indent=2), encoding="utf-8")
    print(json.dumps(datos, indent=2))
    return datos


if __name__ == "__main__":
    ejecutar()

