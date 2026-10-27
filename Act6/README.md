# Act6 · Algoritmo genético de distribución

Trabajo en equipo del grupo 172: Bryan Salvador Ramos López, Alexis Kevin Pérez García, Jorge Lidio Barragán Villanueva y Emmanuel Guzmán García.

Caso aplicado simulado: una brigada educativa sale de una base, visita ocho puntos hipotéticos sobre la red vial de Atlautla y regresa. Un algoritmo genético en Python con DEAP optimiza la distancia total en 30 generaciones. Se comparan vecino más cercano y el óptimo exacto Held–Karp como controles; los datos de las calles provienen de OpenStreetMap, no los destinos.

- [Reporte PDF](FIA_G172_GUZMAN_S6.pdf)
- [Código DEAP](act6_genetico.py)
- [Datos y resultados](resultados/act6_resultados.json)
- [Gráfica de convergencia](resultados/act6_convergencia.png) y [ruta](resultados/act6_ruta.png)

Desde la raíz del repositorio: `python -m pip install -r requirements.txt`, luego `python Act6/act6_genetico.py`. Usa las calles incluidas en `Act5/datos/red_atlautla.json`. Semilla de puntos: 2026; semilla del AG: 42; población: 80; cruce ordenado: 0.85; mutación de intercambio: 0.25; selección por torneo de tres; elitismo: dos. La página principal incluye una demostración interactiva en JavaScript; la solución de referencia evaluada es este programa DEAP.

Datos viales © [colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright), licencia ODbL. El escenario no corresponde a entregas reales.
