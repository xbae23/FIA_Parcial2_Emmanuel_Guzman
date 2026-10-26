"""A* y Dijkstra sobre una instantánea real de calles de Atlautla.

La red es una aproximación caminable no dirigida; los extremos son nodos viales
reales, pero el motivo del viaje es un escenario académico simulado.
"""
from __future__ import annotations

import heapq
import json
import math
import statistics
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from obtener_red_osm import haversine

BASE = Path(__file__).resolve().parent
RED = BASE / "datos" / "red_atlautla.json"
OUT = BASE / "resultados"
CAMPUS_APROX = (19.024609, -98.77549)


def cargar_red() -> tuple[nx.Graph, dict]:
    datos = json.loads(RED.read_text(encoding="utf-8"))
    g = nx.Graph()
    for identificador, (lat, lon) in datos["nodos"].items():
        g.add_node(identificador, lat=lat, lon=lon)
    for a, b, metros in datos["aristas"]:
        g.add_edge(a, b, weight=metros)
    return g, datos


def punto(g: nx.Graph, nodo: str) -> tuple[float, float]:
    return g.nodes[nodo]["lat"], g.nodes[nodo]["lon"]


def mas_cercano(g: nx.Graph, latlon: tuple[float,float]) -> str:
    return min(g.nodes, key=lambda n: (haversine(punto(g, n), latlon), n))


def extremos(g: nx.Graph) -> tuple[str, str]:
    inicio = mas_cercano(g, CAMPUS_APROX)
    meta = max(g.nodes, key=lambda n: (haversine(punto(g, inicio), punto(g, n)), n))
    return inicio, meta


def buscar(g: nx.Graph, inicio: str, meta: str, algoritmo: str) -> dict:
    if algoritmo not in {"Dijkstra", "A*"}:
        raise ValueError("Algoritmo no reconocido")
    objetivo = punto(g, meta)
    # Factor conservador por el redondeo a milímetros de los pesos del JSON.
    def h(n: str) -> float:
        return 0.999 * haversine(punto(g, n), objetivo) if algoritmo == "A*" else 0.0
    cola = [(h(inicio), h(inicio), inicio)]
    dist = {inicio: 0.0}
    padres = {inicio: None}
    cerrados = set()
    max_cola = 1
    while cola:
        _, _, actual = heapq.heappop(cola)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        if actual == meta:
            ruta = []
            while actual is not None:
                ruta.append(actual)
                actual = padres[actual]
            ruta.reverse()
            return {"ruta": ruta, "distancia_m": round(dist[meta], 3),
                    "nodos_expandidos": len(cerrados), "max_frontera": max_cola}
        for vecino in sorted(g.neighbors(actual)):
            if vecino in cerrados:
                continue
            nuevo = dist[actual] + g[actual][vecino]["weight"]
            if nuevo < dist.get(vecino, math.inf) - 1e-9:
                dist[vecino] = nuevo
                padres[vecino] = actual
                estimacion = h(vecino)
                heapq.heappush(cola, (nuevo + estimacion, estimacion, vecino))
        max_cola = max(max_cola, len(cola))
    raise ValueError("No existe una ruta dentro del grafo")


def medir(g: nx.Graph, inicio: str, meta: str, algoritmo: str, repeticiones: int = 50) -> tuple[dict, float]:
    muestras = []
    resultado = None
    for _ in range(repeticiones):
        t0 = time.perf_counter_ns()
        resultado = buscar(g, inicio, meta, algoritmo)
        muestras.append((time.perf_counter_ns() - t0) / 1e6)
    return resultado, round(statistics.median(muestras), 4)


def dibujar(g: nx.Graph, rutas: dict[str,dict]) -> None:
    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 7))
    for a, b in g.edges:
        pa, pb = punto(g, a), punto(g, b)
        ax.plot([pa[1], pb[1]], [pa[0], pb[0]], color="#cbd5df", lw=.7)
    colores = {"Dijkstra": "#0d8c9d", "A*": "#eb7447"}
    for nombre, res in rutas.items():
        coords = [punto(g, n) for n in res["ruta"]]
        ax.plot([v[1] for v in coords], [v[0] for v in coords],
                color=colores[nombre], lw=2.6, label=nombre, alpha=.9)
    for nodo, etiqueta in ((rutas["A*"]["ruta"][0], "Inicio"),
                           (rutas["A*"]["ruta"][-1], "Meta")):
        lat, lon = punto(g, nodo)
        ax.scatter(lon, lat, s=50, color="#172b4d", zorder=5)
        ax.annotate(etiqueta, (lon, lat), xytext=(5, 6), textcoords="offset points")
    ax.set(xlabel="Longitud", ylabel="Latitud", title="Red vial de Atlautla: A* y Dijkstra")
    ax.legend(); ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout(); fig.savefig(OUT / "act5_rutas.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Dijkstra", "A*"], [rutas[k]["nodos_expandidos"] for k in ("Dijkstra", "A*")],
           color=[colores["Dijkstra"], colores["A*"]])
    ax.set(ylabel="Nodos expandidos", title="Trabajo de búsqueda por algoritmo")
    fig.tight_layout(); fig.savefig(OUT / "act5_comparacion.png", dpi=180); plt.close(fig)


def dashboard(g: nx.Graph, rutas: dict[str,dict]) -> None:
    fig = make_subplots(rows=1, cols=2, column_widths=[.73, .27],
                        specs=[[{"type":"scatter"},{"type":"bar"}]],
                        subplot_titles=("Mapa de segmentos y rutas", "Nodos expandidos"))
    xs, ys = [], []
    for a, b in g.edges:
        pa, pb = punto(g,a), punto(g,b)
        xs.extend([pa[1],pb[1],None]); ys.extend([pa[0],pb[0],None])
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",line=dict(color="#c7d2df",width=1),
                             name="Calles OSM",hoverinfo="skip"), row=1,col=1)
    for nombre,color in (("Dijkstra","#0d8c9d"),("A*","#eb7447")):
        coords=[punto(g,n) for n in rutas[nombre]["ruta"]]
        fig.add_trace(go.Scatter(x=[v[1] for v in coords],y=[v[0] for v in coords],
                                 mode="lines+markers",marker=dict(size=4),
                                 line=dict(color=color,width=4),name=nombre,
                                 hovertemplate="Lat %{y:.5f}, lon %{x:.5f}<extra>"+nombre+"</extra>"),row=1,col=1)
    fig.add_trace(go.Bar(x=["Dijkstra","A*"],
                         y=[rutas[k]["nodos_expandidos"] for k in ("Dijkstra","A*")],
                         marker_color=["#0d8c9d","#eb7447"],showlegend=False),row=1,col=2)
    fig.update_layout(title="Act5 · A* y Dijkstra en Atlautla",height=630,
                      template="plotly_white",font=dict(family="Arial"),
                      legend=dict(orientation="h",y=-.09))
    fig.update_xaxes(title_text="Longitud",row=1,col=1)
    fig.update_yaxes(title_text="Latitud",row=1,col=1,scaleanchor="x",scaleratio=1)
    fig.update_yaxes(title_text="Estados",row=1,col=2)
    fig.write_html(BASE / "dashboard.html",include_plotlyjs=True,full_html=True)


def ejecutar() -> dict:
    g, fuente = cargar_red()
    inicio, meta = extremos(g)
    rutas = {}
    for algoritmo in ("Dijkstra", "A*"):
        rutas[algoritmo], tiempo = medir(g, inicio, meta, algoritmo)
        rutas[algoritmo]["tiempo_mediana_ms_50"] = tiempo
        rutas[algoritmo]["coordenadas_ruta"] = [punto(g,n) for n in rutas[algoritmo]["ruta"]]
    dibujar(g, rutas)
    dashboard(g, rutas)
    datos = {"fuente": fuente["url"], "fecha_descarga_utc": fuente["fecha_descarga_utc"],
             "modelo": fuente["nota"], "nodos": g.number_of_nodes(),
             "aristas": g.number_of_edges(), "inicio": {"id":inicio,"latlon":punto(g,inicio)},
             "meta": {"id":meta,"latlon":punto(g,meta)}, "resultados": rutas,
             "heuristica": "0.999 × Haversine en metros; factor conservador frente al redondeo de aristas."}
    (OUT / "act5_resultados.json").write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:{"distancia_m":v["distancia_m"],"nodos_expandidos":v["nodos_expandidos"],
                         "tiempo_mediana_ms_50":v["tiempo_mediana_ms_50"]}
                      for k,v in rutas.items()},indent=2))
    return datos


if __name__ == "__main__":
    ejecutar()
