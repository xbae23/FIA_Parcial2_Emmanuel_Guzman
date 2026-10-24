"""Dos problemas de búsqueda reproducibles sobre grafos de NetworkX."""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

BASE = Path(__file__).resolve().parent
OUT = BASE / "resultados"


def bfs(grafo: nx.Graph, inicio: str, meta: str) -> tuple[list[str], int]:
    """Busca el camino con menos aristas; cada arista cuesta una acción."""
    cola = deque([inicio])
    padres = {inicio: None}
    expandidos = 0
    while cola:
        actual = cola.popleft()
        expandidos += 1
        if actual == meta:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            return list(reversed(camino)), expandidos
        for vecino in sorted(grafo.neighbors(actual)):
            if vecino not in padres:
                padres[vecino] = actual
                cola.append(vecino)
    return [], expandidos


def dijkstra(grafo: nx.Graph, inicio: str, meta: str) -> tuple[list[str], float, int]:
    """Uniform-cost search con costos no negativos y desempate determinista."""
    import heapq
    cola = [(0.0, inicio)]
    costo = {inicio: 0.0}
    padres = {inicio: None}
    cerrados = set()
    while cola:
        distancia, actual = heapq.heappop(cola)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        if actual == meta:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            return list(reversed(camino)), distancia, len(cerrados)
        for vecino in sorted(grafo.neighbors(actual)):
            peso = float(grafo[actual][vecino]["weight"])
            if peso < 0:
                raise ValueError("Dijkstra requiere costos no negativos")
            nuevo = distancia + peso
            if nuevo < costo.get(vecino, float("inf")):
                costo[vecino] = nuevo
                padres[vecino] = actual
                heapq.heappush(cola, (nuevo, vecino))
    return [], float("inf"), len(cerrados)


def construir_grafos() -> tuple[nx.Graph, nx.Graph]:
    evacuacion = nx.Graph()
    evacuacion.add_edges_from([
        ("Aula", "Pasillo A"), ("Aula", "Laboratorio"),
        ("Pasillo A", "Escalera"), ("Laboratorio", "Patio"),
        ("Escalera", "Patio"), ("Escalera", "Enfermeria"),
        ("Patio", "Salida"), ("Enfermeria", "Salida"),
    ])
    reparto = nx.Graph()
    reparto.add_weighted_edges_from([
        ("Almacen", "Mercado", 4), ("Almacen", "Centro", 2),
        ("Mercado", "Clinica", 5), ("Centro", "Mercado", 1),
        ("Centro", "Parque", 7), ("Mercado", "Parque", 3),
        ("Parque", "Clinica", 2),
    ])
    return evacuacion, reparto


def dibujar(grafo: nx.Graph, titulo: str, archivo: Path, camino: list[str]) -> None:
    pos = nx.spring_layout(grafo, seed=11)
    fig, ax = plt.subplots(figsize=(8, 5))
    nx.draw_networkx(grafo, pos, ax=ax, node_size=2000, font_size=8,
                     node_color="#dceaf6", edge_color="#a6b8c7")
    aristas = list(zip(camino, camino[1:]))
    nx.draw_networkx_edges(grafo, pos, edgelist=aristas, ax=ax,
                           width=3.5, edge_color="#e06a3b")
    pesos = nx.get_edge_attributes(grafo, "weight")
    if pesos:
        nx.draw_networkx_edge_labels(grafo, pos, edge_labels=pesos, ax=ax)
    ax.set_title(titulo)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(archivo, dpi=170)
    plt.close(fig)


def ejecutar() -> dict:
    OUT.mkdir(exist_ok=True)
    evacuacion, reparto = construir_grafos()
    ruta1, n1 = bfs(evacuacion, "Aula", "Salida")
    ruta2, costo2, n2 = dijkstra(reparto, "Almacen", "Clinica")
    dibujar(evacuacion, "Evacuacion: minimo numero de pasos", OUT / "act2_evacuacion.png", ruta1)
    dibujar(reparto, "Reparto: minimo costo de recorrido", OUT / "act2_reparto.png", ruta2)
    datos = {
        "evacuacion": {"inicio": "Aula", "meta": "Salida", "camino": ruta1,
                       "pasos": len(ruta1) - 1, "nodos_expandidos": n1,
                       "estados": evacuacion.number_of_nodes(), "aristas": evacuacion.number_of_edges()},
        "reparto": {"inicio": "Almacen", "meta": "Clinica", "camino": ruta2,
                    "costo": costo2, "nodos_expandidos": n2,
                    "estados": reparto.number_of_nodes(), "aristas": reparto.number_of_edges()},
    }
    (OUT / "act2_resultados.json").write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    return datos


if __name__ == "__main__":
    ejecutar()

