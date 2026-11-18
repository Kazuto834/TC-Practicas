"""
gg Módulo Principal de Integración — Suite de Teoría de la Computación (Prácticas 1, 2, 3 y 4).
Optimizado para entorno Docker con flet[web]==0.86.5.
Incluye renderizado gráfico vectorial de autómatas (Canvas), tabla de transiciones (DataTable)
y carga limpia de archivos .jff / .json / .xml sin mostrar código XML crudo.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)
"""

from __future__ import annotations
import math
import os
import json
import tempfile
import flet as ft
import flet.canvas as cv

# Directorio temporal dentro del contenedor para no ensuciar el volumen montado
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "flet_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Módulos Práctica 1
from lenguajes import (
    prefijos,
    sufijos,
    subcadenas,
    cerradura_Kleene,
    cerradura_positiva,
)

# Módulos Práctica 2
from automata import Automata
from formatos import FormatosAutomata
from gui_simulador import crear_vista_simulador

# Módulos Práctica 3 y Teorema de Kleene / Minimización
from algoritmos_afn import (
    calcular_cerradura_lambda,
    simular_afn_lambda_directo,
    transformar_afn_sin_lambda_detallado,
    construccion_subconjuntos_detallada,
)
from eliminacion_inaccesibles import eliminar_estados_inaccesibles_detallado
from equivalencia_afd import decidir_equivalencia_detallada

try:
    from minimizacion import minimizar_afd
except ImportError:
    from minimizacion_afd import minimizar_afd

try:
    from er_a_automata import er_a_afnd_lambda as er_a_automata
except ImportError:
    try:
        from er_a_automata import er_a_automata
    except ImportError:
        er_a_automata = None

try:
    from automata_a_er import automata_a_expresion_regular
except ImportError:
    automata_a_expresion_regular = None

# Módulos Práctica 4
from vista_practica4 import crear_vista_practica4


# =====================================================================
# UTILIDADES GLOBALES Y RENDERIZADO VISUAL DE AUTÓMATAS
# =====================================================================

def notificar(page: ft.Page, mensaje: str, es_error: bool = False) -> None:
    """Muestra un SnackBar seguro en Flet Web 0.86.5 sin crasheos."""
    try:
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700,
            duration=3500,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
    except Exception:
        pass


def construir_grafo_automata_canvas(
    auto: Automata,
    titulo: str = "Diagrama de Estados",
    ancho: float = 640,
    alto: float = 320,
) -> ft.Control:
    """
    Dibuja de forma gráfica (vectorial) un objeto Automata usando flet.canvas.Canvas
    compatible con Flet 0.86.5 (usando `value=` en cv.Text).
    """
    estados = sorted(list(auto.estados))
    if not estados:
        return ft.Container(
            padding=16,
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Text("Sin estados para graficar.", color=ft.Colors.GREY_400),
        )

    n = len(estados)
    cx, cy = ancho / 2.0, alto / 2.0 + 10.0
    radio_layout = min(ancho, alto) * (0.34 if n > 1 else 0.0)
    radio_nodo = 24.0 if n <= 7 else (20.0 if n <= 12 else 16.0)

    posiciones: dict[str, tuple[float, float]] = {}
    for i, q in enumerate(estados):
        if n == 1:
            posiciones[q] = (cx, cy)
        else:
            ang = -math.pi / 2.0 + (2.0 * math.pi * i) / n
            posiciones[q] = (cx + radio_layout * math.cos(ang), cy + radio_layout * math.sin(ang))

    # Agrupar símbolos por par (origen, destino)
    aristas: dict[tuple[str, str], list[str]] = {}
    for t in auto.transiciones:
        etq = t.simbolo if t.simbolo else "λ"
        aristas.setdefault((t.origen, t.destino), [])
        if etq not in aristas[(t.origen, t.destino)]:
            aristas[(t.origen, t.destino)].append(etq)

    shapes: list[cv.Shape] = []

    pincel_arista = ft.Paint(
        color=ft.Colors.BLUE_GREY_200,
        stroke_width=1.8,
        style=ft.PaintingStyle.STROKE,
    )
    pincel_flecha = ft.Paint(
        color=ft.Colors.BLUE_GREY_200,
        style=ft.PaintingStyle.FILL,
    )
    pincel_inicio = ft.Paint(
        color=ft.Colors.GREEN_400,
        stroke_width=2.2,
        style=ft.PaintingStyle.STROKE,
    )
    pincel_inicio_fill = ft.Paint(
        color=ft.Colors.GREEN_400,
        style=ft.PaintingStyle.FILL,
    )

    def dibujar_punta_flecha(px: float, py: float, angulo: float, paint_fill: ft.Paint):
        tam = 8.5
        a1 = angulo + math.radians(152)
        a2 = angulo - math.radians(152)
        p1 = (px + tam * math.cos(a1), py + tam * math.sin(a1))
        p2 = (px + tam * math.cos(a2), py + tam * math.sin(a2))
        shapes.append(
            cv.Path(
                elements=[
                    cv.Path.MoveTo(px, py),
                    cv.Path.LineTo(p1[0], p1[1]),
                    cv.Path.LineTo(p2[0], p2[1]),
                    cv.Path.Close(),
                ],
                paint=paint_fill,
            )
        )

    # 1. Dibujar transiciones (aristas)
    for (orig, dest), simbs in aristas.items():
        if orig not in posiciones or dest not in posiciones:
            continue
        etiqueta = ", ".join(sorted(simbs))
        x1, y1 = posiciones[orig]
        x2, y2 = posiciones[dest]

        if orig == dest:
            vx, vy = x1 - cx, y1 - cy
            norm = math.hypot(vx, vy)
            if norm < 1e-3:
                ux, uy = 0.0, -1.0
            else:
                ux, uy = vx / norm, vy / norm

            ang_centro = math.atan2(uy, ux)
            a_ini = ang_centro - 0.45
            a_fin = ang_centro + 0.45

            sx = x1 + radio_nodo * math.cos(a_ini)
            sy = y1 + radio_nodo * math.sin(a_ini)
            ex = x1 + radio_nodo * math.cos(a_fin)
            ey = y1 + radio_nodo * math.sin(a_fin)

            dist_ctrl = radio_nodo + 36.0
            c1x = x1 + dist_ctrl * math.cos(ang_centro - 0.55)
            c1y = y1 + dist_ctrl * math.sin(ang_centro - 0.55)
            c2x = x1 + dist_ctrl * math.cos(ang_centro + 0.55)
            c2y = y1 + dist_ctrl * math.sin(ang_centro + 0.55)

            shapes.append(
                cv.Path(
                    elements=[
                        cv.Path.MoveTo(sx, sy),
                        cv.Path.CubicTo(c1x, c1y, c2x, c2y, ex, ey),
                    ],
                    paint=pincel_arista,
                )
            )
            ang_punta = math.atan2(ey - c2y, ex - c2x)
            dibujar_punta_flecha(ex, ey, ang_punta, pincel_flecha)

            lx = x1 + (radio_nodo + 34.0) * ux
            ly = y1 + (radio_nodo + 34.0) * uy
            shapes.append(
                cv.Text(
                    x=lx,
                    y=ly,
                    value=etiqueta,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.AMBER_300,
                    ),
                )
            )
        else:
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist < 1e-3:
                continue
            ux, uy = dx / dist, dy / dist
            nx, ny = -uy, ux

            tiene_inversa = (dest, orig) in aristas
            curvatura = 26.0 if tiene_inversa else 0.0

            mx = (x1 + x2) / 2.0 + nx * curvatura
            my = (y1 + y2) / 2.0 + ny * curvatura

            ang_sal = math.atan2(my - y1, mx - x1)
            ang_ent = math.atan2(y2 - my, x2 - mx)

            sx = x1 + radio_nodo * math.cos(ang_sal)
            sy = y1 + radio_nodo * math.sin(ang_sal)
            ex = x2 - radio_nodo * math.cos(ang_ent)
            ey = y2 - radio_nodo * math.sin(ang_ent)

            if tiene_inversa:
                shapes.append(
                    cv.Path(
                        elements=[
                            cv.Path.MoveTo(sx, sy),
                            cv.Path.QuadraticTo(mx, my, ex, ey),
                        ],
                        paint=pincel_arista,
                    )
                )
            else:
                shapes.append(cv.Line(sx, sy, ex, ey, paint=pincel_arista))

            dibujar_punta_flecha(ex, ey, ang_ent, pincel_flecha)

            lx = (sx + 2 * mx + ex) / 4.0 + nx * 12.0
            ly = (sy + 2 * my + ey) / 4.0 + ny * 12.0
            shapes.append(
                cv.Text(
                    x=lx,
                    y=ly,
                    value=etiqueta,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.AMBER_300,
                    ),
                )
            )

    # 2. Flecha de estado inicial q0
    if auto.estado_inicial and auto.estado_inicial in posiciones:
        ix, iy = posiciones[auto.estado_inicial]
        vx, vy = ix - cx, iy - cy
        norm = math.hypot(vx, vy)
        if norm < 1e-3:
            ux, uy = -1.0, 0.0
        else:
            ux, uy = vx / norm, vy / norm

        punta_x = ix + radio_nodo * ux
        punta_y = iy + radio_nodo * uy
        cola_x = ix + (radio_nodo + 30.0) * ux
        cola_y = iy + (radio_nodo + 30.0) * uy

        shapes.append(cv.Line(cola_x, cola_y, punta_x, punta_y, paint=pincel_inicio))
        dibujar_punta_flecha(punta_x, punta_y, math.atan2(punta_y - cola_y, punta_x - cola_x), pincel_inicio_fill)

    # 3. Nodos (estados)
    for q in estados:
        px, py = posiciones[q]
        es_ini = (q == auto.estado_inicial)
        es_fin = (q in auto.estados_aceptacion)

        color_borde = (
            ft.Colors.AMBER_400 if (es_ini and es_fin)
            else ft.Colors.GREEN_400 if es_ini
            else ft.Colors.BLUE_400 if es_fin
            else ft.Colors.BLUE_GREY_300
        )

        shapes.append(
            cv.Circle(
                x=px,
                y=py,
                radius=radio_nodo,
                paint=ft.Paint(color="#1E2430", style=ft.PaintingStyle.FILL),
            )
        )
        shapes.append(
            cv.Circle(
                x=px,
                y=py,
                radius=radio_nodo,
                paint=ft.Paint(color=color_borde, stroke_width=2.4, style=ft.PaintingStyle.STROKE),
            )
        )
        if es_fin:
            shapes.append(
                cv.Circle(
                    x=px,
                    y=py,
                    radius=radio_nodo - 4.5,
                    paint=ft.Paint(color=color_borde, stroke_width=1.5, style=ft.PaintingStyle.STROKE),
                )
            )

        etiqueta_nodo = q if len(q) <= 8 else (q[:7] + "…")
        shapes.append(
            cv.Text(
                x=px,
                y=py,
                value=etiqueta_nodo,
                alignment=ft.Alignment.CENTER,
                style=ft.TextStyle(
                    size=11 if len(etiqueta_nodo) > 4 else 12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            )
        )

    leyenda = ft.Row(
        [
            ft.Text(titulo, weight=ft.FontWeight.BOLD, size=14),
            ft.Row(
                [
                    ft.Text("→ Inicio (q0)", size=11, color=ft.Colors.GREEN_400),
                    ft.Text("◎ Aceptación (F)", size=11, color=ft.Colors.BLUE_400),
                ],
                spacing=12,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        spacing=12,
    )

    return ft.Container(
        padding=12,
        border_radius=8,
        bgcolor="#141821",
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Column(
            [
                leyenda,
                ft.Row(
                    [cv.Canvas(shapes=shapes, width=ancho, height=alto)],
                    scroll=ft.ScrollMode.AUTO,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=6,
        ),
    )


def construir_tabla_transiciones_visual(
    auto: Automata,
    titulo: str = "Tabla de Transiciones (δ)",
) -> ft.Control:
    """Construye un DataTable formal de la función de transición δ(q, a)."""
    estados = sorted(list(auto.estados))
    if not estados:
        return ft.Container()

    tiene_lambda = any(t.es_lambda() for t in auto.transiciones)
    simbolos = sorted([s for s in auto.alfabeto if s != ""])
    if tiene_lambda:
        simbolos.append("")

    columnas = [
        ft.DataColumn(ft.Text("Estado (Q)", weight=ft.FontWeight.BOLD)),
    ]
    for s in simbolos:
        encabezado = s if s != "" else "λ"
        columnas.append(ft.DataColumn(ft.Text(encabezado, weight=ft.FontWeight.BOLD)))

    tabla = auto.obtener_tabla_transiciones()
    filas: list[ft.DataRow] = []

    for q in estados:
        prefijo = ""
        if q == auto.estado_inicial:
            prefijo += "→ "
        if q in auto.estados_aceptacion:
            prefijo += "* "

        celdas = [
            ft.DataCell(
                ft.Text(
                    f"{prefijo}{q}",
                    weight=ft.FontWeight.BOLD,
                    font_family="monospace",
                    color=ft.Colors.GREEN_300 if q == auto.estado_inicial else None,
                )
            )
        ]

        for s in simbolos:
            dests = sorted(list(tabla.get(q, {}).get(s, set())))
            if not dests:
                val = "∅"
            elif auto.tipo == "AFD" and len(dests) == 1:
                val = dests[0]
            else:
                val = "{" + ", ".join(dests) + "}"
            celdas.append(ft.DataCell(ft.Text(val, font_family="monospace")))

        filas.append(ft.DataRow(cells=celdas))

    q_str = "{" + ", ".join(estados) + "}"
    sig_str = "{" + ", ".join([s for s in simbolos if s != ""]) + "}"
    f_str = "{" + ", ".join(sorted(list(auto.estados_aceptacion))) + "}"

    return ft.Container(
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(titulo, weight=ft.FontWeight.BOLD, size=14),
                        ft.Container(expand=True),
                        ft.Text(f"Tipo: {auto.tipo}", size=12, color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Text(
                    f"Q = {q_str}  |  Σ = {sig_str}  |  q0 = {auto.estado_inicial or '∅'}  |  F = {f_str}",
                    size=12,
                    font_family="monospace",
                    color=ft.Colors.GREY_300,
                    selectable=True,
                ),
                ft.Row(
                    [
                        ft.DataTable(
                            columns=columnas,
                            rows=filas,
                            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                            border_radius=6,
                            vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                            horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                            heading_row_height=38,
                            data_row_min_height=34,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=8,
        ),
    )


def serializar_automata_texto(auto: Automata) -> str:
    """Convierte un objeto Automata a texto plano exclusivamente para descarga .TXT."""
    lineas = [
        f"Tipo: {auto.tipo}",
        f"Estados (Q): {{{', '.join(sorted(auto.estados))}}}",
        f"Alfabeto (Σ): {{{', '.join(sorted(auto.alfabeto))}}}",
        f"Estado Inicial (q0): {auto.estado_inicial}",
        f"Estados de Aceptación (F): {{{', '.join(sorted(auto.estados_aceptacion))}}}",
        "\nTabla de Transiciones (δ):",
    ]
    tabla = auto.obtener_tabla_transiciones()
    for origen in sorted(tabla.keys()):
        for simb, dests in sorted(tabla[origen].items()):
            etiqueta = simb if simb != "" else "λ"
            lineas.append(f"  δ({origen}, {etiqueta}) -> {{{', '.join(sorted(dests))}}}")
    return "\n".join(lineas)


def parsear_automata_desde_texto(contenido: str) -> Automata:
    """Construye un objeto Automata a partir de .jff, .xml, .json o texto plano."""
    contenido = contenido.strip()
    if not contenido:
        raise ValueError("El contenido del autómata está vacío.")

    if contenido.startswith("<"):
        if "<structure>" in contenido or "<automaton>" in contenido:
            return FormatosAutomata.cargar_jff(contenido)
        return FormatosAutomata.cargar_xml(contenido)

    if contenido.startswith("{"):
        data = json.loads(contenido)
        if any("desde" in t for t in data.get("transiciones", []) if isinstance(t, dict)):
            return FormatosAutomata.cargar_json(contenido)

        auto = Automata(
            alfabeto=set(data.get("alfabeto", [])),
            estados=set(data.get("estados", [])),
            estado_inicial=data.get("inicial") or data.get("estado_inicial"),
            estados_aceptacion=set(
                data.get("aceptacion") or data.get("finales") or data.get("estados_aceptacion", [])
            ),
        )
        for q in auto.estados:
            auto.agregar_estado(
                q,
                es_inicial=(q == auto.estado_inicial),
                es_final=(q in auto.estados_aceptacion),
            )
        for t in data.get("transiciones", []):
            if isinstance(t, dict):
                auto.agregar_transicion(t["origen"], t.get("simbolo", ""), t["destino"])
            elif isinstance(t, (list, tuple)) and len(t) == 3:
                auto.agregar_transicion(t[0], t[1], t[2])
        return auto

    auto = Automata()
    estados_declarados = []
    finales_declarados = set()
    inicial_declarado = None
    leyendo_transiciones = False

    for raw_line in contenido.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        lower = line.lower()
        if lower.startswith("estados:"):
            leyendo_transiciones = False
            estados_declarados = [x.strip() for x in line.split(":", 1)[1].split(",") if x.strip()]
        elif lower.startswith("alfabeto:"):
            leyendo_transiciones = False
            for s in line.split(":", 1)[1].split(","):
                s = s.strip()
                if s:
                    auto.agregar_simbolo(s)
        elif lower.startswith("inicial:"):
            leyendo_transiciones = False
            inicial_declarado = line.split(":", 1)[1].strip()
        elif lower.startswith("finales:") or lower.startswith("aceptacion:"):
            leyendo_transiciones = False
            finales_declarados = {x.strip() for x in line.split(":", 1)[1].split(",") if x.strip()}
        elif lower.startswith("transiciones:"):
            leyendo_transiciones = True
            resto = line.split(":", 1)[1].strip()
            if resto:
                line = resto
            else:
                continue

        if leyendo_transiciones or "->" in line:
            if "->" in line:
                izq, der = line.split("->", 1)
                partes_izq = [p.strip() for p in izq.split(",")]
                if len(partes_izq) != 2:
                    raise ValueError(f"Transición inválida: '{line}'. Usa 'origen, simbolo -> destino'")
                origen, simb = partes_izq
                destinos = [d.strip() for d in der.split(",") if d.strip()]
                for d in destinos:
                    auto.agregar_transicion(origen, simb, d)
            else:
                partes = [p.strip() for p in line.split(",")]
                if len(partes) == 3:
                    auto.agregar_transicion(partes[0], partes[1], partes[2])

    for q in estados_declarados:
        if q not in auto.estados:
            auto.estados.add(q)

    if inicial_declarado:
        auto.estado_inicial = inicial_declarado
        auto.estados.add(inicial_declarado)

    auto.estados_aceptacion.update(finales_declarados)
    auto.estados.update(finales_declarados)

    for q in auto.estados:
        auto.agregar_estado(
            q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in auto.estados_aceptacion),
        )

    valido, errores = auto.validar_consistencia()
    if not valido:
        raise ValueError(" ; ".join(errores))

    return auto


# =====================================================================
# VISTA 0: PANTALLA DE BIENVENIDA (SOLO TÍTULO Y AUTORES)
# =====================================================================

def crear_vista_bienvenida() -> ft.Control:
    """Portada limpia con el título de la materia y los autores."""
    return ft.Container(
        alignment=ft.Alignment.CENTER,
        expand=True,
        content=ft.Column(
            [
                ft.Container(
                    padding=18,
                    border_radius=60,
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE_400),
                    content=ft.Icon(ft.Icons.HUB, size=56, color=ft.Colors.BLUE_400),
                ),
                ft.Container(height=8),
                ft.Text(
                    "Teoría de la Computación",
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Suite Integrada de Prácticas (Prácticas 1, 2, 3 y 4)",
                    size=18,
                    color=ft.Colors.BLUE_300,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Escuela Superior de Cómputo (ESCOM) — Instituto Politécnico Nacional",
                    size=14,
                    color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                ft.Text(
                    "Autores: Antonio Navarro Domínguez & Mario García Castillo",
                    size=14,
                    color=ft.Colors.GREY_300,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                ft.Text(
                    "Selecciona una práctica en la barra inferior para comenzar.",
                    size=13,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
    )


# =====================================================================
# VISTA PRÁCTICA 1: OPERACIONES CON CADENAS Y ALFABETOS
# =====================================================================

def crear_vista_practica1(page: ft.Page) -> ft.Control:
    """Construye la vista de la Práctica 1 con descarga Web nativa para Flet 0.86.5."""

    texto_resultado = ft.Text(
        value="Selecciona una operación e ingresa los datos para calcular.",
        selectable=True,
        size=14,
    )

    exportar_dialogo = ft.FilePicker()
    page.services.append(exportar_dialogo)

    async def abrir_exportacion(e):
        try:
            contenido_bytes = (texto_resultado.value or "").encode("utf-8")
            await exportar_dialogo.save_file(
                dialog_title="Descargar resultados de Práctica 1",
                file_name="resultados_practica1.txt",
                src_bytes=contenido_bytes,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt"],
            )
            notificar(page, "Descarga iniciada en tu navegador.")
        except Exception as ex:
            notificar(page, f"Error al descargar archivo: {ex}", es_error=True)

    input_texto = ft.TextField(
        label="Cadena de texto (ej: abc)",
        hint_text="Ingresa la cadena o los símbolos separados por coma",
        prefix_icon=ft.Icons.TEXT_FIELDS,
        expand=True,
    )

    input_longitud = ft.TextField(
        label="Longitud Máxima (n)",
        hint_text="Ej: 3",
        prefix_icon=ft.Icons.NUMBERS,
        width=200,
        disabled=True,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    boton_exportar = ft.OutlinedButton(
        "Descargar TXT",
        icon=ft.Icons.DOWNLOAD,
        disabled=True,
        on_click=abrir_exportacion,
    )

    def cambiar_op(e):
        seleccion = e.control.value
        if seleccion in ("Cerradura de Kleene", "Cerradura Positiva"):
            input_longitud.disabled = False
            input_texto.label = "Alfabeto Σ (separado por comas, ej: 0, 1)"
            input_texto.hint_text = "0, 1"
        else:
            input_longitud.disabled = True
            input_longitud.value = ""
            input_texto.label = "Cadena de texto (ej: abc)"
            input_texto.hint_text = "abc"
        page.update()

    opciones_dropdown = ft.Dropdown(
        label="Operación sobre cadenas / lenguajes",
        width=320,
        options=[
            ft.dropdown.Option("Prefijos"),
            ft.dropdown.Option("Sufijos"),
            ft.dropdown.Option("Subcadenas"),
            ft.dropdown.Option("Cerradura de Kleene"),
            ft.dropdown.Option("Cerradura Positiva"),
        ],
        on_select=cambiar_op,
    )

    def mostrar_error(mensaje: str):
        texto_resultado.value = f"ERROR: {mensaje}"
        texto_resultado.color = ft.Colors.RED_400
        boton_exportar.disabled = True
        page.update()

    def calcular_res(e):
        op = opciones_dropdown.value
        texto = (input_texto.value or "").strip()
        texto_resultado.color = None

        if not op or not texto:
            mostrar_error("Selecciona una operación e ingresa la cadena o el alfabeto.")
            return

        try:
            if op == "Prefijos":
                res = prefijos(texto)
                resultado = f"Prefijos de '{texto}' ({len(res)}):\n{res}"
            elif op == "Sufijos":
                res = sufijos(texto)
                resultado = f"Sufijos de '{texto}' ({len(res)}):\n{res}"
            elif op == "Subcadenas":
                res = subcadenas(texto)
                resultado = f"Subcadenas de '{texto}' ({len(res)}):\n{res}"
            elif op in ("Cerradura de Kleene", "Cerradura Positiva"):
                alfabeto = [x.strip() for x in texto.split(",") if x.strip()]
                if not alfabeto:
                    mostrar_error("El alfabeto no es válido o está vacío.")
                    return
                try:
                    n = int(input_longitud.value)
                except (ValueError, TypeError):
                    mostrar_error("La longitud máxima debe ser un número entero.")
                    return
                if n < 0:
                    mostrar_error("La longitud máxima no puede ser negativa.")
                    return

                k = len(alfabeto)
                inicio = 0 if op == "Cerradura de Kleene" else 1
                total = sum(k ** i for i in range(inicio, n + 1))
                if total > 200000:
                    mostrar_error(
                        f"Se intentaron generar {total} combinaciones. El límite seguro es 200,000."
                    )
                    return

                res = cerradura_Kleene(alfabeto, n) if op == "Cerradura de Kleene" else cerradura_positiva(alfabeto, n)
                resultado = f"{op} Σ hasta longitud {n} ({len(res)} elementos):\n{res}"
            else:
                mostrar_error("Operación no reconocida.")
                return

            texto_resultado.value = resultado
            texto_resultado.color = ft.Colors.GREEN_400
            boton_exportar.disabled = False
        except Exception as ex:
            mostrar_error(f"Ocurrió un error al calcular: {ex}")
            return

        page.update()

    def limpiar_p1(e):
        input_texto.value = ""
        input_longitud.value = ""
        texto_resultado.value = "Selecciona una operación e ingresa los datos para calcular."
        texto_resultado.color = None
        boton_exportar.disabled = True
        page.update()

    return ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Icon(ft.Icons.CALCULATE, size=28, color=ft.Colors.BLUE_400),
                    ft.Column(
                        [
                            ft.Text("Práctica 1: Operaciones con Cadenas y Alfabetos", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Prefijos, sufijos, subcadenas, cerradura de Kleene (Σ*) y cerradura positiva (Σ+).", size=12, color=ft.Colors.GREY_400),
                        ],
                        spacing=2,
                    ),
                ]
            ),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        [
                            ft.Row([opciones_dropdown, input_longitud], wrap=True),
                            ft.Row([input_texto]),
                            ft.Row(
                                [
                                    ft.Button("Calcular", icon=ft.Icons.PLAY_ARROW, on_click=calcular_res),
                                    boton_exportar,
                                    ft.TextButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_p1),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=12,
                    ),
                )
            ),
            ft.Text("Resultado:", weight=ft.FontWeight.BOLD, size=14),
            ft.Container(
                content=ft.SelectionArea(
                    content=ft.Column([texto_resultado], scroll=ft.ScrollMode.AUTO)
                ),
                padding=16,
                border_radius=8,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            ),
        ],
        expand=True,
        spacing=12,
    )


# =====================================================================
# VISTA PRÁCTICA 3: VISUALIZACIÓN GRÁFICA + TABLA + CARGA LIMPIA DE ARCHIVOS
# =====================================================================

EJEMPLO_AFN_LAMBDA = """# Ejemplo AFND-lambda: acepta cadenas que terminan en 'ab' o tienen 'b' tras lambda
estados: q0, q1, q2, q3
alfabeto: a, b
inicial: q0
finales: q3
transiciones:
q0, lambda -> q1
q0, a -> q0
q1, b -> q2
q2, lambda -> q3
q3, a -> q3
q3, b -> q3
"""

EJEMPLO_AFD_EQUIV_2 = """# Segundo AFD para comparar equivalencia
estados: s0, s1, s2
alfabeto: a, b
inicial: s0
finales: s2
transiciones:
s0, a -> s0
s0, b -> s1
s1, a -> s2
s1, b -> s2
s2, a -> s2
s2, b -> s2
"""


def crear_vista_practica3(page: ft.Page) -> ft.Control:
    """
    Construye la interfaz de Práctica 3 con:
    - Carga limpia de archivos .jff / .json / .xml (oculta código XML crudo y muestra banner de archivo)
    - Vista previa gráfica en vivo (Canvas + DataTable) tanto de M1 como de M2
    - Renderizado gráfico y tabular del autómata resultante
    """
    ultimo_reporte_txt = {"contenido": ""}
    estado_archivos = {
        "m1_auto": None,
        "m1_nombre": None,
        "m2_auto": None,
        "m2_nombre": None,
    }

    # Banner limpio cuando M1 fue cargado desde archivo (evita mostrar XML crudo)
    txt_banner_m1 = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_200, expand=True)
    banner_archivo_m1 = ft.Container(
        visible=False,
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE_400),
        border=ft.Border.all(1, ft.Colors.BLUE_400),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=22),
                txt_banner_m1,
                ft.TextButton(
                    "Quitar archivo / Editar manual",
                    icon=ft.Icons.EDIT,
                    on_click=lambda _: limpiar_archivo_cargado(1),
                ),
            ],
            spacing=10,
        ),
    )

    # Banner limpio cuando M2 fue cargado desde archivo
    txt_banner_m2 = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_200, expand=True)
    banner_archivo_m2 = ft.Container(
        visible=False,
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_400),
        border=ft.Border.all(1, ft.Colors.PURPLE_400),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=22),
                txt_banner_m2,
                ft.TextButton(
                    "Quitar archivo M2",
                    icon=ft.Icons.EDIT,
                    on_click=lambda _: limpiar_archivo_cargado(2),
                ),
            ],
            spacing=10,
        ),
    )

    editor_automata_1 = ft.TextField(
        label="Definición Manual del Autómata Principal (M1)",
        value=EJEMPLO_AFN_LAMBDA.strip(),
        multiline=True,
        min_lines=7,
        max_lines=10,
        text_style=ft.TextStyle(font_family="monospace", size=13),
        expand=True,
    )

    editor_automata_2 = ft.TextField(
        label="Definición Manual del Segundo Autómata (M2 — Equivalencia AFD)",
        value=EJEMPLO_AFD_EQUIV_2.strip(),
        multiline=True,
        min_lines=7,
        max_lines=10,
        text_style=ft.TextStyle(font_family="monospace", size=13),
        visible=False,
        expand=True,
    )

    campo_parametro = ft.TextField(
        label="Estado específico (opcional, vacío = todos los estados)",
        hint_text="Ej: q0",
        prefix_icon=ft.Icons.INPUT,
        expand=True,
    )

    campo_er = ft.TextField(
        label="Expresión Regular (para conversión ER → Autómata)",
        hint_text="Ej: (a+b)*abb",
        prefix_icon=ft.Icons.FUNCTIONS,
        visible=False,
        expand=True,
    )

    contenedor_vista_previa = ft.Column(spacing=10)

    contenedor_resultados_p3 = ft.Column(
        controls=[
            ft.Text(
                "Selecciona un algoritmo de la Práctica 3 y presiona 'Ejecutar Algoritmo'.",
                size=14,
                color=ft.Colors.GREY_300,
            )
        ],
        spacing=14,
    )

    def obtener_automata_m1() -> Automata:
        if estado_archivos["m1_auto"] is not None:
            return estado_archivos["m1_auto"]
        return parsear_automata_desde_texto(editor_automata_1.value or "")

    def obtener_automata_m2() -> Automata:
        if estado_archivos["m2_auto"] is not None:
            return estado_archivos["m2_auto"]
        return parsear_automata_desde_texto(editor_automata_2.value or "")

    def actualizar_vista_previa_entrada(e=None):
        """Renderiza en vivo el diagrama gráfico y tabla de transiciones del autómata activo."""
        alg = selector_algoritmo.value
        if alg == "er_a_automata":
            contenedor_vista_previa.controls = []
            if e is not None:
                page.update()
            return

        bloques_previa: list[ft.Control] = []
        try:
            m1_preview = obtener_automata_m1()
            etiqueta_m1 = (
                f"M1 ({estado_archivos['m1_nombre']})"
                if estado_archivos["m1_nombre"]
                else "Autómata de Entrada (M1)"
            )
            bloques_previa.append(
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "lg": 7},
                            controls=[
                                construir_grafo_automata_canvas(
                                    m1_preview,
                                    titulo=f"Vista Gráfica — {etiqueta_m1}",
                                    ancho=620,
                                    alto=300,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "lg": 5},
                            controls=[
                                construir_tabla_transiciones_visual(
                                    m1_preview,
                                    titulo=f"Tabla δ — {etiqueta_m1}",
                                )
                            ],
                        ),
                    ],
                    spacing=12,
                    run_spacing=12,
                )
            )
        except Exception:
            pass

        if alg == "equivalencia":
            try:
                m2_preview = obtener_automata_m2()
                etiqueta_m2 = (
                    f"M2 ({estado_archivos['m2_nombre']})"
                    if estado_archivos["m2_nombre"]
                    else "Segundo Autómata (M2)"
                )
                bloques_previa.append(
                    ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "lg": 7},
                                controls=[
                                    construir_grafo_automata_canvas(
                                        m2_preview,
                                        titulo=f"Vista Gráfica — {etiqueta_m2}",
                                        ancho=620,
                                        alto=290,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "lg": 5},
                                controls=[
                                    construir_tabla_transiciones_visual(
                                        m2_preview,
                                        titulo=f"Tabla δ — {etiqueta_m2}",
                                    )
                                ],
                            ),
                        ],
                        spacing=12,
                        run_spacing=12,
                    )
                )
            except Exception:
                pass

        if bloques_previa:
            contenedor_vista_previa.controls = bloques_previa

        if e is not None:
            page.update()

    editor_automata_1.on_change = actualizar_vista_previa_entrada
    editor_automata_2.on_change = actualizar_vista_previa_entrada

    def aplicar_archivo_cargado(editor_num: int, nombre_archivo: str, contenido: str):
        auto_cargado = parsear_automata_desde_texto(contenido)
        resumen = (
            f"Archivo cargado: '{nombre_archivo}'  |  Tipo: {auto_cargado.tipo}  |  "
            f"Estados: {len(auto_cargado.estados)}  |  Transiciones: {len(auto_cargado.transiciones)}"
        )
        if editor_num == 1:
            estado_archivos["m1_auto"] = auto_cargado
            estado_archivos["m1_nombre"] = nombre_archivo
            txt_banner_m1.value = resumen
            banner_archivo_m1.visible = True
            editor_automata_1.visible = False
        else:
            estado_archivos["m2_auto"] = auto_cargado
            estado_archivos["m2_nombre"] = nombre_archivo
            txt_banner_m2.value = resumen
            banner_archivo_m2.visible = True
            editor_automata_2.visible = False

        actualizar_vista_previa_entrada()
        notificar(page, f"Autómata '{nombre_archivo}' cargado correctamente.")
        page.update()

    def limpiar_archivo_cargado(editor_num: int):
        alg = selector_algoritmo.value
        if editor_num == 1:
            estado_archivos["m1_auto"] = None
            estado_archivos["m1_nombre"] = None
            banner_archivo_m1.visible = False
            editor_automata_1.visible = (alg != "er_a_automata")
        else:
            estado_archivos["m2_auto"] = None
            estado_archivos["m2_nombre"] = None
            banner_archivo_m2.visible = False
            editor_automata_2.visible = (alg == "equivalencia")
        actualizar_vista_previa_entrada()
        page.update()

    target_carga = {"editor": 1}

    def on_upload_completado(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            ruta_local = os.path.join(UPLOAD_DIR, e.file_name)
            try:
                if os.path.exists(ruta_local):
                    with open(ruta_local, "r", encoding="utf-8", errors="replace") as f:
                        contenido = f.read()
                    aplicar_archivo_cargado(target_carga["editor"], e.file_name, contenido)
            except Exception as ex:
                notificar(page, f"Error leyendo archivo subido: {ex}", es_error=True)

    picker_cargar_p3 = ft.FilePicker()
    picker_cargar_p3.on_upload = on_upload_completado

    picker_guardar_p3 = ft.FilePicker()
    page.services.extend([picker_cargar_p3, picker_guardar_p3])

    async def procesar_seleccion_archivo(editor_num: int, titulo_dialogo: str):
        target_carga["editor"] = editor_num
        try:
            archivos = await picker_cargar_p3.pick_files(
                dialog_title=titulo_dialogo,
                allow_multiple=False,
                file_type=ft.FilePickerFileType.ANY,
            )
            if not archivos:
                return

            archivo = archivos[0]
            if getattr(archivo, "path", None):
                with open(archivo.path, "r", encoding="utf-8", errors="replace") as f:
                    contenido = f.read()
                aplicar_archivo_cargado(editor_num, archivo.name, contenido)
                return

            upload_url = page.get_upload_url(archivo.name, 600)
            await picker_cargar_p3.upload(
                [ft.FilePickerUploadFile(name=archivo.name, upload_url=upload_url)]
            )
        except Exception as ex:
            notificar(page, f"Error al cargar archivo: {ex}", es_error=True)

    async def cargar_m1_click(e):
        await procesar_seleccion_archivo(1, "Seleccionar archivo de Autómata M1 (.txt, .json, .jff, .xml)")

    async def cargar_m2_click(e):
        await procesar_seleccion_archivo(2, "Seleccionar archivo de Autómata M2 (.txt, .json, .jff, .xml)")

    async def guardar_reporte_click(e):
        try:
            contenido_bytes = (ultimo_reporte_txt["contenido"] or "Sin resultados generados.").encode("utf-8")
            await picker_guardar_p3.save_file(
                dialog_title="Descargar reporte de Práctica 3",
                file_name="reporte_practica3.txt",
                src_bytes=contenido_bytes,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt"],
            )
            notificar(page, "Descarga de reporte iniciada en el navegador.")
        except Exception as ex:
            notificar(page, f"Error al descargar reporte: {ex}", es_error=True)

    selector_algoritmo = ft.Dropdown(
        label="Algoritmo / Operación de Práctica 3",
        value="cerradura_lambda",
        expand=True,
        options=[
            ft.dropdown.Option("cerradura_lambda", "1. Cerradura Lambda (λ-clausura paso a paso)"),
            ft.dropdown.Option("simulacion_directa", "2. Simulación Directa de AFN / AFN-λ"),
            ft.dropdown.Option("eliminacion_lambda", "3. Eliminación de Transiciones Lambda (AFN-λ → AFN)"),
            ft.dropdown.Option("subconjuntos", "4. Construcción de Subconjuntos (AFN → AFD)"),
            ft.dropdown.Option("inaccesibles", "5. Eliminación de Estados Inaccesibles"),
            ft.dropdown.Option("minimizacion", "6. Minimización de AFD"),
            ft.dropdown.Option("equivalencia", "7. Equivalencia entre dos AFD (M1 ≡ M2)"),
            ft.dropdown.Option("automata_a_er", "8. Autómata Finito → Expresión Regular (GNFA)"),
            ft.dropdown.Option("er_a_automata", "9. Expresión Regular → Autómata Finito (Thompson)"),
        ],
    )

    btn_cargar_m2 = ft.OutlinedButton(
        "Subir M2",
        icon=ft.Icons.UPLOAD_FILE,
        visible=False,
        on_click=cargar_m2_click,
    )

    def al_cambiar_algoritmo(e):
        alg = selector_algoritmo.value
        es_equiv = (alg == "equivalencia")
        es_er = (alg == "er_a_automata")

        btn_cargar_m2.visible = es_equiv
        campo_er.visible = es_er

        # Mostrar banner o editor manual según si hay archivo cargado
        if es_er:
            banner_archivo_m1.visible = False
            editor_automata_1.visible = False
        else:
            banner_archivo_m1.visible = (estado_archivos["m1_auto"] is not None)
            editor_automata_1.visible = (estado_archivos["m1_auto"] is None)

        if es_equiv:
            banner_archivo_m2.visible = (estado_archivos["m2_auto"] is not None)
            editor_automata_2.visible = (estado_archivos["m2_auto"] is None)
        else:
            banner_archivo_m2.visible = False
            editor_automata_2.visible = False

        if alg == "cerradura_lambda":
            campo_parametro.visible = True
            campo_parametro.label = "Estado específico (opcional, vacío = todos los estados)"
            campo_parametro.hint_text = "Ej: q0"
        elif alg == "simulacion_directa":
            campo_parametro.visible = True
            campo_parametro.label = "Cadena de entrada a simular"
            campo_parametro.hint_text = "Ej: aab (vacío = cadena λ)"
        else:
            campo_parametro.visible = False

        actualizar_vista_previa_entrada()
        page.update()

    selector_algoritmo.on_select = al_cambiar_algoritmo

    def renderizar_bloque_automata_resultado(auto_res: Automata, titulo_bloque: str) -> ft.Control:
        """Agrupa el diagrama gráfico y la tabla de transiciones del autómata resultante."""
        return ft.ResponsiveRow(
            [
                ft.Column(
                    col={"xs": 12, "lg": 7},
                    controls=[
                        construir_grafo_automata_canvas(
                            auto_res,
                            titulo=f"Grafo Resultante — {titulo_bloque}",
                            ancho=640,
                            alto=330,
                        )
                    ],
                ),
                ft.Column(
                    col={"xs": 12, "lg": 5},
                    controls=[
                        construir_tabla_transiciones_visual(
                            auto_res,
                            titulo=f"Tabla de Transiciones — {titulo_bloque}",
                        )
                    ],
                ),
            ],
            spacing=12,
            run_spacing=12,
        )

    def ejecutar_algoritmo_p3(e):
        alg = selector_algoritmo.value
        controles_salida: list[ft.Control] = []
        lineas_txt: list[str] = []

        try:
            if alg == "er_a_automata":
                if er_a_automata is None:
                    raise RuntimeError("El módulo er_a_automata.py no exporta 'er_a_afnd_lambda'.")
                er = (campo_er.value or "").strip()
                if not er:
                    raise ValueError("Ingresa una expresión regular válida.")
                auto_res = er_a_automata(er)

                encabezado = f"CONVERSIÓN ER → AUTÓMATA (THOMPSON): '{er}'"
                lineas_txt.extend([encabezado, serializar_automata_texto(auto_res)])

                controles_salida.append(
                    ft.Text(encabezado, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
                )
                controles_salida.append(
                    renderizar_bloque_automata_resultado(auto_res, f"AFND-λ para '{er}'")
                )
            else:
                m1 = obtener_automata_m1()

                if alg == "cerradura_lambda":
                    est = (campo_parametro.value or "").strip() or None
                    res = calcular_cerradura_lambda(m1, estado=est)
                    lineas = ["=== CÁLCULO DE CERRADURA LAMBDA (λ-cl) ===", res["resumen_texto"], "\nDetalle paso a paso:"]
                    if est:
                        for p in res["pasos"]:
                            lineas.append(f"  Paso {p['paso']}: {p['descripcion']} -> {p['cerradura_parcial']}")
                    else:
                        for q, info in res["detalles"].items():
                            lineas.append(f"\nEstado {q}:")
                            for p in info["pasos"]:
                                lineas.append(f"  Paso {p['paso']}: {p['descripcion']}")
                    texto_res = "\n".join(lineas)
                    lineas_txt.append(texto_res)
                    controles_salida.append(
                        ft.Text(texto_res, selectable=True, font_family="monospace", size=13)
                    )

                elif alg == "simulacion_directa":
                    cadena = (campo_parametro.value or "").strip()
                    res = simular_afn_lambda_directo(m1, cadena)
                    if isinstance(res, tuple):
                        aceptada, traza = res
                        lineas = [
                            "=== SIMULACIÓN DIRECTA AFN / AFN-λ ===",
                            f"Cadena evaluada: '{cadena if cadena else 'λ'}'",
                            f"Resultado: {'ACEPTADA ✔' if aceptada else 'RECHAZADA ✘'}\n",
                        ]
                        for paso in traza:
                            lineas.append(str(paso))
                        texto_res = "\n".join(lineas)
                    elif isinstance(res, dict):
                        aceptada = res.get("aceptada", False)
                        lineas = [
                            "=== SIMULACIÓN DIRECTA AFN / AFN-λ ===",
                            f"Cadena evaluada: '{cadena if cadena else 'λ'}'",
                            f"Resultado: {'ACEPTADA ✔' if aceptada else 'RECHAZADA ✘'}\n",
                        ]
                        if "resumen_texto" in res:
                            lineas.append(res["resumen_texto"])
                        else:
                            for k, v in res.items():
                                lineas.append(f"{k}: {v}")
                        texto_res = "\n".join(lineas)
                    else:
                        aceptada = True
                        texto_res = str(res)

                    lineas_txt.append(texto_res)
                    controles_salida.append(
                        ft.Text(
                            texto_res,
                            selectable=True,
                            font_family="monospace",
                            size=13,
                            color=ft.Colors.GREEN_400 if aceptada else ft.Colors.RED_400,
                        )
                    )

                elif alg == "eliminacion_lambda":
                    afn_sin_l, rep = transformar_afn_sin_lambda_detallado(m1)
                    lineas = [
                        "=== ELIMINACIÓN DE TRANSICIONES LAMBDA (AFN-λ → AFN) ===",
                        f"Finales originales: {rep['finales_originales']}",
                        f"Finales resultantes: {rep['finales_resultantes']}",
                        f"Estados promovidos a aceptación ({rep['total_estados_promovidos']}):",
                    ]
                    for ep in rep["estados_promovidos"]:
                        lineas.append(f"  • {ep['razon']}")
                    lineas.append(f"\nTransiciones añadidas ({rep['total_transiciones_anadidas']}):")
                    for ta in rep["transiciones_anadidas"]:
                        lineas.append(f"  • δ({ta['origen']}, {ta['simbolo']}) -> {ta['destino']} | {ta['razon']}")

                    detalle_txt = "\n".join(lineas)
                    lineas_txt.extend([detalle_txt, "\n", serializar_automata_texto(afn_sin_l)])

                    controles_salida.append(
                        renderizar_bloque_automata_resultado(afn_sin_l, "AFN Equivalente Sin λ")
                    )
                    controles_salida.append(
                        ft.Text(detalle_txt, selectable=True, font_family="monospace", size=13)
                    )

                elif alg == "subconjuntos":
                    afd, rep = construccion_subconjuntos_detallada(m1)
                    lineas = [
                        "=== CONSTRUCCIÓN DE SUBCONJUNTOS (AFN → AFD) ===",
                        f"Subconjunto inicial S0 = {rep['subconjunto_inicial']}",
                        f"Total de subconjuntos alcanzables: {rep['total_subconjuntos_alcanzables']}\n",
                        "Justificación de estados de aceptación:",
                    ]
                    for nom, info in rep["justificacion_subconjuntos"].items():
                        marca = "[FINAL]" if info["es_final"] else "[NO FINAL]"
                        lineas.append(f"  • {nom} {marca}: {info['justificacion']}")

                    detalle_txt = "\n".join(lineas)
                    lineas_txt.extend([detalle_txt, "\n", serializar_automata_texto(afd)])

                    controles_salida.append(
                        renderizar_bloque_automata_resultado(afd, "AFD Resultante por Subconjuntos")
                    )
                    controles_salida.append(
                        ft.Text(detalle_txt, selectable=True, font_family="monospace", size=13)
                    )

                elif alg == "inaccesibles":
                    depurado, rep = eliminar_estados_inaccesibles_detallado(m1)
                    lineas = [
                        "=== ELIMINACIÓN DE ESTADOS INACCESIBLES ===",
                        f"Estados originales: {rep['estados_originales']}",
                        f"Estados alcanzables desde q0: {rep['estados_alcanzables']}",
                        f"Estados inaccesibles eliminados ({rep['total_eliminados']}): {rep['estados_inaccesibles']}",
                    ]
                    detalle_txt = "\n".join(lineas)
                    lineas_txt.extend([detalle_txt, "\n", serializar_automata_texto(depurado)])

                    controles_salida.append(
                        renderizar_bloque_automata_resultado(depurado, "Autómata Depurado (Sin Inaccesibles)")
                    )
                    controles_salida.append(
                        ft.Text(detalle_txt, selectable=True, font_family="monospace", size=13)
                    )

                elif alg == "minimizacion":
                    afd_min = minimizar_afd(m1)
                    rep_min = getattr(afd_min, "reporte_minimizacion", {})
                    lineas = [
                        "=== MINIMIZACIÓN DE AFD (HOPCROFT / PARTICIONES) ===",
                        f"Estados antes: {len(m1.estados)} | Estados después: {len(afd_min.estados)}",
                    ]
                    for ronda in rep_min.get("rondas", []):
                        lineas.append(f"  • {ronda.get('descripcion', '')}")

                    detalle_txt = "\n".join(lineas)
                    lineas_txt.extend([detalle_txt, "\n", serializar_automata_texto(afd_min)])

                    controles_salida.append(
                        renderizar_bloque_automata_resultado(afd_min, "AFD Mínimo Equivalente")
                    )
                    controles_salida.append(
                        ft.Text(detalle_txt, selectable=True, font_family="monospace", size=13)
                    )

                elif alg == "equivalencia":
                    m2 = obtener_automata_m2()
                    equiv, msg, det = decidir_equivalencia_detallada(m1, m2)
                    lineas = [
                        "=== DECISIÓN DE EQUIVALENCIA ENTRE DOS AFD ===",
                        f"Veredicto: {'EQUIVALENTES ✔' if equiv else 'NO EQUIVALENTES ✘'}",
                        f"Detalle: {msg}\n",
                    ]
                    if "isomorfismo" in det:
                        lineas.append(f"Isomorfismo de estados (M1 ↔ M2): {det['isomorfismo']}")
                    if det.get("contraejemplo") is not None:
                        ce = det["contraejemplo"] if det["contraejemplo"] != "" else "λ (cadena vacía)"
                        lineas.append(f"Cadena contraejemplo más corta: {ce}")

                    texto_res = "\n".join(lineas)
                    lineas_txt.append(texto_res)
                    controles_salida.append(
                        ft.Text(
                            texto_res,
                            selectable=True,
                            font_family="monospace",
                            size=13,
                            color=ft.Colors.GREEN_400 if equiv else ft.Colors.AMBER_300,
                        )
                    )

                elif alg == "automata_a_er":
                    if automata_a_expresion_regular is None:
                        raise RuntimeError("Módulo automata_a_er.py no disponible.")
                    er_res, hist = automata_a_expresion_regular(m1)
                    lineas = [
                        "=== CONVERSIÓN AUTÓMATA → EXPRESIÓN REGULAR (GNFA) ===",
                        f"Expresión Regular Equivalente: {er_res}\n",
                        "Pasos de eliminación de estados:",
                    ]
                    for h in hist:
                        lineas.append(f"  • {h['paso']}: {h['detalle']}")

                    texto_res = "\n".join(lineas)
                    lineas_txt.append(texto_res)
                    controles_salida.append(
                        ft.Text(
                            f"Expresión Regular Resultante: {er_res}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN_400,
                            selectable=True,
                        )
                    )
                    controles_salida.append(
                        ft.Text(texto_res, selectable=True, font_family="monospace", size=13)
                    )

            ultimo_reporte_txt["contenido"] = "\n".join(lineas_txt)
            contenedor_resultados_p3.controls = controles_salida

        except Exception as ex:
            ultimo_reporte_txt["contenido"] = f"ERROR EN EJECUCIÓN:\n{ex}"
            contenedor_resultados_p3.controls = [
                ft.Text(
                    f"ERROR EN EJECUCIÓN:\n{ex}",
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]

        page.update()

    def cargar_ejemplo_rapido(e):
        estado_archivos["m1_auto"] = None
        estado_archivos["m1_nombre"] = None
        estado_archivos["m2_auto"] = None
        estado_archivos["m2_nombre"] = None
        banner_archivo_m1.visible = False
        banner_archivo_m2.visible = False
        editor_automata_1.visible = (selector_algoritmo.value != "er_a_automata")
        editor_automata_2.visible = (selector_algoritmo.value == "equivalencia")
        editor_automata_1.value = EJEMPLO_AFN_LAMBDA.strip()
        editor_automata_2.value = EJEMPLO_AFD_EQUIV_2.strip()
        actualizar_vista_previa_entrada()
        notificar(page, "Ejemplos de autómatas restaurados.")
        page.update()

    actualizar_vista_previa_entrada()

    return ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Icon(ft.Icons.ACCOUNT_TREE, size=28, color=ft.Colors.PURPLE_400),
                    ft.Column(
                        [
                            ft.Text("Práctica 3: Autómatas No Deterministas, Minimización y Equivalencia", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Visualización gráfica, tabla de transiciones δ, cerradura λ, subconjuntos, minimización y Kleene.", size=12, color=ft.Colors.GREY_400),
                        ],
                        spacing=2,
                    ),
                ]
            ),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        [
                            ft.Row([selector_algoritmo], spacing=10),
                            ft.Row([campo_parametro, campo_er], spacing=10),
                            banner_archivo_m1,
                            banner_archivo_m2,
                            ft.Row([editor_automata_1, editor_automata_2], spacing=12),
                            ft.Row(
                                [
                                    ft.Button(
                                        "Ejecutar Algoritmo",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=ejecutar_algoritmo_p3,
                                    ),
                                    ft.OutlinedButton(
                                        "Subir M1 desde Archivo",
                                        icon=ft.Icons.UPLOAD_FILE,
                                        on_click=cargar_m1_click,
                                    ),
                                    btn_cargar_m2,
                                    ft.OutlinedButton(
                                        "Descargar Reporte",
                                        icon=ft.Icons.DOWNLOAD,
                                        on_click=guardar_reporte_click,
                                    ),
                                    ft.TextButton(
                                        "Restaurar Ejemplo",
                                        icon=ft.Icons.RESTORE,
                                        on_click=cargar_ejemplo_rapido,
                                    ),
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                            contenedor_vista_previa,
                        ],
                        spacing=12,
                    ),
                )
            ),
            ft.Text("Resultados, Diagrama Gráfico y Tabla de Transiciones:", weight=ft.FontWeight.BOLD, size=15),
            ft.Container(
                content=ft.SelectionArea(content=contenedor_resultados_p3),
                padding=18,
                border_radius=8,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            ),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=12,
    )


# =====================================================================
# PUNTO DE ENTRADA PRINCIPAL CON BIENVENIDA Y BARRA DE NAVEGACIÓN
# =====================================================================

def main_integrada(page: ft.Page):
    """Arranca en la pantalla de bienvenida y cambia a cada práctica desde la barra inferior."""
    page.title = "Teoría de la Computación — Suite Integrada (Prácticas 1, 2, 3 y 4)"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    vistas_cache: dict[int, ft.Control] = {
        0: crear_vista_bienvenida(),
    }

    contenedor_dinamico = ft.Container(content=vistas_cache[0], expand=True)

    def cambiar_modulo(e):
        indice = e.control.selected_index
        if indice not in vistas_cache:
            if indice == 1:
                vistas_cache[1] = crear_vista_practica1(page)
            elif indice == 2:
                vistas_cache[2] = crear_vista_simulador(page)
            elif indice == 3:
                vistas_cache[3] = crear_vista_practica3(page)
            elif indice == 4:
                vistas_cache[4] = crear_vista_practica4(
                    page,
                    construir_grafo_automata_canvas,
                    construir_tabla_transiciones_visual,
                    notificar,
                )

        contenedor_dinamico.content = vistas_cache[indice]
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Inicio",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALCULATE_OUTLINED,
                selected_icon=ft.Icons.CALCULATE,
                label="Práctica 1: Cadenas",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.PLAY_CIRCLE,
                label="Práctica 2: Simulador",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ACCOUNT_TREE_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_TREE,
                label="Práctica 3: AFN y Minimiz.",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FUNCTIONS_OUTLINED,
                selected_icon=ft.Icons.FUNCTIONS,
                label="Práctica 4: Expr. Regulares",
            ),
        ],
        selected_index=0,
        on_change=cambiar_modulo,
    )

    page.navigation_bar = nav_bar
    page.add(contenedor_dinamico)
    page.update()


if __name__ == "__main__":
    os.environ.setdefault("FLET_SECRET_KEY", "teoria-computacion-escom-2026")
    ft.run(main_integrada, upload_dir=UPLOAD_DIR)