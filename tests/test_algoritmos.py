import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Act2"))
sys.path.insert(0, str(ROOT / "Act3"))
sys.path.insert(0, str(ROOT / "Act4"))

from act2_grafos import bfs, construir_grafos, dijkstra
from act3_optimizacion import hill_climbing, objetivo, simulated_annealing
from act4_laberinto import buscar, construir_grafo


class AlgoritmosTest(unittest.TestCase):
    def test_evacuacion_optima(self):
        grafo, _ = construir_grafos()
        ruta, _ = bfs(grafo, "Aula", "Salida")
        self.assertEqual(len(ruta) - 1, 3)
        self.assertEqual(ruta[0], "Aula")
        self.assertEqual(ruta[-1], "Salida")

    def test_reparto_optimo(self):
        _, grafo = construir_grafos()
        ruta, costo, _ = dijkstra(grafo, "Almacen", "Clinica")
        self.assertEqual(ruta, ["Almacen", "Centro", "Mercado", "Clinica"])
        self.assertEqual(costo, 8)

    def test_objetivo_y_optimizadores(self):
        self.assertAlmostEqual(objetivo((0, 0)), 0)
        inicio = (3.8, 3.8)
        self.assertLessEqual(objetivo(hill_climbing(inicio)[0]), objetivo(inicio))
        self.assertLessEqual(objetivo(simulated_annealing(inicio, 42)[0]), objetivo(inicio))

    def test_bfs_minimo_y_dfs_valido(self):
        grafo, inicio, meta = construir_grafo()
        ruta_bfs, _, _ = buscar(grafo, inicio, meta, "BFS")
        ruta_dfs, _, _ = buscar(grafo, inicio, meta, "DFS")
        self.assertTrue(ruta_bfs)
        for ruta in (ruta_bfs, ruta_dfs):
            self.assertEqual((ruta[0], ruta[-1]), (inicio, meta))
            self.assertTrue(all(grafo.has_edge(a, b) for a, b in zip(ruta, ruta[1:])))
        self.assertLessEqual(len(ruta_bfs), len(ruta_dfs))


if __name__ == "__main__":
    unittest.main()
