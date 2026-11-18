"""
===============================================================================
MÓDULO DE INTERFAZ GRÁFICA PARA EL SIMULADOR DE AUTÓMATAS FINITOS (FLET)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación
Institución: Escuela Superior de Cómputo (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Implementa la vista gráfica interactiva para el simulador de autómatas finitos
    en Flet con estética moderna Material Design 3 y compatibilidad total con
    entornos web en contenedores Docker y escritorios locales:
      - Definición interactiva de estados, alfabeto, estado inicial y aceptación (3.1).
      - Visualización y actualización dinámica de la tabla de transiciones (3.1).
      - Carga multiformato desde .jff (JFLAP), .json y .xml mediante:
          * Carga por archivo en servidor web (FilePicker con upload_dir).
          * Cuadro interactivo para pegar contenido directamente.
          * Selector de ejemplos precargados desde automatas/.
      - Exportación multiformato a .jff, .json y .xml con descarga directa y copia
        al portapapeles.
      - Simulación paso a paso con traza de bifurcaciones y lambda-clausuras (3.3).
      - Compatibilidad completa desacoplada con automata.py y formatos.py.
===============================================================================
"""

from __future__ import annotations
import os
from typing import Optional
import flet as ft
from automata import Automata
from formatos import FormatosAutomata

# Directorio de carga y almacenamiento compartido
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def crear_vista_simulador(page: ft.Page) -> ft.Control:
    """
    Construye y retorna el componente visual interactivo del simulador de autómatas.
    Soporta ejecución en escritorio y en navegador web dentro de contenedores.
    """
    automata_actual: Automata = Automata()
    traza_actual: list = []
    indice_paso_actual: int = 0

    # -------------------------------------------------------------------------
    # 1. Utilidades y Notificaciones
    # -------------------------------------------------------------------------
    def mostrar_snack(mensaje: str, color: str = ft.Colors.BLUE_GREY_800) -> None:
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=3500
        )
        if hasattr(page, "open"):
            page.open(snack)
        else:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    # -------------------------------------------------------------------------
    # 2. Encabezado y Badges de Estado Formal
    # -------------------------------------------------------------------------
    txt_titulo = ft.Text(
        "Simulador de Autómatas Finitos",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY
    )
    txt_subtitulo = ft.Text(
        "Reconocimiento de modelos formales (AFD, AFND y AFND-λ) con traza de ejecución",
        size=13,
        color=ft.Colors.OUTLINE
    )

    badge_tipo = ft.Container(
        content=ft.Text("TIPO: NINGUNO", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=16,
        bgcolor=ft.Colors.GREY_600
    )

    chip_estados = ft.Chip(label=ft.Text("|Q| = 0"), leading=ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED, size=16))
    chip_alfabeto = ft.Chip(label=ft.Text("|Σ| = 0"), leading=ft.Icon(ft.Icons.SPELLCHECK, size=16))
    chip_inicial = ft.Chip(label=ft.Text("q0 = ∅"), leading=ft.Icon(ft.Icons.PLAY_ARROW, size=16))
    chip_finales = ft.Chip(label=ft.Text("|F| = 0"), leading=ft.Icon(ft.Icons.FLAG, size=16))
    chip_transiciones = ft.Chip(label=ft.Text("|δ| = 0"), leading=ft.Icon(ft.Icons.SWAP_HORIZ, size=16))

    fila_chips_resumen = ft.Row(
        controls=[chip_estados, chip_alfabeto, chip_inicial, chip_finales, chip_transiciones],
        wrap=True,
        spacing=8
    )

    txt_quintupla = ft.Text(
        "M = (Q, Σ, δ, q0, F)\nCargue un archivo, seleccione un ejemplo o defina la quíntupla manualmente.",
        size=12,
        font_family="monospace",
        selectable=True
    )

    card_resumen_quintupla = ft.Card(
        elevation=2,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HUB, color=ft.Colors.PRIMARY),
                    ft.Text("Quíntupla Formal del Autómata", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    badge_tipo
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10),
                fila_chips_resumen,
                ft.Container(
                    content=txt_quintupla,
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
                )
            ], spacing=10)
        )
    )

    # -------------------------------------------------------------------------
    # 3. Campos de Entrada para Definición Interactiva (Ejercicio 3.1)
    # -------------------------------------------------------------------------
    tf_estados = ft.TextField(
        label="Estados Q (ej. q0, q1, q2)",
        hint_text="Separados por comas",
        dense=True,
        expand=True,
        border_radius=8,
        prefix_icon=ft.Icons.RADIO_BUTTON_CHECKED
    )
    tf_alfabeto = ft.TextField(
        label="Alfabeto Σ (ej. 0, 1 o a, b)",
        hint_text="Separados por comas",
        dense=True,
        expand=True,
        border_radius=8,
        prefix_icon=ft.Icons.SPELLCHECK
    )
    tf_inicial = ft.TextField(
        label="Estado Inicial q0 (ej. q0)",
        dense=True,
        width=170,
        border_radius=8,
        prefix_icon=ft.Icons.PLAY_ARROW
    )
    tf_aceptacion = ft.TextField(
        label="Estados Aceptación F (ej. q1, q2)",
        hint_text="Separados por comas",
        dense=True,
        expand=True,
        border_radius=8,
        prefix_icon=ft.Icons.FLAG
    )

    tf_trans_origen = ft.TextField(
        label="Origen q_i",
        dense=True,
        width=120,
        border_radius=8,
        hint_text="ej. q0"
    )
    tf_trans_simbolo = ft.TextField(
        label="Símbolo (vacío = λ)",
        dense=True,
        width=150,
        border_radius=8,
        hint_text="ej. 0 o λ"
    )
    tf_trans_destino = ft.TextField(
        label="Destino q_j",
        dense=True,
        width=120,
        border_radius=8,
        hint_text="ej. q1"
    )

    tabla_transiciones_col = ft.Column(scroll=ft.ScrollMode.AUTO)

    # -------------------------------------------------------------------------
    # 4. Componentes para Simulación y Traza Paso a Paso (Ejercicio 3.3)
    # -------------------------------------------------------------------------
    tf_cadena_simular = ft.TextField(
        label="Cadena de entrada w",
        hint_text="ej. 001001 o vacío para λ",
        dense=True,
        expand=True,
        border_radius=8,
        prefix_icon=ft.Icons.KEYBOARD
    )

    banner_resultado_sim = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE_GREY_400),
            ft.Text("Ingrese una cadena y pulse 'Simular Cadena'", weight=ft.FontWeight.W_500)
        ]),
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
    )

    txt_traza_detallada = ft.Text(
        value="La traza detallada paso a paso se mostrará aquí una vez iniciada la simulación.",
        size=12,
        font_family="monospace",
        selectable=True
    )

    btn_paso_inicio = ft.IconButton(
        icon=ft.Icons.FIRST_PAGE,
        tooltip="Paso inicial",
        disabled=True
    )
    btn_paso_anterior = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Paso anterior",
        disabled=True
    )
    btn_paso_siguiente = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD,
        tooltip="Paso siguiente",
        disabled=True
    )
    btn_paso_fin = ft.IconButton(
        icon=ft.Icons.LAST_PAGE,
        tooltip="Paso final",
        disabled=True
    )
    txt_contador_pasos = ft.Text(value="Paso: - / -", size=13, weight=ft.FontWeight.BOLD)

    # -------------------------------------------------------------------------
    # 5. Sincronización y Actualización de la Quíntupla
    # -------------------------------------------------------------------------
    def actualizar_resumen_quintupla() -> None:
        nonlocal automata_actual
        q_list = sorted(list(automata_actual.estados))
        sig_list = sorted(list(automata_actual.alfabeto))
        f_list = sorted(list(automata_actual.estados_aceptacion))
        q0 = automata_actual.estado_inicial or "∅"

        automata_actual._actualizar_tipo()
        tipo = automata_actual.tipo or "Ninguno"

        # Colores por tipo de autómata
        if tipo == "AFD":
            bg_color = ft.Colors.TEAL_600
        elif tipo == "AFND":
            bg_color = ft.Colors.AMBER_800
        elif tipo == "AFND-lambda" or tipo == "AFND-λ":
            bg_color = ft.Colors.DEEP_PURPLE_600
        else:
            bg_color = ft.Colors.GREY_600

        badge_tipo.content.value = f"TIPO: {tipo}"
        badge_tipo.bgcolor = bg_color

        chip_estados.label.value = f"|Q| = {len(q_list)}"
        chip_alfabeto.label.value = f"|Σ| = {len(sig_list)}"
        chip_inicial.label.value = f"q0 = {q0}"
        chip_finales.label.value = f"|F| = {len(f_list)}"
        chip_transiciones.label.value = f"|δ| = {len(automata_actual.transiciones)}"

        q_str = "{" + ", ".join(q_list) + "}"
        sig_str = "{" + ", ".join(sig_list) + "}"
        f_str = "{" + ", ".join(f_list) + "}"

        txt_quintupla.value = (
            f"Q  = {q_str}\n"
            f"Σ  = {sig_str}\n"
            f"q0 = {q0}\n"
            f"F  = {f_str}"
        )

        # Generar filas de la tabla de transiciones
        filas = []
        tabla_dict = automata_actual.obtener_tabla_transiciones()
        for orig in q_list:
            trans_dict = tabla_dict.get(orig, {})
            dest_strs = []
            for simb, dests in sorted(trans_dict.items()):
                label_simb = simb if simb else "λ"
                dest_strs.append(f"δ({orig}, '{label_simb}') → {{{', '.join(sorted(list(dests)))}}}")

            es_ini = orig == automata_actual.estado_inicial
            es_fin = orig in automata_actual.estados_aceptacion
            prefijo = ""
            if es_ini and es_fin:
                prefijo = "→ * "
            elif es_ini:
                prefijo = "→ "
            elif es_fin:
                prefijo = "* "

            filas.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{prefijo}{orig}", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(";  ".join(dest_strs) if dest_strs else "∅ (Sin transiciones)"))
                ])
            )

        if not filas:
            tabla_transiciones_col.controls = [
                ft.Container(
                    content=ft.Text("No hay transiciones registradas todavía.", color=ft.Colors.OUTLINE),
                    padding=15
                )
            ]
        else:
            tabla_transiciones_col.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Transiciones δ(q, a)", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=filas,
                    dense=True,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    vertical_lines=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    horizontal_lines=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST
                )
            ]
        page.update()

    def aplicar_definicion_manual(e) -> None:
        """Aplica y valida los datos de estados y alfabeto ingresados interactivamente."""
        nonlocal automata_actual
        auto = Automata()

        estados = [x.strip() for x in (tf_estados.value or "").split(",") if x.strip()]
        alfabeto = [x.strip() for x in (tf_alfabeto.value or "").split(",") if x.strip()]
        inicial = (tf_inicial.value or "").strip() or None
        aceptacion = [x.strip() for x in (tf_aceptacion.value or "").split(",") if x.strip()]

        if not estados:
            mostrar_snack("Debe especificar al menos un estado en Q.", ft.Colors.RED_700)
            return

        for q in estados:
            auto.agregar_estado(q, es_inicial=(q == inicial), es_final=(q in aceptacion))
        for a in alfabeto:
            auto.agregar_simbolo(a)

        # Conservar transiciones si los estados existen
        for t in automata_actual.transiciones:
            if t.origen in auto.estados and t.destino in auto.estados:
                auto.agregar_transicion(t.origen, t.simbolo, t.destino)

        automata_actual = auto
        actualizar_resumen_quintupla()
        mostrar_snack("Quíntupla formal actualizada con éxito.", ft.Colors.GREEN_700)

    def agregar_transicion_click(e) -> None:
        """Registra una nueva transición delta(origen, símbolo) -> destino."""
        nonlocal automata_actual
        orig = (tf_trans_origen.value or "").strip()
        simb = (tf_trans_simbolo.value or "").strip()
        dest = (tf_trans_destino.value or "").strip()

        if not orig or not dest:
            mostrar_snack("Debe especificar estado de origen y de destino.", ft.Colors.RED_700)
            return

        # Normalizar símbolo lambda
        if simb.lower() in ("lambda", "epsilon", "λ", "ε"):
            simb = ""

        automata_actual.agregar_transicion(orig, simb, dest)
        tf_trans_simbolo.value = ""
        actualizar_resumen_quintupla()
        mostrar_snack(f"Transición δ({orig}, '{simb or 'λ'}') → {dest} agregada.", ft.Colors.GREEN_700)

    def limpiar_transiciones_click(e) -> None:
        nonlocal automata_actual
        automata_actual.transiciones.clear()
        actualizar_resumen_quintupla()
        mostrar_snack("Transiciones eliminadas.", ft.Colors.BLUE_GREY_700)

    def reiniciar_automata_click(e) -> None:
        nonlocal automata_actual, traza_actual, indice_paso_actual
        automata_actual = Automata()
        traza_actual = []
        indice_paso_actual = 0
        tf_estados.value = ""
        tf_alfabeto.value = ""
        tf_inicial.value = ""
        tf_aceptacion.value = ""
        tf_cadena_simular.value = ""
        txt_traza_detallada.value = "La traza detallada paso a paso se mostrará aquí una vez iniciada la simulación."
        banner_resultado_sim.content = ft.Row([
            ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE_GREY_400),
            ft.Text("Ingrese una cadena y pulse 'Simular Cadena'", weight=ft.FontWeight.W_500)
        ])
        banner_resultado_sim.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        btn_paso_inicio.disabled = True
        btn_paso_anterior.disabled = True
        btn_paso_siguiente.disabled = True
        btn_paso_fin.disabled = True
        txt_contador_pasos.value = "Paso: - / -"
        actualizar_resumen_quintupla()
        mostrar_snack("Autómata reiniciado completamente.", ft.Colors.BLUE_GREY_700)

    # -------------------------------------------------------------------------
    # 6. Simulación y Motor de Traza Paso a Paso
    # -------------------------------------------------------------------------
    def ejecutar_simulacion_completa(e) -> None:
        nonlocal automata_actual, traza_actual, indice_paso_actual
        if not automata_actual.estados:
            mostrar_snack("Debe definir o cargar un autómata antes de simular.", ft.Colors.RED_700)
            return

        cadena = tf_cadena_simular.value or ""
        aceptada, traza = automata_actual.simular_cadena(cadena)
        traza_actual = traza
        indice_paso_actual = len(traza) - 1 if traza else 0

        if aceptada:
            banner_resultado_sim.bgcolor = ft.Colors.GREEN_700
            banner_resultado_sim.content = ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=24),
                ft.Column([
                    ft.Text("CADENA ACEPTADA", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=15),
                    ft.Text(f"La cadena '{cadena or 'λ'}' pertenece al lenguaje formal L(M).", color=ft.Colors.WHITE, size=12)
                ], spacing=2)
            ])
        else:
            banner_resultado_sim.bgcolor = ft.Colors.RED_700
            banner_resultado_sim.content = ft.Row([
                ft.Icon(ft.Icons.CANCEL, color=ft.Colors.WHITE, size=24),
                ft.Column([
                    ft.Text("CADENA RECHAZADA", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=15),
                    ft.Text(f"La cadena '{cadena or 'λ'}' NO pertenece al lenguaje formal L(M).", color=ft.Colors.WHITE, size=12)
                ], spacing=2)
            ])

        mostrar_paso_actual()

    def mostrar_paso_actual() -> None:
        nonlocal traza_actual, indice_paso_actual
        if not traza_actual:
            txt_traza_detallada.value = "Sin traza de ejecución disponible."
            btn_paso_inicio.disabled = True
            btn_paso_anterior.disabled = True
            btn_paso_siguiente.disabled = True
            btn_paso_fin.disabled = True
            txt_contador_pasos.value = "Paso: - / -"
            page.update()
            return

        paso = traza_actual[indice_paso_actual]
        num_paso = paso.get("paso", 0)
        total_pasos = len(traza_actual) - 1

        btn_paso_inicio.disabled = (indice_paso_actual == 0)
        btn_paso_anterior.disabled = (indice_paso_actual == 0)
        btn_paso_siguiente.disabled = (indice_paso_actual == total_pasos)
        btn_paso_fin.disabled = (indice_paso_actual == total_pasos)
        txt_contador_pasos.value = f"Paso {num_paso} de {total_pasos}"

        lineas = [
            f"┌── DETALLE DE EJECUCIÓN (PASO {num_paso} DE {total_pasos}) ──",
            f"│ Símbolo leído:       {paso.get('simbolo_leido', 'λ (Inicio)')}",
            f"│ Estados previos:     {sorted(list(paso.get('estados_previos', [])))}",
            f"│ λ-clausura previa:   {sorted(list(paso.get('clausura_previa', [])))}",
            f"│ Transiciones:        {paso.get('transiciones_tomadas', [])}",
            f"│ Destinos directos:   {sorted(list(paso.get('estados_posteriores', [])))}",
            f"│ λ-clausura final:    {sorted(list(paso.get('clausura_posterior', [])))}",
            f"│ ¿Alcanza aceptación? {'SÍ' if paso.get('es_aceptacion') else 'NO'}",
            f"└─────────────────────────────────────────────────────────────"
        ]
        if "error" in paso:
            lineas.append(f"⚠️ AVISO / ERROR: {paso['error']}")

        txt_traza_detallada.value = "\n".join(lineas)
        page.update()

    def ir_paso_inicio(e) -> None:
        nonlocal indice_paso_actual
        indice_paso_actual = 0
        mostrar_paso_actual()

    def ir_paso_anterior(e) -> None:
        nonlocal indice_paso_actual
        if indice_paso_actual > 0:
            indice_paso_actual -= 1
            mostrar_paso_actual()

    def ir_paso_siguiente(e) -> None:
        nonlocal indice_paso_actual, traza_actual
        if indice_paso_actual < len(traza_actual) - 1:
            indice_paso_actual += 1
            mostrar_paso_actual()

    def ir_paso_fin(e) -> None:
        nonlocal indice_paso_actual, traza_actual
        if traza_actual:
            indice_paso_actual = len(traza_actual) - 1
            mostrar_paso_actual()

    btn_paso_inicio.on_click = ir_paso_inicio
    btn_paso_anterior.on_click = ir_paso_anterior
    btn_paso_siguiente.on_click = ir_paso_siguiente
    btn_paso_fin.on_click = ir_paso_fin

    # -------------------------------------------------------------------------
    # 7. Carga y Deserialización de Autómatas (Web / Contenedor & Desktop)
    # -------------------------------------------------------------------------
    def sincronizar_modelo_a_ui(auto: Automata, nombre_fuente: str = "") -> None:
        nonlocal automata_actual
        automata_actual = auto
        tf_estados.value = ", ".join(sorted(list(auto.estados)))
        tf_alfabeto.value = ", ".join(sorted(list(auto.alfabeto)))
        tf_inicial.value = auto.estado_inicial or ""
        tf_aceptacion.value = ", ".join(sorted(list(auto.estados_aceptacion)))
        actualizar_resumen_quintupla()
        if nombre_fuente:
            mostrar_snack(f"Autómata importado exitosamente desde '{nombre_fuente}'.", ft.Colors.GREEN_700)

    def cargar_desde_archivo_o_texto(origen: str, nombre_fuente: str = "") -> None:
        try:
            contenido = origen
            ext = ""
            if os.path.exists(origen):
                ext = os.path.splitext(origen)[1].lower()
                with open(origen, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()
            elif nombre_fuente:
                ext = os.path.splitext(nombre_fuente)[1].lower()

            contenido_strip = contenido.strip()
            # Detección por extensión o por estructura de contenido
            if ext == ".json" or (contenido_strip.startswith("{") and "transiciones" in contenido_strip):
                nuevo_auto = FormatosAutomata.cargar_json(contenido)
            elif ext == ".xml" or (contenido_strip.startswith("<automata") or "<alfabeto>" in contenido_strip):
                nuevo_auto = FormatosAutomata.cargar_xml(contenido)
            elif ext == ".jff" or "<structure>" in contenido_strip or "<automaton>" in contenido_strip:
                nuevo_auto = FormatosAutomata.cargar_jff(contenido)
            else:
                # Intentar heurística JFF -> JSON -> XML
                try:
                    nuevo_auto = FormatosAutomata.cargar_jff(contenido)
                except Exception:
                    try:
                        nuevo_auto = FormatosAutomata.cargar_json(contenido)
                    except Exception:
                        nuevo_auto = FormatosAutomata.cargar_xml(contenido)

            sincronizar_modelo_a_ui(nuevo_auto, nombre_fuente or "Contenido procesado")
        except Exception as ex:
            mostrar_snack(f"Error al procesar autómata: {ex}", ft.Colors.RED_700)

    # 7.1 Manejo de FilePicker compatible con Servidor Web en Contenedores
    def on_archivo_seleccionado(e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        f = e.files[0]
        # Si estamos en modo de escritorio nativo con ruta válida
        if f.path and os.path.exists(f.path):
            cargar_desde_archivo_o_texto(f.path, os.path.basename(f.path))
        else:
            # Modo Servidor Web en Contenedor Docker:
            # e.files[0].path es None, debemos activar la subida vía get_upload_url
            try:
                upload_url = page.get_upload_url(f.name, 600)
                file_picker_importar.upload([
                    ft.FilePickerUploadFile(
                        name=f.name,
                        upload_url=upload_url
                    )
                ])
                mostrar_snack(f"Cargando '{f.name}' en el contenedor...", ft.Colors.BLUE_700)
            except Exception as ex:
                mostrar_snack(f"Error al iniciar carga web: {ex}", ft.Colors.RED_700)

    def on_archivo_subido(e: ft.FilePickerUploadEvent) -> None:
        if getattr(e, "error", None):
            mostrar_snack(f"Error en la subida: {e.error}", ft.Colors.RED_700)
            return

        # Cuando la subida se completa
        nombre = getattr(e, "file_name", None)
        if not nombre:
            # Fallback en caso de que e tenga otra propiedad
            nombre = getattr(e, "name", None)

        if nombre:
            ruta_servidor = os.path.join(UPLOAD_DIR, nombre)
            if os.path.exists(ruta_servidor):
                cargar_desde_archivo_o_texto(ruta_servidor, nombre)

    file_picker_importar = ft.FilePicker()
    file_picker_importar.on_result = on_archivo_seleccionado
    file_picker_importar.on_upload = on_archivo_subido
    page.services.append(file_picker_importar)

    # 7.2 Modal para Pegar Código Directamente (Garantía contra restricciones de sandbox)
    tf_pegar_contenido = ft.TextField(
        label="Pegar contenido (.jff, .json, .xml)",
        multiline=True,
        min_lines=8,
        max_lines=15,
        dense=True,
        border_radius=8,
        font_family="monospace"
    )

    def cerrar_dialogo_pegar(e=None) -> None:
        dialogo_pegar.open = False
        page.update()

    def procesar_pegar_click(e) -> None:
        texto = tf_pegar_contenido.value or ""
        if not texto.strip():
            mostrar_snack("Debe pegar el contenido de un autómata.", ft.Colors.RED_700)
            return
        cerrar_dialogo_pegar()
        cargar_desde_archivo_o_texto(texto, "Texto Pegado")

    dialogo_pegar = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.CODE), ft.Text("Importar desde Código / Texto")]),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Pegue a continuación la definición formal en formato XML (JFLAP .jff), JSON estructurado o XML canónico:"),
                tf_pegar_contenido
            ], tight=True, spacing=10),
            width=550
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_pegar),
            ft.ElevatedButton("Importar Contenido", icon=ft.Icons.CHECK, on_click=procesar_pegar_click)
        ]
    )

    def abrir_dialogo_pegar(e) -> None:
        tf_pegar_contenido.value = ""
        if hasattr(page, "open"):
            page.open(dialogo_pegar)
        else:
            page.dialog = dialogo_pegar
            dialogo_pegar.open = True
        page.update()

    # 7.3 Carga de Ejemplos Precargados desde el Repositorio
    def cargar_ejemplo_precargado(ruta_relativa: str, descripcion: str) -> None:
        ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
        if os.path.exists(ruta_completa):
            cargar_desde_archivo_o_texto(ruta_completa, descripcion)
        else:
            mostrar_snack(f"No se encontró el archivo de ejemplo en '{ruta_relativa}'", ft.Colors.RED_700)

    # -------------------------------------------------------------------------
    # 8. Exportación Multiformato (.jff, .json, .xml) con Descarga y Copia
    # -------------------------------------------------------------------------
    tf_exportar_preview = ft.TextField(
        label="Contenido Generado",
        multiline=True,
        min_lines=10,
        max_lines=18,
        read_only=True,
        dense=True,
        border_radius=8,
        font_family="monospace"
    )

    def cerrar_dialogo_exportar(e=None) -> None:
        dialogo_exportar.open = False
        page.update()

    def copiar_exportado_clipboard(e) -> None:
        if tf_exportar_preview.value:
            page.set_clipboard(tf_exportar_preview.value)
            mostrar_snack("¡Contenido copiado al portapapeles!", ft.Colors.GREEN_700)

    def descargar_exportado_click(e) -> None:
        nombre_arch = getattr(dialogo_exportar, "_nombre_archivo_actual", "automata_exportado.txt")
        # Abrir la URL servida desde uploads / assets
        try:
            page.launch_url(f"/{nombre_arch}")
            mostrar_snack(f"Descargando '{nombre_arch}'...", ft.Colors.GREEN_700)
        except Exception as ex:
            mostrar_snack(f"Error al solicitar descarga: {ex}", ft.Colors.RED_700)

    dialogo_exportar = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.DOWNLOAD), ft.Text("Exportar Autómata")]),
        content=ft.Container(
            content=ft.Column([
                ft.Text("A continuación se muestra la serialización formal generada. Puede copiarla directamente o descargar el archivo:"),
                tf_exportar_preview
            ], tight=True, spacing=10),
            width=580
        ),
        actions=[
            ft.TextButton("Copiar al Portapapeles", icon=ft.Icons.COPY, on_click=copiar_exportado_clipboard),
            ft.ElevatedButton("Descargar Archivo", icon=ft.Icons.DOWNLOAD, on_click=descargar_exportado_click),
            ft.TextButton("Cerrar", on_click=cerrar_dialogo_exportar)
        ]
    )

    def exportar_automata(formato: str) -> None:
        nonlocal automata_actual
        if not automata_actual.estados:
            mostrar_snack("No hay ningún autómata definido para exportar.", ft.Colors.RED_700)
            return

        nombre_archivo = f"automata_exportado.{formato}"
        ruta_salida = os.path.join(UPLOAD_DIR, nombre_archivo)
        dialogo_exportar._nombre_archivo_actual = nombre_archivo

        try:
            if formato == "jff":
                contenido = FormatosAutomata.a_jff_str(automata_actual)
            elif formato == "json":
                contenido = FormatosAutomata.a_json_str(automata_actual)
            elif formato == "xml":
                contenido = FormatosAutomata.a_xml_str(automata_actual)
            else:
                mostrar_snack(f"Formato '{formato}' no soportado.", ft.Colors.RED_700)
                return

            with open(ruta_salida, "w", encoding="utf-8") as f:
                f.write(contenido)

            # También guardar en directorio raíz si es posible para entorno de pruebas
            try:
                with open(os.path.join(BASE_DIR, nombre_archivo), "w", encoding="utf-8") as f:
                    f.write(contenido)
            except Exception:
                pass

            tf_exportar_preview.value = contenido
            dialogo_exportar.title.controls[1].value = f"Exportar Autómata (Formato .{formato.upper()})"

            if hasattr(page, "open"):
                page.open(dialogo_exportar)
            else:
                page.dialog = dialogo_exportar
                dialogo_exportar.open = True
            page.update()

        except Exception as ex:
            mostrar_snack(f"Error al exportar: {ex}", ft.Colors.RED_700)

    # -------------------------------------------------------------------------
    # 9. Barra de Herramientas de Carga, Ejemplos y Exportación
    # -------------------------------------------------------------------------
    btn_subir_archivo = ft.ElevatedButton(
        "Subir Archivo",
        icon=ft.Icons.UPLOAD_FILE,
        tooltip="Cargar archivo .jff, .json o .xml desde su equipo",
        on_click=lambda _: file_picker_importar.pick_files(
            allowed_extensions=["jff", "json", "xml"],
            dialog_title="Seleccione autómata (.jff, .json, .xml)"
        )
    )

    btn_pegar_codigo = ft.OutlinedButton(
        "Pegar Código",
        icon=ft.Icons.CODE,
        tooltip="Pegar texto XML o JSON directamente",
        on_click=abrir_dialogo_pegar
    )

    btn_ejemplos_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.LIGHTBULB_OUTLINE), ft.Text("AFD: Paridad Ceros (102.jff)")]),
                on_click=lambda _: cargar_ejemplo_precargado("automatas/102.jff", "102.jff (AFD Paridad)")
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.LIGHTBULB_OUTLINE), ft.Text("AFND: Cadenas '01' (106.jff)")]),
                on_click=lambda _: cargar_ejemplo_precargado("automatas/106.jff", "106.jff (AFND '01')")
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.LIGHTBULB_OUTLINE), ft.Text("AFND-λ: Ciclos λ (148.jff)")]),
                on_click=lambda _: cargar_ejemplo_precargado("automatas/148.jff", "148.jff (AFND-λ)")
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.GAMES), ft.Text("Pac-Man Extendido (pacman_extended.jff)")]),
                on_click=lambda _: cargar_ejemplo_precargado("automatas/aplicacion/pacman_extended.jff", "Pac-Man 6 Estados")
            ),
        ],
        icon=ft.Icons.FOLDER_OPEN,
        tooltip="Cargar Ejemplo Precargado"
    )

    btn_exportar_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.FILE_DOWNLOAD), ft.Text("Exportar .JFF (JFLAP 7.1)")]),
                on_click=lambda _: exportar_automata("jff")
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.FILE_DOWNLOAD), ft.Text("Exportar .JSON Estructurado")]),
                on_click=lambda _: exportar_automata("json")
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.FILE_DOWNLOAD), ft.Text("Exportar .XML Canónico")]),
                on_click=lambda _: exportar_automata("xml")
            ),
        ],
        icon=ft.Icons.DOWNLOAD,
        tooltip="Exportar Autómata en Formato Oficial"
    )

    btn_reiniciar = ft.IconButton(
        icon=ft.Icons.REPLAY,
        tooltip="Reiniciar Autómata",
        icon_color=ft.Colors.RED_400,
        on_click=reiniciar_automata_click
    )

    card_toolbar = ft.Card(
        elevation=1,
        content=ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row([
                btn_subir_archivo,
                btn_pegar_codigo,
                ft.VerticalDivider(width=1),
                ft.Text("Ejemplos:", size=13, weight=ft.FontWeight.W_500),
                btn_ejemplos_menu,
                ft.VerticalDivider(width=1),
                ft.Text("Exportar:", size=13, weight=ft.FontWeight.W_500),
                btn_exportar_menu,
                ft.Container(expand=True),
                btn_reiniciar
            ], wrap=True, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )
    )

    # -------------------------------------------------------------------------
    # 10. Panel de Definición Interactiva (Q, Sigma, q0, F, delta)
    # -------------------------------------------------------------------------
    panel_definicion = ft.ExpansionTile(
        title=ft.Row([
            ft.Icon(ft.Icons.EDIT_NOTE, color=ft.Colors.PRIMARY),
            ft.Text("1. Definición Interactiva de la Quíntupla", weight=ft.FontWeight.BOLD, size=14)
        ]),
        initially_expanded=False,
        controls=[
            ft.Container(
                padding=14,
                content=ft.Column([
                    ft.Row([tf_estados, tf_alfabeto]),
                    ft.Row([tf_inicial, tf_aceptacion]),
                    ft.Row([
                        ft.ElevatedButton(
                            "Actualizar Quíntupla",
                            icon=ft.Icons.CHECK,
                            on_click=aplicar_definicion_manual
                        )
                    ]),
                    ft.Divider(height=20),
                    ft.Text("Registrar Transición Individual δ(origen, símbolo) → destino:", weight=ft.FontWeight.BOLD, size=13),
                    ft.Row([
                        tf_trans_origen,
                        tf_trans_simbolo,
                        ft.IconButton(
                            icon=ft.Icons.EXPOSURE_ZERO,
                            tooltip="Insertar λ (Vacío)",
                            on_click=lambda _: setattr(tf_trans_simbolo, "value", "λ") or tf_trans_simbolo.update()
                        ),
                        tf_trans_destino,
                        ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=agregar_transicion_click),
                        ft.OutlinedButton("Limpiar δ", icon=ft.Icons.DELETE_SWEEP, on_click=limpiar_transiciones_click)
                    ], wrap=True)
                ], spacing=10)
            )
        ]
    )

    # -------------------------------------------------------------------------
    # 11. Panel de Tabla de Transiciones
    # -------------------------------------------------------------------------
    card_tabla = ft.Card(
        elevation=1,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TABLE_CHART, color=ft.Colors.PRIMARY),
                    ft.Text("2. Tabla de Transiciones δ(q, a)", size=15, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text("Convención: '→' Inicial, '*' Aceptación", size=11, color=ft.Colors.OUTLINE)
                ]),
                ft.Divider(height=10),
                tabla_transiciones_col
            ], spacing=8)
        )
    )

    # -------------------------------------------------------------------------
    # 12. Panel de Simulación y Traza Paso a Paso
    # -------------------------------------------------------------------------
    def insertar_simbolo_simular(s: str) -> None:
        if s == "λ":
            tf_cadena_simular.value = ""
        else:
            tf_cadena_simular.value = (tf_cadena_simular.value or "") + s
        tf_cadena_simular.update()

    card_simulacion = ft.Card(
        elevation=2,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PLAY_CIRCLE_FILLED, color=ft.Colors.PRIMARY),
                    ft.Text("3. Motor de Simulación y Traza de Ejecución", size=15, weight=ft.FontWeight.BOLD)
                ]),
                ft.Text("Ingrese la cadena a evaluar o use los accesos rápidos:", size=12, color=ft.Colors.OUTLINE),
                ft.Row([
                    tf_cadena_simular,
                    ft.OutlinedButton("λ (Vacía)", on_click=lambda _: insertar_simbolo_simular("λ")),
                    ft.OutlinedButton("0", on_click=lambda _: insertar_simbolo_simular("0")),
                    ft.OutlinedButton("1", on_click=lambda _: insertar_simbolo_simular("1")),
                    ft.IconButton(ft.Icons.BACKSPACE, tooltip="Limpiar cadena", on_click=lambda _: insertar_simbolo_simular("λ")),
                    ft.ElevatedButton(
                        "Simular Cadena",
                        icon=ft.Icons.PLAY_ARROW,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY),
                        on_click=ejecutar_simulacion_completa
                    )
                ], wrap=True),
                ft.Divider(height=10),
                banner_resultado_sim,
                ft.Divider(height=10),
                ft.Row([
                    ft.Text("Navegación de Pasos:", weight=ft.FontWeight.BOLD, size=13),
                    btn_paso_inicio,
                    btn_paso_anterior,
                    txt_contador_pasos,
                    btn_paso_siguiente,
                    btn_paso_fin
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=txt_traza_detallada,
                    padding=14,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
                )
            ], spacing=10)
        )
    )

    # -------------------------------------------------------------------------
    # 13. Ensamblado Final de la Vista
    # -------------------------------------------------------------------------
    vista_principal = ft.Column([
        txt_titulo,
        txt_subtitulo,
        card_toolbar,
        card_resumen_quintupla,
        panel_definicion,
        card_tabla,
        card_simulacion
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=16)

    # Inicializar con quíntupla vacía
    actualizar_resumen_quintupla()

    return vista_principal


def main_standalone(page: ft.Page) -> None:
    """Punto de entrada independiente para el simulador de autómatas."""
    page.title = "Simulador de Autómatas Finitos (P2)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.add(crear_vista_simulador(page))


if __name__ == "__main__":
    port = int(os.environ.get("FLET_SERVER_PORT", 8550))
    host = os.environ.get("FLET_SERVER_IP", "0.0.0.0")
    is_web = os.environ.get("FLET_FORCE_WEB_SERVER", "false").lower() in ("true", "1")
    if is_web:
        ft.run(main_standalone, host=host, port=port, upload_dir=UPLOAD_DIR, assets_dir=UPLOAD_DIR)
    else:
        ft.run(main_standalone, upload_dir=UPLOAD_DIR, assets_dir=UPLOAD_DIR)
