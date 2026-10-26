# Act5 · A* y Dijkstra en una red vial

Trabajo en equipo del grupo 172: Bryan Salvador Ramos López, Alexis Kevin Pérez García, Jorge Lidio Barragán Villanueva y Emmanuel Guzmán García.

Se modela una ruta peatonal hipotética sobre una instantánea de calles reales de Atlautla, México, tomada de OpenStreetMap. Se compara A* con Dijkstra en distancia, nodos expandidos, tamaño de frontera y tiempo. La heurística `0.999 × distancia Haversine` es una cota conservadora debido al redondeo de las aristas. No es una herramienta de navegación real.

- [Reporte PDF](FIA_G172_Guzman_S5.pdf)
- [Código principal](act5_rutas.py) y [descarga/reconstrucción de la red](obtener_red_osm.py)
- [Red incluida](datos/red_atlautla.json), [resultados JSON](resultados/act5_resultados.json) y [dashboard Plotly](dashboard.html)
- [Mapa de rutas](resultados/act5_rutas.png) y [comparación](resultados/act5_comparacion.png)

Desde la raíz del repositorio: `python -m pip install -r requirements.txt`, luego `python Act5/act5_rutas.py`. La descarga de una nueva instantánea con `python Act5/obtener_red_osm.py` es opcional y requiere internet; puede alterar los resultados. La red y el análisis ya publicados son reproducibles sin descargar nada.

Datos © [colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright), licencia ODbL. Los puntos de inicio y fin se seleccionaron para el ejercicio y no representan una encomienda real.
