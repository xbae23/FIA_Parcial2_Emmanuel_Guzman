"""Genera los seis reportes PDF del portafolio a partir de resultados reproducibles."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageBreak,
                                PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle)

BASE = Path(__file__).resolve().parent
ALUMNO = "Emmanuel Guzmán García"
EQUIPO = ["Bryan Salvador Ramos López", "Alexis Kevin Pérez García",
          "Jorge Lidio Barragán Villanueva", ALUMNO]
GRUPO = "172"
REPO_URL = "https://github.com/xbae23/FIA_Parcial2_Emmanuel_Guzman"
WEB_URL = "https://xbae23.github.io/FIA_Parcial2_Emmanuel_Guzman/"
AZUL = colors.HexColor("#17365D")
CIAN = colors.HexColor("#0D9DB2")
GRIS = colors.HexColor("#536273")

FONT_DIR = Path("C:/Windows/Fonts")
if (FONT_DIR / "arial.ttf").exists():
    pdfmetrics.registerFont(TTFont("FIA", str(FONT_DIR / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("FIA-Bold", str(FONT_DIR / "arialbd.ttf")))
    pdfmetrics.registerFontFamily("FIA", normal="FIA", bold="FIA-Bold")
    FUENTE, NEGRITA = "FIA", "FIA-Bold"
else:
    FUENTE, NEGRITA = "Helvetica", "Helvetica-Bold"
if (FONT_DIR / "consola.ttf").exists():
    pdfmetrics.registerFont(TTFont("FIA-Code", str(FONT_DIR / "consola.ttf")))
    CODIGO = "FIA-Code"
else:
    CODIGO = "Courier"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloFIA", fontName=NEGRITA, fontSize=20,
                          leading=25, textColor=AZUL, spaceAfter=15))
styles.add(ParagraphStyle(name="SubFIA", fontName=NEGRITA, fontSize=12,
                          leading=15, textColor=AZUL, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="CuerpoFIA", fontName=FUENTE, fontSize=9.2,
                          leading=12.6, spaceAfter=5))
styles.add(ParagraphStyle(name="PieFIA", fontName=FUENTE, fontSize=7.7,
                          leading=10, textColor=GRIS, spaceAfter=5))
styles.add(ParagraphStyle(name="TablaFIA", fontName=FUENTE, fontSize=8,
                          leading=10.5))
styles.add(ParagraphStyle(name="TablaCabFIA", fontName=NEGRITA, fontSize=8,
                          leading=10.5, textColor=colors.white))
styles.add(ParagraphStyle(name="PortadaFIA", fontName=NEGRITA, fontSize=24,
                          leading=29, textColor=AZUL, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CentroFIA", fontName=FUENTE, fontSize=11,
                          leading=16, alignment=TA_CENTER, spaceAfter=9))
styles.add(ParagraphStyle(name="CodigoFIA", fontName=CODIGO, fontSize=6.5,
                          leading=8.5, leftIndent=3))


def P(text: str, estilo: str = "CuerpoFIA") -> Paragraph:
    return Paragraph(text, styles[estilo])


def H(text: str) -> Paragraph:
    return P(text, "SubFIA")


def tabla(cabeceras: list[str], filas: list[list[str]], anchos=None) -> Table:
    data = [[P(escape(v), "TablaCabFIA") for v in cabeceras]]
    data += [[P(escape(str(v)), "TablaFIA") for v in fila] for fila in filas]
    t = Table(data, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF5F8")]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C6D4DD")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def foto(path: Path, ancho: float = 16.4*cm) -> Image:
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        ratio = im.height / im.width
    return Image(str(path), width=ancho, height=ancho*ratio)


class Reporte(BaseDocTemplate):
    def __init__(self, archivo: Path, seccion: str):
        super().__init__(str(archivo), pagesize=A4, leftMargin=2.1*cm,
                         rightMargin=2.1*cm, topMargin=2.2*cm, bottomMargin=1.9*cm,
                         title=f"{seccion} - Fundamentos de IA", author=ALUMNO)
        self.seccion = seccion
        marco = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
        self.addPageTemplates(PageTemplate(id="normal", frames=[marco], onPage=self.decorar))

    def decorar(self, canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(CIAN); canvas.setLineWidth(2)
        canvas.line(2.1*cm, h-1.6*cm, w-2.1*cm, h-1.6*cm)
        canvas.setFont(NEGRITA, 8); canvas.setFillColor(AZUL)
        canvas.drawString(2.1*cm, h-1.35*cm, "FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL")
        canvas.setFont(FUENTE, 8); canvas.setFillColor(GRIS)
        canvas.drawString(2.1*cm, 1.25*cm, f"{self.seccion}  |  G172")
        canvas.drawRightString(w-2.1*cm, 1.25*cm, f"Página {doc.page}")
        canvas.restoreState()


def portada(numero: int, tema: str, fecha: str, equipo: bool = False) -> list:
    return [Spacer(1, 1.4*cm), P("UNIVERSIDAD POLITÉCNICA DE ATLAUTLA", "CentroFIA"),
            P("Ingeniería en Tecnologías de la Información e Innovación Digital", "CentroFIA"),
            Spacer(1, 1.0*cm), P(f"ACTIVIDAD {numero}", "PortadaFIA"),
            Spacer(1, 0.3*cm), P(escape(tema), "PortadaFIA"),
            Spacer(1, 1.1*cm),
            tabla(["Datos de entrega", "Información"], [
                ["Asignatura", "Fundamentos de Inteligencia Artificial"],
                ["Integrantes" if equipo else "Alumno", " · ".join(EQUIPO) if equipo else ALUMNO], ["Grupo", GRUPO],
                ["Docente", "Mtro. Javier García Lara"],
                ["Fecha indicada en el enunciado", fecha + " de octubre de 2026"],
            ], [5.4*cm, 11.3*cm]),
            Spacer(1, 0.5*cm),
            P(f"Repositorio: <link href='{REPO_URL}' color='#0D9DB2'>{REPO_URL}</link>", "PieFIA"),
            P(f"Demostración: <link href='{WEB_URL}' color='#0D9DB2'>{WEB_URL}</link>", "PieFIA"),
            P(("Trabajo en equipo" if equipo else "Portafolio individual") + " versionado en GitHub. Se incluyen planteamiento, "
              "procedimiento, evidencia, conclusiones y referencias.", "PieFIA"),
            Spacer(1, 0.7*cm)]


def declaracion() -> list:
    return [H("Uso de inteligencia artificial y verificación"),
            P("Se utilizó ChatGPT/Codex para apoyar la organización del reporte, la redacción, "
              "el desarrollo de código y gráficos. Se ejecutaron los programas y pruebas locales, "
              "y se cotejaron las afirmaciones documentales con las fuentes citadas. Quienes "
              "presentan el trabajo deben revisarlo, comprenderlo y poder explicarlo.")]


def referencias_comunes() -> list:
    return [H("Referencias (APA 7.ª ed.)"),
            P("Russell, S., &amp; Norvig, P. (2020). <i>Artificial intelligence: A modern approach</i> (4th ed.). Pearson."),
            P("Bohm, R. A. (2021). <i>The fundamentals of search algorithms</i>. Nova Science Publishers."),
            P("Documentación oficial de NetworkX. (s. f.). <i>Algorithms</i>. https://networkx.org/documentation/stable/reference/algorithms/")]


def anexo_codigo(act: int, archivo: str) -> list:
    lineas = (BASE / f"Act{act}" / archivo).read_text(encoding="utf-8").splitlines()
    piezas = [PageBreak(), H("Anexo: código Python completo"),
              P(f"Archivo ejecutable <b>Act{act}/{archivo}</b>. La numeración facilita la revisión; "
                "el archivo del repositorio es la versión directamente ejecutable.", "PieFIA")]
    for i in range(0, len(lineas), 55):
        bloque = "\n".join(f"{j+1:03d}  {lineas[j]}" for j in range(i, min(i+55, len(lineas))))
        piezas.append(Preformatted(bloque, styles["CodigoFIA"]))
    return piezas


def infografia() -> Path:
    destino = BASE / "Act1" / "resultados" / "act1_infografia.png"
    destino.parent.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.2))
    fig.patch.set_facecolor("#f6fafc"); ax.set_facecolor("#f6fafc")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    tarjetas = [
        (0.25, "SALUD", "IDx-DR", "Imagen retinal → detección", "KPI: sensibilidad / especificidad", "FDA: autorización en 2018"),
        (4.2, "INDUSTRIA", "DeepMind", "Sensores → redes neuronales", "KPI: energía de refrigeración", "Hasta 40% menos refrigeración"),
        (8.15, "MOVILIDAD", "Google Maps", "Tráfico + relieve → rutas", "KPI: consumo / CO₂e estimado", "Ruta eficiente según vehículo"),
    ]
    for x, sector, caso, tecnica, kpi, impacto in tarjetas:
        ax.add_patch(plt.Rectangle((x, .55), 3.6, 4.7, facecolor="white",
                                   edgecolor="#cadbe5", linewidth=1.5))
        ax.add_patch(plt.Rectangle((x, 4.6), 3.6, .65, facecolor="#17365d"))
        ax.text(x+.18, 4.92, sector, color="white", fontsize=11, weight="bold", va="center")
        ax.text(x+.18, 4.15, caso, color="#17365d", fontsize=15, weight="bold")
        ax.text(x+.18, 3.34, tecnica, fontsize=9.5)
        ax.text(x+.18, 2.42, kpi, fontsize=9.3, color="#435e70")
        ax.text(x+.18, 1.38, impacto, fontsize=9.5, weight="bold", color="#0d8496")
    ax.text(6, 5.65, "Tres aplicaciones reales de IA", ha="center", fontsize=17,
            weight="bold", color="#17365d")
    fig.tight_layout(); fig.savefig(destino, dpi=180); plt.close(fig)
    return destino


def act1() -> None:
    s = portada(1, "Aplicaciones y casos de estudio de IA", "18")
    s += [H("Propósito y método"),
          P("Comparar tres aplicaciones reales de IA en salud, industria y movilidad. "
            "Se seleccionaron fuentes primarias de la FDA y de las organizaciones que operan "
            "los sistemas. Los KPI se distinguen entre cifras publicadas y métricas propuestas "
            "para evaluar una aplicación local."),
          H("1. Salud: IDx-DR y retinopatía diabética"),
          P("<b>Problema.</b> El cribado de retinopatía diabética necesita interpretar fotografías "
            "de retina y derivar oportunamente a pacientes con hallazgos. <b>Técnica.</b> El sistema "
            "IDx-DR emplea análisis automatizado de imágenes mediante IA para emitir una decisión "
            "diagnóstica dentro de su uso autorizado. <b>Resultado verificable.</b> La FDA concedió "
            "la clasificación De Novo DEN180001 el 11 de abril de 2018. Esa autorización no "
            "equivale a afirmar que el sistema reemplaza cualquier examen oftalmológico. "
            "<b>KPI.</b> Sensibilidad, especificidad, proporción de imágenes evaluables y tiempo "
            "hasta referencia clínica; requieren medición en la población y flujo concretos."),
          H("2. Industria: refrigeración de centros de datos de Google"),
          P("<b>Problema.</b> La refrigeración consume energía y depende de interacciones "
            "no lineales entre clima, cargas y equipos. <b>Técnica.</b> DeepMind entrenó un "
            "conjunto de redes neuronales con datos históricos de sensores para predecir la "
            "eficiencia energética futura y ajustar recomendaciones operativas. <b>Impacto "
            "publicado.</b> La organización informó una reducción de hasta 40% de la energía "
            "utilizada para refrigeración en los centros evaluados; es una cifra propia de "
            "Google, no una garantía transferible. <b>KPI.</b> kWh de refrigeración, PUE, "
            "temperatura fuera de rango y costo por unidad de cómputo."),
          H("3. Movilidad: rutas de bajo consumo en Google Maps"),
          P("<b>Problema.</b> La ruta más rápida no siempre minimiza combustible o energía. "
            "<b>Técnica.</b> Maps compara alternativas considerando tráfico, pendientes, "
            "tipo de vía y motorización. <b>Resultado.</b> La ayuda oficial describe "
            "estimaciones de eficiencia y recomienda la ruta eficiente cuando su llegada es "
            "aproximadamente similar a la más rápida; la disponibilidad depende de la región. "
            "<b>KPI.</b> litros o kWh por trayecto, CO₂e estimado y diferencia de tiempo."),
          H("Comparación de criterios"),
          tabla(["Caso", "Rama / técnica", "Dato publicado", "KPI para evaluar"], [
              ["IDx-DR", "Visión computacional / IA diagnóstica", "Autorización FDA, 2018", "Sensibilidad y especificidad"],
              ["DeepMind", "Aprendizaje supervisado y optimización", "Hasta 40% menos energía de refrigeración", "kWh y PUE"],
              ["Maps", "Predicción y optimización de rutas", "Función de rutas eficientes documentada", "Combustible, CO₂e y ETA"],
          ], [2.45*cm, 4.75*cm, 4.65*cm, 4.85*cm]),
          H("Infografía comparativa"), foto(infografia(), 14.5*cm),
          H("Conclusión reflexiva"),
          P("La IA es valiosa cuando una decisión medible mejora un proceso concreto. "
            "La aprobación regulatoria, una cifra energética comunicada por el operador "
            "y una función de navegación son evidencias de naturaleza distinta. Para "
            "compararlas responsablemente se necesitan datos locales, línea base, "
            "supervisión humana y mediciones posteriores."),
          H("Referencias (APA 7.ª ed.)"),
          P("U.S. Food and Drug Administration. (2018). <i>Device classification under section 513(f)(2) (De Novo): IDx-DR (DEN180001)</i>. https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?id=DEN180001"),
          P("Evans, R., &amp; Gao, J. (2016). <i>DeepMind AI reduces Google data centre cooling bill by 40%</i>. Google DeepMind. https://deepmind.google/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/"),
          P("Google. (s. f.). <i>Use eco-friendly routes on your Google Maps app</i>. Google Maps Help. https://support.google.com/maps/answer/11470237"),
          *declaracion()]
    Reporte(BASE / "Act1" / "FIA_G172_GUZMAN_S1.pdf", "Act1 · Sección 1").build(s)


def leer_resultados(act: int) -> dict:
    return json.loads((BASE / f"Act{act}" / "resultados" / f"act{act}_resultados.json").read_text(encoding="utf-8"))


def act2() -> None:
    d = leer_resultados(2); e, r = d["evacuacion"], d["reparto"]
    s = portada(2, "Problemas y espacios de búsqueda", "18")
    s += [H("Planteamiento"),
          P("Se modelan dos situaciones didácticas independientes. Los vértices son estados "
            "y las aristas son acciones legales. Los datos del mapa se inventaron con fines "
            "pedagógicos y no representan una instalación o ciudad reales."),
          H("Problema A: evacuación con mínimo número de pasos"),
          P("<b>Estado:</b> ubicación actual (aula, pasillo, laboratorio, patio, etc.). "
            "<b>Inicio:</b> Aula. <b>Meta:</b> Salida. <b>Acción:</b> pasar a una ubicación "
            "adyacente. <b>Costo:</b> una acción por arista. <b>Algoritmo:</b> búsqueda "
            "en anchura (BFS) con cola FIFO y conjunto de visitados. BFS encuentra un "
            "camino con mínimo número de aristas en grafos no ponderados."),
          P(f"<b>Solución:</b> {' → '.join(e['camino'])}; {e['pasos']} pasos, "
            f"{e['nodos_expandidos']} nodos expandidos de {e['estados']} estados."),
          foto(BASE / "Act2" / "resultados" / "act2_evacuacion.png", 15.5*cm),
          H("Problema B: reparto con costo de traslado"),
          P("<b>Estado:</b> punto actual de la red. <b>Inicio:</b> Almacen. "
            "<b>Meta:</b> Clinica. <b>Acción:</b> circular por una vía adyacente. "
            "<b>Costo:</b> valor no negativo de cada arista (unidades de recorrido "
            "simuladas). <b>Algoritmo:</b> Dijkstra o búsqueda de costo uniforme, "
            "con cola de prioridad y relajación de distancias."),
          P(f"<b>Solución:</b> {' → '.join(r['camino'])}; costo {r['costo']:g} "
            f"unidades y {r['nodos_expandidos']} nodos expandidos."),
          foto(BASE / "Act2" / "resultados" / "act2_reparto.png", 15.5*cm),
          H("Procedimiento y complejidad"),
          tabla(["Problema", "Estructura", "Tiempo", "Memoria"], [
              ["Evacuación / BFS", "Cola FIFO + padres", "O(V + E)", "O(V)"],
              ["Reparto / Dijkstra", "Montículo + distancias", "O((V + E) log V)", "O(V + E)"],
          ], [3.75*cm, 5.2*cm, 3.9*cm, 3.85*cm]),
          P("V es el número de estados y E el de aristas. Los límites consideran listas de "
            "adyacencia; el orden alfabético de vecinos usado para reproducibilidad agrega "
            "trabajo de ordenación en esta implementación. En reparto hay dos caminos "
            "óptimos de costo 8; se muestra el que produce el desempate determinista."),
          H("Código y verificación"),
          P("El código ejecutable y comentado está en <b>Act2/act2_grafos.py</b>. "
            "Implementa `bfs`, `dijkstra`, `construir_grafos` y exporta diagramas y JSON. "
            "La prueba `test_reparto_optimo` comprueba costo y ruta; `test_evacuacion_optima` "
            "comprueba tres pasos, inicio y meta. Ejecutar desde la raíz: "
            "<font name='Courier'>python Act2/act2_grafos.py</font>."),
          H("Conclusión"),
          P("La formulación del costo decide qué camino es mejor: BFS minimiza acciones "
            "cuando todas valen lo mismo; Dijkstra minimiza costo acumulado con pesos "
            "no negativos. Un modelo equivocado del costo puede producir una ruta "
            "matemáticamente óptima pero inútil para la operación real."),
          *referencias_comunes(), *declaracion(), *anexo_codigo(2, "act2_grafos.py")]
    Reporte(BASE / "Act2" / "FIA_G172_GUZMAN_S2.pdf", "Act2 · Sección 2").build(s)


def act3() -> None:
    d = leer_resultados(3); ej = d["ejemplo"]; comp = d["30_inicios"]
    s = portada(3, "Búsqueda local y optimización", "22")
    s += [H("Enunciado y función objetivo"),
          P("Minimizar una función real de dos variables sobre [-5.12, 5.12]². "
            "Se usa Rastrigin como paisaje de prueba multimodal: "
            "<b>f(x,y) = 20 + x² + y² − 10[cos(2πx) + cos(2πy)]</b>. "
            "Su mínimo global conocido es f(0,0)=0. Es un problema matemático "
            "didáctico, no un caso empresarial real. La vecindad de Hill Climbing "
            "son los cuatro puntos a distancia 0.1 por eje."),
          H("Métodos y parámetros"),
          tabla(["Método", "Regla", "Parámetros"], [
              ["Hill Climbing", "Elige el mejor vecino si mejora; termina si no mejora.", "Paso 0.1; máximo 500 iteraciones."],
              ["Simulated Annealing", "Acepta empeoramiento con probabilidad exp(-Δ/T); registra el mejor visto.", "T inicial 10; T←0.995T; 2000 iteraciones; ruido gaussiano σ=0.25."],
          ], [3.3*cm, 7.6*cm, 5.8*cm]),
          P("Ambos métodos aplican límites al dominio. El experimento de convergencia "
            "comienza en (3.8, 3.8), con semilla 42 para recocido simulado. "
            "La comparación adicional usa 30 puntos iniciales generados con semillas 0–29; "
            "el recocido usa la misma semilla de cada corrida."),
          H("Resultados reproducibles"),
          tabla(["Medida", "Hill Climbing", "Simulated Annealing"], [
              ["Inicio (3.8, 3.8): f final", f"{ej['hill_climbing']['valor']:.4f}", f"{ej['simulated_annealing']['valor']:.4f}"],
              ["Iteraciones del ejemplo", str(ej['hill_climbing']['iteraciones']), str(ej['simulated_annealing']['iteraciones'])],
              ["Media de f final, 30 inicios", f"{comp['media_hc']:.4f}", f"{comp['media_sa']:.4f}"],
              ["Corridas con f < 1, de 30", str(comp['exitos_hc_f_menor_1']), str(comp['exitos_sa_f_menor_1'])],
          ], [6.2*cm, 5.25*cm, 5.25*cm]),
          foto(BASE / "Act3" / "resultados" / "act3_convergencia.png", 14.2*cm),
          P("La gráfica registra el mejor valor encontrado, no el estado instantáneo del "
            "recocido. Por eso ambas curvas son no crecientes aunque el recocido acepte "
            "pasos temporales de mayor costo."),
          H("Código, verificación y complejidad"),
          P("<b>Act3/act3_optimizacion.py</b> incluye `objetivo`, `hill_climbing`, "
            "`simulated_annealing` y la exportación de resultados. Cada evaluación "
            "de f es O(1); HC usa hasta O(4I) evaluaciones con memoria O(I) para el "
            "historial, y SA usa O(I) tiempo y O(I) memoria por su historial. "
            "Sin guardar gráficas, la memoria de optimización sería O(1). "
            "Las pruebas comprueban f(0,0)=0 y que ambos métodos conservan una "
            "solución no peor que la inicial."),
          H("Conclusiones y límites"),
          P("En esta configuración el recocido obtuvo menor valor medio, pero no alcanzó "
            "el mínimo global en la mayoría de corridas. Hill Climbing quedó atrapado "
            "cerca de mínimos locales por la vecindad fija. El resultado depende de "
            "parámetros, presupuesto de evaluaciones y semilla; 30 corridas son una "
            "comparación exploratoria, no una garantía general."),
          H("Referencias (APA 7.ª ed.)"),
          P("Russell, S., &amp; Norvig, P. (2020). <i>Artificial intelligence: A modern approach</i> (4th ed.). Pearson."),
          P("Wirsansky, E. (2020). <i>Hands-on genetic algorithms with Python</i>. Packt. [Referencia del temario; no se implementan algoritmos genéticos en esta actividad]."),
          *declaracion(), *anexo_codigo(3, "act3_optimizacion.py")]
    Reporte(BASE / "Act3" / "FIA_G172_GUZMAN_S3.pdf", "Act3 · Sección 3").build(s)


def act4() -> None:
    d = leer_resultados(4); b, f = d["BFS"], d["DFS"]
    s = portada(4, "Búsqueda ciega: BFS y DFS", "25")
    s += [H("Planteamiento y representación"),
          P("Resolver un laberinto didáctico de 7 × 10 celdas. `#` es pared, `S` inicio "
            "y `G` meta. Cada celda libre es un estado (fila, columna); las acciones "
            "legales mueven arriba, abajo, izquierda o derecha a una celda libre, "
            "con costo 1. El grafo es no dirigido y no ponderado. Se construyó "
            f"con {d['estados_libres']} estados y {d['aristas']} aristas."),
          foto(BASE / "Act4" / "resultados" / "act4_rutas.png", 13.5*cm),
          H("Procedimiento"),
          P("BFS usa una cola FIFO y descubre estados por distancia creciente; DFS "
            "usa una pila LIFO y profundiza en una rama. Ambos registran padres al "
            "descubrir un estado para reconstruir la ruta y evitan ciclos con visitados. "
            "El orden de vecinos se fija por (fila, columna); DFS extrae primero "
            "el vecino mayor de la pila. Cada algoritmo termina al extraer la meta."),
          H("Resultados de la ejecución"),
          tabla(["Métrica", "BFS", "DFS"], [
              ["Longitud de ruta", f"{b['pasos']} pasos", f"{f['pasos']} pasos"],
              ["Nodos expandidos", str(b['nodos_expandidos']), str(f['nodos_expandidos'])],
              ["Máximo en frontera", str(b['max_frontera']), str(f['max_frontera'])],
              ["Tiempo (una ejecución)", f"{b['tiempo_microsegundos_una_ejecucion']:.1f} µs", f"{f['tiempo_microsegundos_una_ejecucion']:.1f} µs"],
          ], [6*cm, 5.35*cm, 5.35*cm]),
          P("El tiempo es una sola medición con reloj de alta resolución y cambia entre "
            "equipos y ejecuciones; la longitud de ruta y nodos expandidos son las "
            "medidas más útiles para comparar este ejemplo. BFS garantiza ruta mínima "
            "con costo uniforme; DFS depende del orden y aquí encuentra una más larga."),
          H("Grafo de estados"), foto(BASE / "Act4" / "resultados" / "act4_grafo.png", 12*cm),
          H("Complejidad y código"),
          P("En el grafo finito explícito, ambos recorren como máximo V estados y E "
            "aristas: O(V+E) tiempo y O(V) memoria por padres y frontera. La versión "
            "clásica en árbol se expresa como BFS O(b^d) tiempo/memoria y DFS "
            "O(b^m) tiempo, O(bm) memoria, con factor de ramificación b, profundidad "
            "óptima d y profundidad máxima m. El código está en "
            "<b>Act4/act4_laberinto.py</b>; las pruebas verifican adyacencia de cada "
            "paso, inicio, meta y que BFS no es más largo que DFS."),
          H("Conclusión"),
          P("BFS conviene si importa la ruta más corta y la memoria disponible alcanza; "
            "DFS puede ser útil para explorar con una pila, pero no garantiza la "
            "solución mínima. La selección del algoritmo debe responder a la meta "
            "real, al tamaño del espacio y al costo de las acciones."),
          *referencias_comunes(), *declaracion(), *anexo_codigo(4, "act4_laberinto.py")]
    Reporte(BASE / "Act4" / "FIA_G172_GUZMAN_S4.pdf", "Act4 · Sección 4").build(s)


def act5() -> None:
    d = leer_resultados(5)
    dij, ast = d["resultados"]["Dijkstra"], d["resultados"]["A*"]
    s = portada(5, "Búsqueda heurística en una red vial", "25", equipo=True)
    s += [H("Planteamiento y datos"),
          P("Caso académico: hallar una ruta peatonal entre dos nodos de la red vial de Atlautla, "
            "Estado de México. Las calles y coordenadas provienen de una instantánea de "
            "OpenStreetMap; la necesidad de viaje y sus extremos son un escenario hipotético. "
            "No es una indicación de navegación real ni garantiza accesibilidad o seguridad."),
          P(f"El grafo no dirigido conexo contiene {d['nodos']} intersecciones/nodos y "
            f"{d['aristas']} segmentos. Cada arista pesa su longitud geodésica aproximada "
            "en metros. Inicio: nodo " + d['inicio']['id'] + "; meta: nodo " + d['meta']['id'] + ". "
            "Se eligió el inicio próximo a una coordenada de referencia del campus y la meta "
            "como el nodo más distante en línea recta dentro del recorte."),
          H("Formulación y método"),
          P("Estado: nodo vial actual. Acción: avanzar a un nodo adyacente. Costo: longitud "
            "del segmento. Objetivo: minimizar la suma de longitudes hasta la meta. "
            "Dijkstra prioriza g(n), el costo recorrido; A* prioriza f(n)=g(n)+h(n). "
            "Se usó h(n)=0.999·d<sub>Haversine</sub>(n,meta). El factor 0.999 compensa "
            "el redondeo de pesos a milímetros. En cada arista, la distancia geodésica "
            "directa no supera la longitud del tramo; con ese factor, h es consistente "
            "y admisible en la instantánea almacenada."),
          H("Procedimiento reproducible"),
          P("1) Descargar la caja geográfica mediante <b>Act5/obtener_red_osm.py</b> "
            "(la instantánea JSON ya se incluye). 2) Filtrar vías caminables y conservar "
            "la componente conexa mayor. 3) Ejecutar ambos algoritmos con los mismos extremos. "
            "4) Registrar ruta, distancia, estados expandidos, frontera y mediana de 50 "
            "ejecuciones en milisegundos. 5) Comparar sobre el mismo mapa. "
            "Ejecutar: <font name='Courier'>python Act5/act5_rutas.py</font>."),
          tabla(["Métrica", "Dijkstra", "A*"], [
              ["Longitud (m)", f"{dij['distancia_m']:.3f}", f"{ast['distancia_m']:.3f}"],
              ["Nodos expandidos", str(dij['nodos_expandidos']), str(ast['nodos_expandidos'])],
              ["Frente máximo", str(dij['max_frontera']), str(ast['max_frontera'])],
              ["Mediana de 50 tiempos (ms)", f"{dij['tiempo_mediana_ms_50']:.4f}",
               f"{ast['tiempo_mediana_ms_50']:.4f}"],
          ], [7*cm, 4.8*cm, 4.8*cm]),
          P("Ambos algoritmos obtuvieron exactamente el mismo costo en este caso. A* "
            "expandió menos estados, pero aquí su cálculo de la heurística elevó el "
            "tiempo mediano. Los tiempos dependen del equipo y no son una promesa de "
            "ventaja universal."),
          H("Mapa y tablero"), foto(BASE / "Act5" / "resultados" / "act5_rutas.png", 15*cm),
          P("El tablero interactivo Plotly se encuentra en <b>Act5/dashboard.html</b>. "
            "La interfaz principal del repositorio permite cambiar los extremos y repetir "
            "la comparación en el navegador. El código Python está comentado y se anexa."),
          foto(BASE / "Act5" / "resultados" / "act5_comparacion.png", 10*cm),
          H("Complejidad y límites"),
          P("Con listas de adyacencia y montículo, la cota usual de ambos métodos es "
            "O((V+E) log V) en tiempo y O(V+E) en memoria. A* puede expandir menos "
            "estados si la heurística es informativa, pero su costo de evaluación importa. "
            "La red omitió restricciones de sentido y accesibilidad; se modeló como no dirigida."),
          H("Conclusión"),
          P("La heurística admisible mantuvo la ruta óptima y redujo expansiones en esta "
            "instancia. Para una aplicación de transporte real harían falta velocidades, "
            "sentidos de circulación, cierres y validación de campo."),
          H("Referencias (APA 7.ª ed.)"),
          P("OpenStreetMap contributors. (2026). <i>OpenStreetMap</i> [datos geográficos]. "
            "https://www.openstreetmap.org/copyright"),
          P("NetworkX developers. (s. f.). <i>Shortest paths</i>. "
            "https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html"),
          P("Russell, S., &amp; Norvig, P. (2020). <i>Artificial intelligence: A modern approach</i> (4th ed.). Pearson."),
          *declaracion(), *anexo_codigo(5, "act5_rutas.py")]
    Reporte(BASE / "Act5" / "FIA_G172_GUZMAN_S5.pdf", "Act5 · Sección 5").build(s)


def act6() -> None:
    d = leer_resultados(6)
    p = d["parametros"]
    s = portada(6, "Algoritmo genético para distribución", "26", equipo=True)
    s += [H("Caso y formulación"),
          P("Se simula una brigada de entrega de materiales educativos en Atlautla: sale "
            "de una base, visita ocho puntos y regresa. Las calles son datos reales de "
            "OpenStreetMap y los puntos de entrega son hipotéticos, seleccionados con "
            "semilla fija. No se describen entregas, clientes ni direcciones reales."),
          P("Cada cromosoma es una permutación de los índices 1 a 8; la base ocupa "
            "el índice 0 y se añade al inicio y final del circuito. La aptitud a minimizar "
            "es la suma de las distancias viales mínimas entre paradas consecutivas. "
            "La matriz se precalcula con Dijkstra sobre la red incluida en Act5."),
          H("Implementación con DEAP"),
          tabla(["Parámetro", "Valor"], [
              ["Población", str(p['poblacion'])], ["Generaciones", str(p['generaciones'])],
              ["Semilla", str(p['semilla'])], ["Selección", p['seleccion']],
              ["Cruce", f"{p['cruce']} (p={p['prob_cruce']})"],
              ["Mutación", f"{p['mutacion']} (p={p['prob_mutacion']}; gen={p['prob_gen_mutacion']})"],
              ["Elitismo", str(p['elitismo'])],
          ], [7*cm, 9.6*cm]),
          P("Procedimiento: generar 80 permutaciones, evaluar costos, conservar dos élites, "
            "seleccionar por torneo de tres, cruzar con operador ordenado, mutar "
            "permutando posiciones y repetir 30 generaciones. El mejor histórico y la "
            "media se registran desde la generación 0. El cruce conserva la validez "
            "de las permutaciones."),
          H("Resultados y control"),
          tabla(["Método", "Distancia del circuito"], [
              ["Algoritmo genético DEAP", f"{d['distancia_ga_m']:.3f} m"],
              ["Vecino más cercano", f"{d['distancia_vecino_cercano_m']:.3f} m"],
              ["Óptimo exacto Held-Karp", f"{d['distancia_optima_control_m']:.3f} m"],
              ["Brecha del AG contra óptimo", f"{d['brecha_optima_pct']:.2f} %"],
          ], [8.3*cm, 8.3*cm]),
          P("Orden del AG: Base → " + " → ".join(map(str, d['ruta_ga'])) + " → Base. "
            "Held-Karp se utilizó como control exacto para esta instancia pequeña, no "
            "como componente del algoritmo genético. Una coincidencia con el óptimo en "
            "esta semilla no garantiza que el AG lo alcance en toda instancia."),
          foto(BASE / "Act6" / "resultados" / "act6_convergencia.png", 15*cm),
          foto(BASE / "Act6" / "resultados" / "act6_ruta.png", 14*cm),
          H("Reproducción y límites"),
          P("Instalar <font name='Courier'>pip install -r requirements.txt</font> y ejecutar "
            "<font name='Courier'>python Act6/act6_genetico.py</font> desde la raíz. "
            "El archivo <b>Act6/resultados/act6_resultados.json</b> conserva matriz, "
            "parámetros, ruta e historia completos. La interfaz HTML permite repetir "
            "una simulación genética en el navegador; la implementación evaluada usa DEAP."),
          H("Conclusión"),
          P("La búsqueda evolutiva redujo el recorrido frente a vecino más cercano y "
            "alcanzó el costo exacto de control en este ejemplo. Para adoptar el modelo "
            "en una empresa o programa social se necesitarían horarios, capacidad, "
            "costos de operación, restricciones reales y protección de datos."),
          H("Referencias (APA 7.ª ed.)"),
          P("Fortin, F.-A., De Rainville, F.-M., Gardner, M.-A., Parizeau, M., &amp; "
            "Gagné, C. (2012). DEAP: Evolutionary algorithms made easy. "
            "<i>Journal of Machine Learning Research, 13</i>, 2171–2175."),
          P("OpenStreetMap contributors. (2026). <i>OpenStreetMap</i> [datos geográficos]. "
            "https://www.openstreetmap.org/copyright"),
          P("Wirsansky, E. (2020). <i>Hands-on genetic algorithms with Python</i>. Packt Publishing."),
          *declaracion(), *anexo_codigo(6, "act6_genetico.py")]
    Reporte(BASE / "Act6" / "FIA_G172_GUZMAN_S6.pdf", "Act6 · Sección 6").build(s)


if __name__ == "__main__":
    for funcion in (act1, act2, act3, act4, act5, act6):
        funcion()
    print("Se generaron seis reportes PDF.")
