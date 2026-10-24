# Fundamentos de Inteligencia Artificial - Parcial 2

**Estudiante:** Emmanuel Guzmán · **Grupo:** 172 · **Universidad:** Politécnica de Atlautla  
**Docente:** Mtro. Javier García Lara · **Periodo:** 12 al 26 de octubre de 2026

Portafolio de las cuatro secciones individuales del enunciado. Cada carpeta contiene su reporte PDF, código o material reproducible y resultados. Las secciones 5 y 6 son de equipo y no forman parte de esta entrega.

| Carpeta | Sección | Entrega | Contenido |
| --- | --- | --- | --- |
| [Act1](Act1/) | 1.7 Aplicaciones y casos de estudio | 18 oct | Tres casos reales, tabla de KPI e infografía comparativa. |
| [Act2](Act2/) | 2.1 Problemas y 2.2 Espacios de búsqueda | 18 oct | Dos problemas modelados como grafos, búsqueda de estados y análisis de complejidad. |
| [Act3](Act3/) | 2.3 Búsqueda local | 22 oct | Hill Climbing y Simulated Annealing para optimización continua. |
| [Act4](Act4/) | 2.4 Búsqueda ciega | 25 oct | BFS y DFS para un laberinto, con comparación de tiempo y nodos. |

## Reproducir

Instala Python 3.10+ y las dependencias: `python -m pip install -r requirements.txt`. Desde la raíz, ejecuta `python Act2/act2_grafos.py`, `python Act3/act3_optimizacion.py` y `python Act4/act4_laberinto.py`. Los scripts generan imágenes y datos en sus carpetas `resultados/`. Para comprobar invariantes, ejecuta `python -m unittest discover -s tests -v`. Los PDF se pueden regenerar con `python generar_reportes.py`.

Los datos de Act2 y el laberinto de Act4 son ejemplos didácticos inventados y se identifican como tales. Los tres casos de Act1 proceden de fuentes verificables, citadas en el reporte. Los resultados experimentales de Act3 usan semillas fijas para facilitar la reproducción.

## Uso de IA

Se utilizó ChatGPT/Codex como apoyo para estructurar el portafolio, redactar borradores, desarrollar código, diagramas y pruebas, y generar los PDF. Las salidas se verificaron mediante ejecución local y lectura de las fuentes indicadas. El estudiante debe revisar y poder explicar el trabajo antes de entregarlo.

