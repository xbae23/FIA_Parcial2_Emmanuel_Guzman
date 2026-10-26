"""Descarga una instantánea reproducible de calles de Atlautla desde OSM.

Uso excepcional: el archivo JSON ya está incluido; no es necesario descargarlo
para ejecutar los algoritmos. La red es una aproximación de caminata: no incluye
aceras, restricciones de giro ni cierres temporales.
"""
from __future__ import annotations

import json
import math
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx

BASE = Path(__file__).resolve().parent
OUT = BASE / "datos" / "red_atlautla.json"
BBOX = (19.018, -98.783, 19.031, -98.767)
URL = ("https://api.openstreetmap.org/api/0.6/map?bbox="
       f"{BBOX[1]},{BBOX[0]},{BBOX[3]},{BBOX[2]}")
TIPOS = {"residential", "tertiary", "secondary", "unclassified", "service",
         "primary", "living_street"}


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia geodésica aproximada en metros."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    dlat, dlon = la2-la1, lo2-lo1
    h = math.sin(dlat/2)**2 + math.cos(la1)*math.cos(la2)*math.sin(dlon/2)**2
    return 12742000 * math.asin(math.sqrt(h))


def descargar() -> dict:
    req = urllib.request.Request(URL,
                                 headers={"User-Agent": "FIA-Parcial2-educational/1.0 (OpenStreetMap attribution)"})
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = ET.parse(response).getroot()
    puntos = {e.attrib["id"]: (float(e.attrib["lat"]), float(e.attrib["lon"]))
              for e in raw.findall("node")}
    grafo = nx.Graph()
    for way in raw.findall("way"):
        tags = {e.attrib["k"]: e.attrib["v"] for e in way.findall("tag")}
        if tags.get("highway") not in TIPOS:
            continue
        referencias = [e.attrib["ref"] for e in way.findall("nd")]
        for a, b in zip(referencias, referencias[1:]):
            if a in puntos and b in puntos and a != b:
                grafo.add_edge(a, b, weight=haversine(puntos[a], puntos[b]))
    if not grafo:
        raise RuntimeError("OSM no devolvió calles utilizables")
    mayor = max(nx.connected_components(grafo), key=len)
    sub = grafo.subgraph(mayor).copy()
    nodos = {n: [round(v, 7) for v in puntos[n]] for n in sorted(sub.nodes())}
    aristas = [[a, b, round(sub[a][b]["weight"], 3)] for a, b in sorted(sub.edges())]
    salida = {
        "origen": "© OpenStreetMap contributors, ODbL 1.0",
        "url": "https://www.openstreetmap.org/copyright",
        "api": URL, "tipos_de_via": sorted(TIPOS),
        "fecha_descarga_utc": datetime.now(timezone.utc).isoformat(),
        "bbox": BBOX, "nota": "Componente conexa mayor de segmentos viales; grafo no dirigido de caminata aproximada.",
        "nodos": nodos, "aristas": aristas,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Guardados {len(nodos)} nodos y {len(aristas)} aristas en {OUT}")
    return salida


if __name__ == "__main__":
    descargar()
