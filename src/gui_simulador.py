"""
Módulo de Interfaz Gráfica para el Simulador de Autómatas Finitos (Flet).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Vista y controladores para definición interactiva,
                importación/exportación multiformato (.jff, .json, .xml),
                simulación paso a paso con traza y visualización de la quíntupla.
"""

from __future__ import annotations
import os
import flet as ft
from automata import Automata
from formatos import FormatosAutomata


def crear_vista_simulador(page: ft.Page) -> ft.Control:
    """
    Construye y retorna el componente visual completo del simulador de autómatas.
    Totalmente desacoplado de la lógica del núcleo matemático.
    """
    # Estado interno del autómata en la interfaz
    automata_actual: Automata = Automata()
    traza_actual: list = []
    indice_paso_actual: int = 0

    # -------------------------------------------------------------------------
    # Componentes Visuales: Panel de Información y Quíntupla
    # -------------------------------------------------------------------------
    txt_titulo = ft.Text(
        "Simulador Interactivo de Autómatas Finitos (AFD / AFND / AFND-λ)",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_GREY_800
    )

    txt_quintupla = ft.Text(
        "M = (Q, Σ, δ, q0, F)\nCargue un archivo o defina el autómata manualmente.",
        size=12,
        font_family="monospace",
        color=ft.Colors.GREY_700
    )

    txt_tipo_auto = ft.Text("Tipo: Ninguno", weight=ft.FontWeight.W_500)

    # -------------------------------------------------------------------------
    # Componentes Visuales: Definición Interactiva
    # -------------------------------------------------------------------------
    tf_estados = ft.TextField(
        label="Estados Q (ej. q0, q1, q2)",
        hint_text="Separados por comas",
        dense=True,
        expand=True
    )
    tf_alfabeto = ft.TextField(
        label="Alfabeto Σ (ej. 0, 1 o a, b)",
        hint_text="Separados por comas",
        dense=True,
        expand=True
    )
    tf_inicial = ft.TextField(
        label="Estado Inicial q0 (ej. q0)",
        dense=True,
        width=160
    )
    tf_aceptacion = ft.TextField(
        label="Estados Aceptación F (ej. q1, q2)",
        hint_text="Separados por comas",
        dense=True,
        expand=True
    )

    # Definición de transiciones
    tf_trans_origen = ft.TextField(label="Origen", dense=True, width=100)
    tf_trans_simbolo = ft.TextField(
        label="Símbolo (vacío = λ)",
        dense=True,
        width=130
    )
    tf_trans_destino = ft.TextField(label="Destino", dense=True, width=100)

    # Contenedor para la tabla de transiciones
    tabla_transiciones_col = ft.Column(scroll=ft.ScrollMode.AUTO)

    # -------------------------------------------------------------------------
    # Componentes Visuales: Simulación y Traza
    # -------------------------------------------------------------------------
    tf_cadena_simular = ft.TextField(
        label="Cadena de entrada w",
        hint_text="ej. 001001 o vacío para λ",
        dense=True,
        width=250
    )
    txt_resultado_sim = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)
    txt_traza_detallada = ft.Text(
        value="",
        size=11,
        font_family="monospace",
        selectable=True
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
    txt_contador_pasos = ft.Text(value="Paso: - / -", size=12)

    # -------------------------------------------------------------------------
    # Actualización de la Interfaz
    # -------------------------------------------------------------------------
    def actualizar_resumen_quintupla():
        nonlocal automata_actual
        q_str = "{" + ", ".join(sorted(list(automata_actual.estados))) + "}"
        sig_str = "{" + ", ".join(sorted(list(automata_actual.alfabeto))) + "}"
        q0_str = str(automata_actual.estado_inicial or "∅")
        f_str = "{" + ", ".join(sorted(list(automata_actual.estados_aceptacion))) + "}"
        
        automata_actual._actualizar_tipo()
        txt_tipo_auto.value = f"Tipo Detectado: {automata_actual.tipo} ({len(automata_actual.transiciones)} transiciones)"
        txt_quintupla.value = (
            f"Q  = {q_str}\n"
            f"Σ  = {sig_str}\n"
            f"q0 = {q0_str}\n"
            f"F  = {f_str}"
        )

        # Actualizar tabla visual de transiciones
        filas = []
        tabla_dict = automata_actual.obtener_tabla_transiciones()
        for orig in sorted(list(automata_actual.estados)):
            trans_dict = tabla_dict.get(orig, {})
            dest_strs = []
            for simb, dests in sorted(trans_dict.items()):
                label_simb = simb if simb else "λ"
                dest_strs.append(f"{label_simb} → {{{', '.join(sorted(list(dests)))}}}")
            filas.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(orig, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("; ".join(dest_strs) if dest_strs else "∅"))
                ])
            )

        tabla_transiciones_col.controls = [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Estado")),
                    ft.DataColumn(ft.Text("Transiciones δ(q, a)")),
                ],
                rows=filas,
                dense=True,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                vertical_lines=ft.Border.all(1, ft.Colors.GREY_200)
            )
        ]
        page.update()

    def aplicar_definicion_manual(e):
        nonlocal automata_actual
        auto = Automata()
        
        estados = [x.strip() for x in tf_estados.value.split(",") if x.strip()]
        alfabeto = [x.strip() for x in tf_alfabeto.value.split(",") if x.strip()]
        inicial = tf_inicial.value.strip() or None
        aceptacion = [x.strip() for x in tf_aceptacion.value.split(",") if x.strip()]

        for q in estados:
            auto.agregar_estado(q, es_inicial=(q == inicial), es_final=(q in aceptacion))
        for a in alfabeto:
            auto.agregar_simbolo(a)

        automata_actual = auto
        actualizar_resumen_quintupla()
        mostrar_snack("Quíntupla base actualizada. Ya puede agregar transiciones.")

    def agregar_transicion_click(e):
        nonlocal automata_actual
        orig = tf_trans_origen.value.strip()
        simb = tf_trans_simbolo.value.strip()
        dest = tf_trans_destino.value.strip()

        if not orig or not dest:
            mostrar_snack("Debe especificar estado de origen y destino.", color=ft.Colors.RED_400)
            return

        automata_actual.agregar_transicion(orig, simb, dest)
        tf_trans_simbolo.value = ""
        actualizar_resumen_quintupla()
        mostrar_snack(f"Transición δ({orig}, '{simb or 'λ'}') → {dest} agregada.")

    # -------------------------------------------------------------------------
    # Controladores de Simulación Paso a Paso
    # -------------------------------------------------------------------------
    def ejecutar_simulacion_completa(e):
        nonlocal automata_actual, traza_actual, indice_paso_actual
        cadena = tf_cadena_simular.value or ""
        aceptada, traza = automata_actual.simular_cadena(cadena)
        traza_actual = traza
        indice_paso_actual = len(traza) - 1 if traza else 0

        color_res = ft.Colors.GREEN_600 if aceptada else ft.Colors.RED_600
        estado_res = "ACEPTADA" if aceptada else "RECHAZADA"
        txt_resultado_sim.value = f"Resultado: {estado_res}"
        txt_resultado_sim.color = color_res

        mostrar_paso_actual()

    def mostrar_paso_actual():
        nonlocal traza_actual, indice_paso_actual
        if not traza_actual:
            txt_traza_detallada.value = "Sin traza de ejecución disponible."
            btn_paso_anterior.disabled = True
            btn_paso_siguiente.disabled = True
            txt_contador_pasos.value = "Paso: - / -"
            page.update()
            return

        paso = traza_actual[indice_paso_actual]
        num_paso = paso.get("paso", 0)
        total_pasos = len(traza_actual) - 1

        btn_paso_anterior.disabled = (indice_paso_actual == 0)
        btn_paso_siguiente.disabled = (indice_paso_actual == total_pasos)
        txt_contador_pasos.value = f"Paso {num_paso} de {total_pasos}"

        lineas = [
            f"=== PASO {num_paso} ===",
            f"Símbolo procesado: {paso.get('simbolo_leido', 'λ (Inicio)')}",
            f"Estados activos antes: {paso.get('estados_previos', [])}",
            f"λ-clausura previa:     {paso.get('clausura_previa', [])}",
            f"Transiciones tomadas:  {paso.get('transiciones_tomadas', [])}",
            f"Destinos directos:     {paso.get('estados_posteriores', [])}",
            f"λ-clausura resultante: {paso.get('clausura_posterior', [])}",
            f"¿Alcanza aceptación?:  {'SÍ' if paso.get('es_aceptacion') else 'NO'}"
        ]
        if "error" in paso:
            lineas.append(f"ERROR: {paso['error']}")

        txt_traza_detallada.value = "\n".join(lineas)
        page.update()

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

    def mostrar_snack(mensaje: str, color: str = ft.Colors.BLUE_400):
        snack = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        if hasattr(page, "open"):
            page.open(snack)
        else:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    # -------------------------------------------------------------------------
    # Integración con FilePicker (Importar / Exportar)
    # -------------------------------------------------------------------------
    def on_archivo_seleccionado(e: ft.FilePickerResultEvent):
        nonlocal automata_actual
        if not e.files:
            return
        ruta = e.files[0].path
        try:
            ext = os.path.splitext(ruta)[1].lower()
            if ext == ".jff":
                automata_actual = FormatosAutomata.cargar_jff(ruta)
            elif ext == ".json":
                automata_actual = FormatosAutomata.cargar_json(ruta)
            elif ext == ".xml":
                automata_actual = FormatosAutomata.cargar_xml(ruta)
            else:
                mostrar_snack(f"Extensión no soportada: {ext}", color=ft.Colors.RED_400)
                return

            # Sincronizar inputs
            tf_estados.value = ", ".join(sorted(list(automata_actual.estados)))
            tf_alfabeto.value = ", ".join(sorted(list(automata_actual.alfabeto)))
            tf_inicial.value = automata_actual.estado_inicial or ""
            tf_aceptacion.value = ", ".join(sorted(list(automata_actual.estados_aceptacion)))

            actualizar_resumen_quintupla()
            mostrar_snack(f"Autómata importado exitosamente desde '{os.path.basename(ruta)}'.")
        except Exception as ex:
            mostrar_snack(f"Error al importar archivo: {ex}", color=ft.Colors.RED_400)

    file_picker_importar = ft.FilePicker()
    file_picker_importar.on_result = on_archivo_seleccionado
    page.services.append(file_picker_importar)

    # Exportación rápida a directorio local
    def exportar_automata(formato: str):
        nonlocal automata_actual
        if not automata_actual.estados:
            mostrar_snack("No hay autómata definido para exportar.", color=ft.Colors.RED_400)
            return

        nombre_archivo = f"automata_exportado.{formato}"
        try:
            if formato == "jff":
                FormatosAutomata.guardar_jff(automata_actual, nombre_archivo)
            elif formato == "json":
                FormatosAutomata.guardar_json(automata_actual, nombre_archivo)
            elif formato == "xml":
                FormatosAutomata.guardar_xml(automata_actual, nombre_archivo)
            mostrar_snack(f"Guardado como '{nombre_archivo}' con éxito.")
        except Exception as ex:
            mostrar_snack(f"Error al exportar: {ex}", color=ft.Colors.RED_400)

    # -------------------------------------------------------------------------
    # Layout y Ensamblado de Controles
    # -------------------------------------------------------------------------
    panel_definicion = ft.ExpansionTile(
        title=ft.Text("1. Definición Interactiva del Autómata", weight=ft.FontWeight.BOLD),
        expanded=False,
        controls=[
            ft.Row([tf_estados, tf_alfabeto]),
            ft.Row([tf_inicial, tf_aceptacion]),
            ft.ElevatedButton("Actualizar Quíntupla", on_click=aplicar_definicion_manual),
            ft.Divider(),
            ft.Text("Agregar Transición Individual:", weight=ft.FontWeight.W_500),
            ft.Row([tf_trans_origen, tf_trans_simbolo, tf_trans_destino, ft.ElevatedButton("Agregar", on_click=agregar_transicion_click)])
        ]
    )

    panel_archivos = ft.ExpansionTile(
        title=ft.Text("2. Importación y Exportación (.jff, .json, .xml)", weight=ft.FontWeight.BOLD),
        expanded=False,
        controls=[
            ft.Row([
                ft.ElevatedButton(
                    "Importar Archivo...",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: file_picker_importar.pick_files(
                        allowed_extensions=["jff", "json", "xml"],
                        dialog_title="Seleccione autómata (.jff, .json, .xml)"
                    )
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(content=ft.Text("Exportar .JFF (JFLAP)"), on_click=lambda _: exportar_automata("jff")),
                        ft.PopupMenuItem(content=ft.Text("Exportar .JSON"), on_click=lambda _: exportar_automata("json")),
                        ft.PopupMenuItem(content=ft.Text("Exportar .XML"), on_click=lambda _: exportar_automata("xml")),
                    ],
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Exportar en formato..."
                )
            ])
        ]
    )

    panel_simulacion = ft.Container(
        content=ft.Column([
            ft.Text("3. Simulación y Validación Paso a Paso", size=15, weight=ft.FontWeight.BOLD),
            ft.Row([
                tf_cadena_simular,
                ft.ElevatedButton("Simular Cadena", icon=ft.Icons.PLAY_ARROW, on_click=ejecutar_simulacion_completa)
            ]),
            txt_resultado_sim,
            ft.Row([btn_paso_anterior, txt_contador_pasos, btn_paso_siguiente]),
            ft.Container(
                content=txt_traza_detallada,
                padding=10,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=5,
                bgcolor=ft.Colors.GREY_50
            )
        ]),
        padding=10,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=8
    )

    vista_principal = ft.Column([
        txt_titulo,
        txt_tipo_auto,
        ft.Container(content=txt_quintupla, padding=8, bgcolor=ft.Colors.BLUE_50, border_radius=5),
        panel_definicion,
        panel_archivos,
        ft.Text("Tabla de Transiciones Actual:", weight=ft.FontWeight.BOLD),
        tabla_transiciones_col,
        ft.Divider(),
        panel_simulacion
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    return vista_principal


def main_standalone(page: ft.Page):
    page.title = "Simulador de Autómatas Finitos"
    page.window.width = 650
    page.window.height = 750
    page.padding = 20
    page.add(crear_vista_simulador(page))


if __name__ == "__main__":
    ft.run(main_standalone)

