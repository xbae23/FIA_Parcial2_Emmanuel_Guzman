# Fundamentos de Inteligencia Artificial - Parcial 2

**Estudiante:** Emmanuel Guzmán García · **Grupo:** 172 · **Universidad:** Politécnica de Atlautla
**Docente:** Mtro. Javier García Lara · **Periodo:** 12 al 26 de octubre de 2026

Portafolio de las seis secciones del enunciado: cuatro individuales y dos de equipo. Cada carpeta contiene su reporte PDF, código o material reproducible y resultados. [Abrir demostración visual](https://xbae23.github.io/FIA_Parcial2_Emmanuel_Guzman/).

| Carpeta | Sección | Entrega | Contenido |
| --- | --- | --- | --- |
| [Act1](Act1/) | 1.7 Aplicaciones y casos de estudio | 18 oct | Tres casos reales, tabla de KPI e infografía comparativa. |
| [Act2](Act2/) | 2.1 Problemas y 2.2 Espacios de búsqueda | 18 oct | Dos problemas modelados como grafos, búsqueda de estados y análisis de complejidad. |
| [Act3](Act3/) | 2.3 Búsqueda local | 22 oct | Hill Climbing y Simulated Annealing para optimización continua. |
| [Act4](Act4/) | 2.4 Búsqueda ciega | 25 oct | BFS y DFS para un laberinto, con comparación de tiempo y nodos. |
| [Act5](Act5/) | 2.5 Búsqueda heurística · equipo | 25 oct | A* vs Dijkstra sobre calles de Atlautla, mapa, métricas y dashboard. |
| [Act6](Act6/) | 2.6 Algoritmos genéticos · equipo | 26 oct | DEAP para un circuito de distribución, 30 generaciones y convergencia. |

**Equipo Act5 y Act6:** Bryan Salvador Ramos López, Alexis Kevin Pérez García, Jorge Lidio Barragán Villanueva y Emmanuel Guzmán García.

## Reproducir

Instala Python 3.10+ y las dependencias: `python -m pip install -r requirements.txt`. Desde la raíz, ejecuta `python Act2/act2_grafos.py`, `python Act3/act3_optimizacion.py`, `python Act4/act4_laberinto.py`, `python Act5/act5_rutas.py` y `python Act6/act6_genetico.py`. Los scripts generan imágenes y datos en sus carpetas `resultados/`. Para comprobar invariantes, ejecuta `python -m unittest discover -s tests -v`. Los PDF se pueden regenerar con `python generar_reportes.py`. La instantánea de OpenStreetMap ya está incluida y no requiere nueva descarga.

Para probar todos los ejercicios sin instalar Python, abre la [demostración publicada](https://xbae23.github.io/FIA_Parcial2_Emmanuel_Guzman/). Usa los botones de cada actividad para ejecutar búsquedas, optimizaciones y rutas directamente en el navegador. El tablero Plotly de Act5 también está disponible por separado. El JavaScript es una demostración interactiva; los programas Python y sus resultados son la implementación de referencia.

Los datos de Act2 y el laberinto de Act4 son ejemplos didácticos inventados y se identifican como tales. Los tres casos de Act1 proceden de fuentes verificables, citadas en el reporte. Los resultados experimentales de Act3 usan semillas fijas. La red vial de Act5–6 procede de OpenStreetMap (© colaboradores, ODbL); los desplazamientos y las ocho entregas son hipotéticos.

## Uso de IA

Se utilizó ChatGPT/Codex como apoyo para estructurar el portafolio, redactar borradores, desarrollar código, diagramas, interfaz y pruebas, y generar los PDF. Las salidas se verificaron mediante ejecución local y lectura de las fuentes indicadas. Los integrantes deben revisar, comprender y poder explicar la entrega antes de presentarla.

