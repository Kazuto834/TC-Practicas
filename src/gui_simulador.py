"""
Módulo de Interfaz Gráfica para el Simulador de Autómatas Finitos (Práctica 2).
Incluye visor gráfico vectorial interactivo (Canvas) con resaltado en tiempo real
de estados activos y transiciones tomadas en cada paso de la simulación, tabla
formal de transiciones δ (DataTable) y bloqueo al subir archivos .jff.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
"""

from __future__ import annotations
import math
import os
import tempfile
import flet as ft
import flet.canvas as cv
from automata import Automata
from formatos import FormatosAutomata

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "flet_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def construir_grafo_simulador_canvas(
    auto: Automata,
    estados_activos: set[str] | None = None,
    transiciones_activas: set[tuple[str, str, str]] | None = None,
    es_aceptacion_paso: bool = False,
    titulo: str = "Diagrama Gráfico en Tiempo Real",
    ancho: float = 650,
    alto: float = 330,
) -> ft.Control:
    """
    Renderiza el diagrama vectorial del autómata en Flet 0.86.5:
    - Resalta en ámbar/verde los estados activos en el paso actual.
    - Ilumina en cian las transiciones δ(origen, símbolo) -> destino tomadas en ese paso.
    """
    estados = sorted(list(auto.estados))
    estados_activos = estados_activos or set()
    transiciones_activas = transiciones_activas or set()

    if not estados:
        return ft.Container(
            padding=16,
            border_radius=8,
            bgcolor="#141821",
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Text(
                "Define estados manualmente o sube un archivo (.jff, .json, .xml) para visualizar el grafo.",
                size=13,
                color=ft.Colors.GREY_400,
            ),
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

    # Agrupar símbolos por par (origen, destino) y detectar si alguno está activo en este paso
    aristas: dict[tuple[str, str], list[tuple[str, bool]]] = {}
    for t in auto.transiciones:
        etq = t.simbolo if t.simbolo else "λ"
        clave_trans = (t.origen, t.simbolo, t.destino)
        esta_activa = clave_trans in transiciones_activas
        aristas.setdefault((t.origen, t.destino), [])

        # Evitar duplicados actualizando el flag activo si aplica
        existente = next((idx for idx, item in enumerate(aristas[(t.origen, t.destino)]) if item[0] == etq), None)
        if existente is None:
            aristas[(t.origen, t.destino)].append((etq, esta_activa))
        elif esta_activa:
            aristas[(t.origen, t.destino)][existente] = (etq, True)

    shapes: list[cv.Shape] = []

    pincel_arista_normal = ft.Paint(
        color=ft.Colors.BLUE_GREY_300,
        stroke_width=1.7,
        style=ft.PaintingStyle.STROKE,
    )
    pincel_flecha_normal = ft.Paint(
        color=ft.Colors.BLUE_GREY_300,
        style=ft.PaintingStyle.FILL,
    )
    pincel_arista_activa = ft.Paint(
        color=ft.Colors.CYAN_300,
        stroke_width=3.2,
        style=ft.PaintingStyle.STROKE,
    )
    pincel_flecha_activa = ft.Paint(
        color=ft.Colors.CYAN_300,
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

    def dibujar_punta_flecha(px: float, py: float, angulo: float, paint_fill: ft.Paint, escala: float = 8.5):
        a1 = angulo + math.radians(152)
        a2 = angulo - math.radians(152)
        p1 = (px + escala * math.cos(a1), py + escala * math.sin(a1))
        p2 = (px + escala * math.cos(a2), py + escala * math.sin(a2))
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

    # 1. Dibujar aristas (primero inactivas, luego activas encima para máxima visibilidad)
    aristas_ordenadas = sorted(
        aristas.items(),
        key=lambda item: any(act for _, act in item[1]),
    )

    for (orig, dest), lista_simbs in aristas_ordenadas:
        if orig not in posiciones or dest not in posiciones:
            continue

        arista_activa = any(act for _, act in lista_simbs)
        etiquetas_fmt = [f"[{s}]" if act else s for s, act in sorted(lista_simbs, key=lambda x: x[0])]
        etiqueta = ", ".join(etiquetas_fmt)

        p_stroke = pincel_arista_activa if arista_activa else pincel_arista_normal
        p_fill = pincel_flecha_activa if arista_activa else pincel_flecha_normal
        color_texto = ft.Colors.CYAN_200 if arista_activa else ft.Colors.AMBER_300
        tam_flecha = 10.5 if arista_activa else 8.5

        x1, y1 = posiciones[orig]
        x2, y2 = posiciones[dest]

        if orig == dest:
            vx, vy = x1 - cx, y1 - cy
            norm = math.hypot(vx, vy)
            ux, uy = (0.0, -1.0) if norm < 1e-3 else (vx / norm, vy / norm)

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
                    paint=p_stroke,
                )
            )
            ang_punta = math.atan2(ey - c2y, ex - c2x)
            dibujar_punta_flecha(ex, ey, ang_punta, p_fill, tam_flecha)

            lx = x1 + (radio_nodo + 35.0) * ux
            ly = y1 + (radio_nodo + 35.0) * uy
            shapes.append(
                cv.Text(
                    x=lx,
                    y=ly,
                    value=etiqueta,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=13 if arista_activa else 12,
                        weight=ft.FontWeight.BOLD,
                        color=color_texto,
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
                        paint=p_stroke,
                    )
                )
            else:
                shapes.append(cv.Line(sx, sy, ex, ey, paint=p_stroke))

            dibujar_punta_flecha(ex, ey, ang_ent, p_fill, tam_flecha)

            lx = (sx + 2 * mx + ex) / 4.0 + nx * 13.0
            ly = (sy + 2 * my + ey) / 4.0 + ny * 13.0
            shapes.append(
                cv.Text(
                    x=lx,
                    y=ly,
                    value=etiqueta,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=13 if arista_activa else 12,
                        weight=ft.FontWeight.BOLD,
                        color=color_texto,
                    ),
                )
            )

    # 2. Flecha de estado inicial q0
    if auto.estado_inicial and auto.estado_inicial in posiciones:
        ix, iy = posiciones[auto.estado_inicial]
        vx, vy = ix - cx, iy - cy
        norm = math.hypot(vx, vy)
        ux, uy = (-1.0, 0.0) if norm < 1e-3 else (vx / norm, vy / norm)

        punta_x = ix + radio_nodo * ux
        punta_y = iy + radio_nodo * uy
        cola_x = ix + (radio_nodo + 30.0) * ux
        cola_y = iy + (radio_nodo + 30.0) * uy

        shapes.append(cv.Line(cola_x, cola_y, punta_x, punta_y, paint=pincel_inicio))
        dibujar_punta_flecha(punta_x, punta_y, math.atan2(punta_y - cola_y, punta_x - cola_x), pincel_inicio_fill)

    # 3. Nodos (estados) con resaltado de estados activos en el paso
    for q in estados:
        px, py = posiciones[q]
        es_ini = (q == auto.estado_inicial)
        es_fin = (q in auto.estados_aceptacion)
        es_activo = (q in estados_activos)

        if es_activo and es_fin and es_aceptacion_paso:
            color_relleno = "#14532D"
            color_borde = ft.Colors.GREEN_300
            grosor_borde = 3.2
        elif es_activo:
            color_relleno = "#78350F"
            color_borde = ft.Colors.AMBER_300
            grosor_borde = 3.2
        else:
            color_relleno = "#1E2430"
            color_borde = (
                ft.Colors.AMBER_400 if (es_ini and es_fin)
                else ft.Colors.GREEN_400 if es_ini
                else ft.Colors.BLUE_400 if es_fin
                else ft.Colors.BLUE_GREY_300
            )
            grosor_borde = 2.3

        # Aura externa si el estado está activo en el paso actual
        if es_activo:
            shapes.append(
                cv.Circle(
                    x=px,
                    y=py,
                    radius=radio_nodo + 5.0,
                    paint=ft.Paint(
                        color=ft.Colors.with_opacity(0.35, color_borde),
                        stroke_width=2.0,
                        style=ft.PaintingStyle.STROKE,
                    ),
                )
            )

        shapes.append(
            cv.Circle(
                x=px,
                y=py,
                radius=radio_nodo,
                paint=ft.Paint(color=color_relleno, style=ft.PaintingStyle.FILL),
            )
        )
        shapes.append(
            cv.Circle(
                x=px,
                y=py,
                radius=radio_nodo,
                paint=ft.Paint(color=color_borde, stroke_width=grosor_borde, style=ft.PaintingStyle.STROKE),
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
                    ft.Text("● Activo", size=11, color=ft.Colors.AMBER_300),
                    ft.Text("━ Transición tomada", size=11, color=ft.Colors.CYAN_300),
                    ft.Text("◎ Final", size=11, color=ft.Colors.BLUE_400),
                ],
                spacing=10,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        spacing=10,
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


def construir_tabla_transiciones_simulador(
    auto: Automata,
    estados_activos: set[str] | None = None,
    titulo: str = "Tabla Formal de Transiciones (δ)",
) -> ft.Control:
    """Construye un DataTable formal de la función δ destacando los estados activos."""
    estados = sorted(list(auto.estados))
    estados_activos = estados_activos or set()

    if not estados:
        return ft.Container(
            padding=16,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Text("Sin tabla de transiciones.", size=13, color=ft.Colors.GREY_400),
        )

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

        es_act = q in estados_activos
        celdas = [
            ft.DataCell(
                ft.Text(
                    f"{prefijo}{q}",
                    weight=ft.FontWeight.BOLD,
                    font_family="monospace",
                    color=ft.Colors.AMBER_300 if es_act else (ft.Colors.GREEN_300 if q == auto.estado_inicial else None),
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

        filas.append(
            ft.DataRow(
                cells=celdas,
                color=ft.Colors.with_opacity(0.14, ft.Colors.AMBER_400) if es_act else None,
            )
        )

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
                        ft.Text(f"Tipo: {auto.tipo}", size=12, color=ft.Colors.GREEN_300, weight=ft.FontWeight.BOLD),
                    ]
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


def crear_vista_simulador(page: ft.Page) -> ft.Control:
    """
    Construye la vista de la Práctica 2 con visor gráfico vectorial, tabla δ
    y resaltado dinámico de transiciones en cada paso de la simulación.
    """
    automata_actual: Automata = Automata()
    traza_actual: list = []
    indice_paso_actual: int = 0
    bloqueado_por_archivo: bool = False

    # -------------------------------------------------------------------------
    # Controles de Definición Manual
    # -------------------------------------------------------------------------
    titulo_quintupla_manual = ft.Text(
        "1. Definición de Quíntupla y Transiciones",
        size=14,
        weight=ft.FontWeight.BOLD,
    )

    badge_bloqueo_archivo = ft.Text(
        value="",
        size=12,
        color=ft.Colors.AMBER_300,
        weight=ft.FontWeight.W_500,
        visible=False,
    )

    tf_estados = ft.TextField(
        label="Estados Q (ej. A, B, C)",
        hint_text="A, B, C",
        dense=True,
        expand=True,
    )
    tf_alfabeto = ft.TextField(
        label="Alfabeto Σ (ej. 0, 1)",
        hint_text="0, 1",
        dense=True,
        expand=True,
    )
    tf_inicial = ft.TextField(
        label="Estado Inicial q0",
        hint_text="A",
        dense=True,
        width=180,
    )
    tf_aceptacion = ft.TextField(
        label="Estados Aceptación F",
        hint_text="C",
        dense=True,
        expand=True,
    )

    tf_trans_origen = ft.TextField(label="Origen", hint_text="A", dense=True, expand=True)
    tf_trans_simbolo = ft.TextField(label="Símbolo (vacío = λ)", hint_text="0", dense=True, expand=True)
    tf_trans_destino = ft.TextField(label="Destino", hint_text="B", dense=True, expand=True)

    btn_aplicar_quintupla = ft.Button(
        "Aplicar Quíntupla",
        icon=ft.Icons.CHECK,
    )
    btn_agregar_transicion = ft.Button(
        "Agregar Transición",
        icon=ft.Icons.ADD,
    )

    # -------------------------------------------------------------------------
    # Contenedor del Visor Gráfico + Tabla Formal de Transiciones δ
    # -------------------------------------------------------------------------
    contenedor_visualizador_grafo_tabla = ft.Column(spacing=10)

    # -------------------------------------------------------------------------
    # Controles de Simulación y Salida
    # -------------------------------------------------------------------------
    tf_cadena_simular = ft.TextField(
        label="Cadena de entrada w",
        hint_text="Ej: 001001 (vacío = λ)",
        prefix_icon=ft.Icons.INPUT,
        dense=True,
        width=320,
    )

    txt_estado_quintupla = ft.Text(
        value="Tipo: Ninguno (0 transiciones)  |  M = (∅, ∅, δ, ∅, ∅)",
        size=13,
        font_family="monospace",
        color=ft.Colors.GREEN_300,
        selectable=True,
    )

    txt_resultado_sim = ft.Text(
        value="Define o importa un autómata e ingresa una cadena para simular.",
        size=14,
        weight=ft.FontWeight.BOLD,
    )

    banner_transicion_paso = ft.Container(
        visible=False,
        padding=10,
        border_radius=6,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.CYAN_400),
        border=ft.Border.all(1, ft.Colors.CYAN_400),
        content=ft.Text(
            value="",
            size=13,
            font_family="monospace",
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_200,
            selectable=True,
        ),
    )

    txt_salida_unificada = ft.Text(
        value="Aquí se mostrará la traza paso a paso de la simulación.",
        size=13,
        font_family="monospace",
        selectable=True,
    )

    btn_paso_anterior = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Paso anterior",
        disabled=True,
    )
    btn_paso_siguiente = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD,
        tooltip="Paso siguiente",
        disabled=True,
    )
    txt_contador_pasos = ft.Text(value="Paso: - / -", size=12)

    # -------------------------------------------------------------------------
    # Control de Bloqueo / Desbloqueo del Apartado Manual
    # -------------------------------------------------------------------------
    def establecer_bloqueo_manual(bloqueado: bool, nombre_archivo: str = ""):
        nonlocal bloqueado_por_archivo
        bloqueado_por_archivo = bloqueado
        controles_manuales = [
            tf_estados,
            tf_alfabeto,
            tf_inicial,
            tf_aceptacion,
            tf_trans_origen,
            tf_trans_simbolo,
            tf_trans_destino,
            btn_aplicar_quintupla,
            btn_agregar_transicion,
        ]
        for ctrl in controles_manuales:
            ctrl.disabled = bloqueado

        recuadro_quintupla.opacity = 0.55 if bloqueado else 1.0
        if bloqueado:
            badge_bloqueo_archivo.value = (
                f"🔒 Archivo cargado ({nombre_archivo}). Presiona 'Limpiar' para editar manualmente."
            )
            badge_bloqueo_archivo.visible = True
        else:
            badge_bloqueo_archivo.value = ""
            badge_bloqueo_archivo.visible = False

    # -------------------------------------------------------------------------
    # Notificación Segura
    # -------------------------------------------------------------------------
    def mostrar_snack(mensaje: str, es_error: bool = False):
        try:
            snack = ft.SnackBar(
                content=ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700,
                duration=2500,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception:
            txt_resultado_sim.value = mensaje
            txt_resultado_sim.color = ft.Colors.RED_400 if es_error else ft.Colors.GREEN_400
            page.update()

    # -------------------------------------------------------------------------
    # Actualización del Visor Gráfico + Tabla Formal δ (Con o Sin Paso Activo)
    # -------------------------------------------------------------------------
    def refrescar_panel_estados_y_transiciones(
        estados_activos: set[str] | None = None,
        transiciones_activas: set[tuple[str, str, str]] | None = None,
        es_aceptacion_paso: bool = False,
        subtitulo_grafo: str = "Diagrama de Estados en Tiempo Real",
    ):
        contenedor_visualizador_grafo_tabla.controls = [
            ft.ResponsiveRow(
                [
                    ft.Column(
                        col={"xs": 12, "lg": 7},
                        controls=[
                            construir_grafo_simulador_canvas(
                                automata_actual,
                                estados_activos=estados_activos,
                                transiciones_activas=transiciones_activas,
                                es_aceptacion_paso=es_aceptacion_paso,
                                titulo=subtitulo_grafo,
                                ancho=630,
                                alto=310,
                            )
                        ],
                    ),
                    ft.Column(
                        col={"xs": 12, "lg": 5},
                        controls=[
                            construir_tabla_transiciones_simulador(
                                automata_actual,
                                estados_activos=estados_activos,
                                titulo="Tabla Formal de Transiciones (δ)",
                            )
                        ],
                    ),
                ],
                spacing=12,
                run_spacing=12,
            )
        ]

    def actualizar_resumen_quintupla(actualizar_salida: bool = True):
        nonlocal automata_actual
        q_str = "{" + ", ".join(sorted(list(automata_actual.estados))) + "}"
        sig_str = "{" + ", ".join(sorted(list(automata_actual.alfabeto))) + "}"
        q0_str = str(automata_actual.estado_inicial or "∅")
        f_str = "{" + ", ".join(sorted(list(automata_actual.estados_aceptacion))) + "}"

        automata_actual._actualizar_tipo()
        txt_estado_quintupla.value = (
            f"Tipo: {automata_actual.tipo} ({len(automata_actual.transiciones)} transiciones)\n"
            f"Q = {q_str}  |  Σ = {sig_str}  |  q0 = {q0_str}  |  F = {f_str}"
        )
        refrescar_panel_estados_y_transiciones()
        if actualizar_salida and not traza_actual:
            banner_transicion_paso.visible = False
            txt_salida_unificada.value = "Autómata actualizado. Ingresa una cadena w y presiona 'Simular Cadena' para ver la traza."
        page.update()

    # -------------------------------------------------------------------------
    # Sincronización en Vivo al Escribir Manualmente (on_change)
    # -------------------------------------------------------------------------
    def sincronizar_quintupla_en_vivo(e=None):
        nonlocal automata_actual
        if bloqueado_por_archivo:
            return

        estados_txt = [x.strip() for x in (tf_estados.value or "").split(",") if x.strip()]
        alfabeto_txt = [x.strip() for x in (tf_alfabeto.value or "").split(",") if x.strip()]
        inicial_txt = (tf_inicial.value or "").strip() or None
        aceptacion_txt = [x.strip() for x in (tf_aceptacion.value or "").split(",") if x.strip()]

        estados_trans = []
        for t in automata_actual.transiciones:
            estados_trans.extend([t.origen, t.destino])

        conjunto_estados = list(
            dict.fromkeys(
                estados_txt
                + ([inicial_txt] if inicial_txt else [])
                + aceptacion_txt
                + estados_trans
            )
        )

        nuevo_auto = Automata()
        for q in conjunto_estados:
            nuevo_auto.agregar_estado(
                q,
                es_inicial=(q == inicial_txt),
                es_final=(q in aceptacion_txt),
            )
        for a in alfabeto_txt:
            nuevo_auto.agregar_simbolo(a)

        for t in automata_actual.transiciones:
            nuevo_auto.agregar_transicion(t.origen, t.simbolo, t.destino)

        automata_actual = nuevo_auto
        actualizar_resumen_quintupla(actualizar_salida=False)

    tf_estados.on_change = sincronizar_quintupla_en_vivo
    tf_alfabeto.on_change = sincronizar_quintupla_en_vivo
    tf_inicial.on_change = sincronizar_quintupla_en_vivo
    tf_aceptacion.on_change = sincronizar_quintupla_en_vivo

    def aplicar_definicion_manual(e):
        nonlocal automata_actual, traza_actual, indice_paso_actual
        try:
            sincronizar_quintupla_en_vivo()
            if not automata_actual.estados:
                mostrar_snack("Ingresa al menos un estado en Q (ej: A, B, C).", es_error=True)
                return

            tf_estados.value = ", ".join(sorted(list(automata_actual.estados)))
            traza_actual = []
            indice_paso_actual = 0
            btn_paso_anterior.disabled = True
            btn_paso_siguiente.disabled = True
            txt_contador_pasos.value = "Paso: - / -"
            banner_transicion_paso.visible = False
            txt_resultado_sim.value = "Quíntupla confirmada. Agrega transiciones o simula una cadena."
            txt_resultado_sim.color = ft.Colors.BLUE_300

            actualizar_resumen_quintupla(actualizar_salida=True)
            mostrar_snack("Quíntupla aplicada correctamente.")
        except Exception as ex:
            mostrar_snack(f"Error al aplicar quíntupla: {ex}", es_error=True)

    def agregar_transicion_click(e):
        nonlocal automata_actual, traza_actual
        try:
            orig = (tf_trans_origen.value or "").strip()
            simb = (tf_trans_simbolo.value or "").strip()
            dest = (tf_trans_destino.value or "").strip()

            if not orig or not dest:
                mostrar_snack("Especifica el estado de origen y destino.", es_error=True)
                return

            if not automata_actual.estados and not automata_actual.estado_inicial:
                automata_actual.agregar_estado(orig, es_inicial=True, es_final=False)
                tf_inicial.value = orig

            automata_actual.agregar_transicion(orig, simb, dest)
            tf_estados.value = ", ".join(sorted(list(automata_actual.estados)))
            tf_alfabeto.value = ", ".join(sorted(list(automata_actual.alfabeto)))
            tf_trans_simbolo.value = ""
            traza_actual = []

            actualizar_resumen_quintupla(actualizar_salida=True)
            mostrar_snack(f"Transición δ({orig}, '{simb or 'λ'}') → {dest} agregada.")
        except Exception as ex:
            mostrar_snack(f"Error al agregar transición: {ex}", es_error=True)

    btn_aplicar_quintupla.on_click = aplicar_definicion_manual
    btn_agregar_transicion.on_click = agregar_transicion_click

    # -------------------------------------------------------------------------
    # Simulación Paso a Paso con Iluminación Gráfica de Transiciones
    # -------------------------------------------------------------------------
    def mostrar_paso_actual():
        nonlocal traza_actual, indice_paso_actual
        if not traza_actual:
            btn_paso_anterior.disabled = True
            btn_paso_siguiente.disabled = True
            txt_contador_pasos.value = "Paso: - / -"
            banner_transicion_paso.visible = False
            refrescar_panel_estados_y_transiciones()
            page.update()
            return

        paso = traza_actual[indice_paso_actual]
        num_paso = paso.get("paso", 0)
        total_pasos = len(traza_actual) - 1

        btn_paso_anterior.disabled = (indice_paso_actual == 0)
        btn_paso_siguiente.disabled = (indice_paso_actual == total_pasos)
        txt_contador_pasos.value = f"Paso {num_paso} de {total_pasos}"

        simbolo_leido = paso.get("simbolo_leido")
        trans_tomadas_raw = paso.get("transiciones_tomadas", [])
        estados_activos_paso = set(paso.get("clausura_posterior") or paso.get("estados_posteriores") or [])
        es_acep_paso = bool(paso.get("es_aceptacion", False))

        # Construir conjunto de tuplas (origen, simbolo, destino) iluminadas en el grafo
        transiciones_iluminadas: set[tuple[str, str, str]] = set()
        descripciones_trans: list[str] = []

        for tr in trans_tomadas_raw:
            origen_t = tr.get("desde", "")
            simb_t = tr.get("lee", "")
            dest_t = tr.get("hacia", "")
            transiciones_iluminadas.add((origen_t, simb_t, dest_t))
            descripciones_trans.append(f"δ({origen_t}, '{simb_t or 'λ'}') → {dest_t}")

        # Detectar también transiciones λ encadenadas en este paso
        destinos_dir = set(paso.get("estados_posteriores") or [])
        if num_paso == 0:
            destinos_dir = set(paso.get("estados_previos") or [])
        for t in automata_actual.transiciones:
            if t.es_lambda() and t.origen in destinos_dir and t.destino in estados_activos_paso:
                transiciones_iluminadas.add((t.origen, t.simbolo, t.destino))
                descripciones_trans.append(f"δ({t.origen}, 'λ') → {t.destino}")

        if num_paso == 0:
            resumen_banner = (
                f"Paso 0 (Inicio): Estado inicial q0 = {paso.get('estados_previos', [])}  →  "
                f"λ-clausura activa = {sorted(list(estados_activos_paso))}"
            )
            if descripciones_trans:
                resumen_banner += f"  |  Transiciones λ: {', '.join(descripciones_trans)}"
        elif descripciones_trans:
            resumen_banner = (
                f"Paso {num_paso} (lee '{simbolo_leido}'):  "
                + "   |   ".join(descripciones_trans)
                + f"   ⇒   Activos: {sorted(list(estados_activos_paso))}"
            )
        else:
            resumen_banner = (
                f"Paso {num_paso} (lee '{simbolo_leido}'): Sin transiciones válidas → Estado de bloqueo (∅)"
            )

        banner_transicion_paso.content.value = resumen_banner
        banner_transicion_paso.visible = True

        # Actualizar grafo y tabla iluminando los estados y transiciones de este paso
        refrescar_panel_estados_y_transiciones(
            estados_activos=estados_activos_paso,
            transiciones_activas=transiciones_iluminadas,
            es_aceptacion_paso=es_acep_paso,
            subtitulo_grafo=f"Grafo en Paso {num_paso}/{total_pasos} — Símbolo: '{simbolo_leido if simbolo_leido else 'Inicio (λ)'}'",
        )

        lineas = [
            f"=== TRAZA DE SIMULACIÓN — PASO {num_paso} DE {total_pasos} ===",
            f"Símbolo procesado:     {simbolo_leido if simbolo_leido else 'λ (Inicio)'}",
            f"Estados activos antes: {paso.get('estados_previos', [])}",
            f"λ-clausura previa:     {paso.get('clausura_previa', [])}",
            f"Transiciones tomadas:  {descripciones_trans if descripciones_trans else 'Ninguna'}",
            f"Destinos directos:     {paso.get('estados_posteriores', [])}",
            f"λ-clausura resultante: {paso.get('clausura_posterior', [])}",
            f"¿Alcanza aceptación?:  {'SÍ ✔' if es_acep_paso else 'NO ✘'}",
        ]
        if "error" in paso:
            lineas.append(f"ERROR: {paso['error']}")

        txt_salida_unificada.value = "\n".join(lineas)
        page.update()

    def ejecutar_simulacion_completa(e):
        nonlocal automata_actual, traza_actual, indice_paso_actual
        if not automata_actual.estados:
            mostrar_snack("Define o importa un autómata antes de simular.", es_error=True)
            return

        cadena = tf_cadena_simular.value or ""
        aceptada, traza = automata_actual.simular_cadena(cadena)
        traza_actual = traza
        # Iniciar en el Paso 1 (o Paso 0 si la cadena es vacía) para ver la primera transición
        indice_paso_actual = 1 if len(traza) > 1 else 0

        txt_resultado_sim.value = (
            f"Cadena '{cadena if cadena else 'λ'}' → {'ACEPTADA ✔' if aceptada else 'RECHAZADA ✘'} "
            f"(Usa las flechas ◀ ▶ para recorrer cada transición)"
        )
        txt_resultado_sim.color = ft.Colors.GREEN_400 if aceptada else ft.Colors.RED_400
        mostrar_paso_actual()

    def paso_anterior_click(e):
        nonlocal indice_paso_actual
        if indice_paso_actual > 0:
            indice_paso_actual -= 1
            mostrar_paso_actual()

    def paso_siguiente_click(e):
        nonlocal indice_paso_actual, traza_actual
        if indice_paso_actual < len(traza_actual) - 1:
            indice_paso_actual += 1
            mostrar_paso_actual()

    btn_paso_anterior.on_click = paso_anterior_click
    btn_paso_siguiente.on_click = paso_siguiente_click

    # -------------------------------------------------------------------------
    # Importación / Exportación de Archivos (.jff, .json, .xml) en Docker Web
    # -------------------------------------------------------------------------
    def cargar_desde_ruta_local(ruta: str, nombre_visible: str):
        nonlocal automata_actual, traza_actual
        ext = os.path.splitext(nombre_visible)[1].lower()
        if ext == ".jff":
            automata_actual = FormatosAutomata.cargar_jff(ruta)
        elif ext == ".json":
            automata_actual = FormatosAutomata.cargar_json(ruta)
        elif ext == ".xml":
            automata_actual = FormatosAutomata.cargar_xml(ruta)
        else:
            mostrar_snack(f"Extensión no soportada: {ext}", es_error=True)
            return

        traza_actual = []
        banner_transicion_paso.visible = False
        tf_estados.value = ", ".join(sorted(list(automata_actual.estados)))
        tf_alfabeto.value = ", ".join(sorted(list(automata_actual.alfabeto)))
        tf_inicial.value = automata_actual.estado_inicial or ""
        tf_aceptacion.value = ", ".join(sorted(list(automata_actual.estados_aceptacion)))

        if ext in (".jff", ".xml", ".json"):
            establecer_bloqueo_manual(True, nombre_visible)

        txt_resultado_sim.value = f"Autómata cargado desde '{nombre_visible}'. Listo para simular."
        txt_resultado_sim.color = ft.Colors.BLUE_300

        actualizar_resumen_quintupla()
        mostrar_snack(f"Autómata importado desde '{nombre_visible}'.")

    def on_upload_completado(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            ruta_temp = os.path.join(UPLOAD_DIR, e.file_name)
            try:
                if os.path.exists(ruta_temp):
                    cargar_desde_ruta_local(ruta_temp, e.file_name)
            except Exception as ex:
                mostrar_snack(f"Error al procesar archivo: {ex}", es_error=True)

    file_picker_importar = ft.FilePicker()
    file_picker_importar.on_upload = on_upload_completado

    file_picker_exportar = ft.FilePicker()
    page.services.extend([file_picker_importar, file_picker_exportar])

    async def importar_archivo_click(e):
        try:
            archivos = await file_picker_importar.pick_files(
                allowed_extensions=["jff", "json", "xml"],
                allow_multiple=False,
                dialog_title="Seleccione autómata (.jff, .json, .xml)",
            )
            if not archivos:
                return

            archivo = archivos[0]
            if getattr(archivo, "path", None):
                cargar_desde_ruta_local(archivo.path, archivo.name)
                return

            upload_url = page.get_upload_url(archivo.name, 600)
            await file_picker_importar.upload(
                [ft.FilePickerUploadFile(name=archivo.name, upload_url=upload_url)]
            )
        except Exception as ex:
            mostrar_snack(f"Error al importar archivo: {ex}", es_error=True)

    async def exportar_automata(formato: str):
        nonlocal automata_actual
        if not automata_actual.estados:
            mostrar_snack("No hay autómata definido para exportar.", es_error=True)
            return

        nombre_archivo = f"automata_exportado.{formato}"
        ruta_temp = os.path.join(UPLOAD_DIR, nombre_archivo)
        try:
            if formato == "jff":
                FormatosAutomata.guardar_jff(automata_actual, ruta_temp)
            elif formato == "json":
                FormatosAutomata.guardar_json(automata_actual, ruta_temp)
            elif formato == "xml":
                FormatosAutomata.guardar_xml(automata_actual, ruta_temp)

            with open(ruta_temp, "rb") as f:
                contenido_bytes = f.read()

            await file_picker_exportar.save_file(
                dialog_title=f"Descargar autómata (.{formato})",
                file_name=nombre_archivo,
                src_bytes=contenido_bytes,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[formato],
            )
            mostrar_snack(f"Descarga de '{nombre_archivo}' iniciada.")
        except Exception as ex:
            mostrar_snack(f"Error al exportar: {ex}", es_error=True)

    def limpiar_simulador(e):
        nonlocal automata_actual, traza_actual, indice_paso_actual
        automata_actual = Automata()
        traza_actual = []
        indice_paso_actual = 0
        tf_estados.value = ""
        tf_alfabeto.value = ""
        tf_inicial.value = ""
        tf_aceptacion.value = ""
        tf_trans_origen.value = ""
        tf_trans_simbolo.value = ""
        tf_trans_destino.value = ""
        tf_cadena_simular.value = ""
        banner_transicion_paso.visible = False

        establecer_bloqueo_manual(False)

        txt_resultado_sim.value = "Define o importa un autómata e ingresa una cadena para simular."
        txt_resultado_sim.color = None
        btn_paso_anterior.disabled = True
        btn_paso_siguiente.disabled = True
        txt_contador_pasos.value = "Paso: - / -"
        actualizar_resumen_quintupla()
        txt_salida_unificada.value = "Aquí se mostrará la traza paso a paso de la simulación."
        page.update()

    # -------------------------------------------------------------------------
    # Ensamblado Visual
    # -------------------------------------------------------------------------
    recuadro_quintupla = ft.Container(
        padding=14,
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        content=ft.Column(
            [
                ft.Row(
                    [
                        titulo_quintupla_manual,
                        badge_bloqueo_archivo,
                    ],
                    wrap=True,
                    spacing=12,
                ),
                ft.Row([tf_estados, tf_alfabeto], spacing=10),
                ft.Row(
                    [
                        tf_inicial,
                        tf_aceptacion,
                        btn_aplicar_quintupla,
                    ],
                    spacing=10,
                ),
                ft.Row(
                    [
                        tf_trans_origen,
                        tf_trans_simbolo,
                        tf_trans_destino,
                        btn_agregar_transicion,
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        ),
    )

    # Inicializar panel gráfico vacío
    refrescar_panel_estados_y_transiciones()

    return ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Icon(ft.Icons.PLAY_CIRCLE, size=28, color=ft.Colors.GREEN_400),
                    ft.Column(
                        [
                            ft.Text(
                                "Práctica 2: Simulador Interactivo de Autómatas Finitos",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Visor gráfico vectorial con resaltado de transiciones paso a paso y tabla formal δ.",
                                size=12,
                                color=ft.Colors.GREY_400,
                            ),
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
                            ft.Container(
                                content=txt_estado_quintupla,
                                padding=10,
                                border_radius=6,
                                bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN_400),
                                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                            ),
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Subir Autómata (.jff / .json / .xml)",
                                        icon=ft.Icons.UPLOAD_FILE,
                                        on_click=importar_archivo_click,
                                    ),
                                    ft.OutlinedButton(
                                        "Descargar .JFF",
                                        icon=ft.Icons.DOWNLOAD,
                                        on_click=lambda _: page.run_task(exportar_automata, "jff"),
                                    ),
                                    ft.OutlinedButton(
                                        "Descargar .JSON",
                                        icon=ft.Icons.DOWNLOAD,
                                        on_click=lambda _: page.run_task(exportar_automata, "json"),
                                    ),
                                    ft.OutlinedButton(
                                        "Descargar .XML",
                                        icon=ft.Icons.DOWNLOAD,
                                        on_click=lambda _: page.run_task(exportar_automata, "xml"),
                                    ),
                                    ft.TextButton(
                                        "Limpiar",
                                        icon=ft.Icons.RESTORE,
                                        on_click=limpiar_simulador,
                                    ),
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                            recuadro_quintupla,
                            # Barra de simulación justo encima del visor gráfico para ver cada transición al instante
                            ft.Row(
                                [
                                    tf_cadena_simular,
                                    ft.Button(
                                        "Simular Cadena",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=ejecutar_simulacion_completa,
                                    ),
                                    btn_paso_anterior,
                                    txt_contador_pasos,
                                    btn_paso_siguiente,
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                            txt_resultado_sim,
                            banner_transicion_paso,
                            contenedor_visualizador_grafo_tabla,
                        ],
                        spacing=12,
                    ),
                )
            ),
            ft.Text("Detalle de la Traza Paso a Paso:", weight=ft.FontWeight.BOLD, size=14),
            ft.Container(
                content=ft.SelectionArea(
                    content=ft.Column([txt_salida_unificada], scroll=ft.ScrollMode.AUTO)
                ),
                padding=16,
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


def main_standalone(page: ft.Page):
    page.title = "Simulador de Autómatas Finitos"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK
    page.add(crear_vista_simulador(page))


if __name__ == "__main__":
    os.environ.setdefault("FLET_SECRET_KEY", "teoria-computacion-escom-2026")
    ft.run(main_standalone, upload_dir=UPLOAD_DIR)