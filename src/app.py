"""
===============================================================================
MÓDULO DE INTEGRACIÓN DE APLICACIONES INTERACTIVAS (PRÁCTICAS 1 Y 2)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación
Institución: Escuela Superior de Cómputo (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Punto de entrada principal con interfaz gráfica unificada en Flet (Material Design 3).
    Integra armónicamente en una sola aplicación con barra de navegación persistente:
      1. Simulador de Autómatas Finitos (AFD, AFND, AFND-λ) (Práctica 2):
         Definición interactiva, tabla de transiciones dinámica, importación web/local,
         ejemplos precargados, exportación multiformato (.jff, .json, .xml) y simulación
         paso a paso con traza de λ-clausura.
      2. Calculadora de Operaciones sobre Lenguajes y Cadenas (Práctica 1):
         Prefijos, sufijos, subcadenas, cerradura de Kleene (Σ*) y cerradura positiva (Σ+).
         
    Soporta despliegue nativo en contenedores Docker (Web Server en puerto 8550)
    y ejecución en escritorio local con soporte completo de subida y descarga de archivos.
===============================================================================
"""

from __future__ import annotations
import os
import flet as ft

# -----------------------------------------------------------------------------
# Importaciones de Módulos del Núcleo Formal
# -----------------------------------------------------------------------------
from lenguajes import (
    prefijos,
    sufijos,
    subcadenas,
    cerradura_Kleene,
    cerradura_positiva
)
from gui_simulador import crear_vista_simulador, UPLOAD_DIR, BASE_DIR


# =============================================================================
# SECCIÓN 1: VISTA DE OPERACIONES SOBRE CADENAS Y ALFABETOS (PRÁCTICA 1)
# =============================================================================

def crear_vista_practica1(page: ft.Page) -> ft.Control:
    """
    Construye la vista interactiva para las operaciones de la Práctica 1:
    prefijos, sufijos, subcadenas, cerradura de Kleene y cerradura positiva.
    """
    # -------------------------------------------------------------------------
    # 1.1 Utilidades y Diálogo de Exportación a TXT
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

    tf_exportar_preview = ft.TextField(
        label="Vista Previa de Resultados",
        multiline=True,
        min_lines=8,
        max_lines=15,
        read_only=True,
        dense=True,
        border_radius=8,
        text_style=ft.TextStyle(font_family="monospace")
    )

    def cerrar_dialogo_exportar(e=None) -> None:
        dialogo_exportar.open = False
        page.update()

    def copiar_resultados_click(e) -> None:
        if texto_resultado.value:
            page.set_clipboard(texto_resultado.value)
            mostrar_snack("¡Resultados copiados al portapapeles!", ft.Colors.GREEN_700)

    def descargar_archivo_txt(e) -> None:
        nombre_arch = "resultados_lenguajes.txt"
        try:
            page.launch_url(f"/{nombre_arch}")
            mostrar_snack(f"Descargando '{nombre_arch}'...", ft.Colors.GREEN_700)
        except Exception as ex:
            mostrar_snack(f"Error al solicitar descarga: {ex}", ft.Colors.RED_700)

    dialogo_exportar = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.FILE_DOWNLOAD), ft.Text("Exportar Resultados a TXT")]),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Los resultados han sido guardados en el servidor. Puede copiarlos directamente o descargarlos:"),
                tf_exportar_preview
            ], tight=True, spacing=10),
            width=550
        ),
        actions=[
            ft.TextButton("Copiar al Portapapeles", icon=ft.Icons.COPY, on_click=copiar_resultados_click),
            ft.ElevatedButton("Descargar Archivo", icon=ft.Icons.DOWNLOAD, on_click=descargar_archivo_txt),
            ft.TextButton("Cerrar", on_click=cerrar_dialogo_exportar)
        ]
    )

    def guardar_archivo_picker(e: ft.FilePickerResultEvent) -> None:
        if e.path:
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(texto_resultado.value)
                mostrar_snack(f"Archivo guardado exitosamente en '{e.path}'", ft.Colors.GREEN_700)
            except Exception as ex:
                mostrar_snack(f"Error al guardar archivo: {ex}", ft.Colors.RED_700)

    exportar_dialogo = ft.FilePicker()
    exportar_dialogo.on_result = guardar_archivo_picker
    page.services.append(exportar_dialogo)

    def abrir_exportacion(e) -> None:
        contenido = texto_resultado.value or ""
        if not contenido or contenido.startswith("Seleccione una operación"):
            mostrar_snack("No hay ningún resultado disponible para exportar.", ft.Colors.RED_700)
            return

        nombre_archivo = "resultados_lenguajes.txt"
        ruta_salida = os.path.join(UPLOAD_DIR, nombre_archivo)
        try:
            with open(ruta_salida, "w", encoding="utf-8") as f:
                f.write(contenido)
            try:
                with open(os.path.join(BASE_DIR, nombre_archivo), "w", encoding="utf-8") as f:
                    f.write(contenido)
            except Exception:
                pass

            tf_exportar_preview.value = contenido
            if hasattr(page, "open"):
                page.open(dialogo_exportar)
            else:
                page.dialog = dialogo_exportar
                dialogo_exportar.open = True
            page.update()
        except Exception as ex:
            mostrar_snack(f"Error al exportar resultados: {ex}", ft.Colors.RED_700)

    # -------------------------------------------------------------------------
    # 1.2 Controles Visuales de Entrada y Configuración
    # -------------------------------------------------------------------------
    txt_titulo = ft.Text(
        "Operaciones sobre Lenguajes y Cadenas",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY
    )
    txt_subtitulo = ft.Text(
        "Módulo de cálculo formal para prefijos, sufijos, subcadenas y cerraduras de Kleene / positiva",
        size=13,
        color=ft.Colors.OUTLINE
    )

    input_texto = ft.TextField(
        label="Cadena de texto w (ej. abc)",
        hint_text="Ingrese los símbolos de la cadena",
        expand=True,
        dense=True,
        border_radius=8,
        prefix_icon=ft.Icons.TEXT_FIELDS
    )

    input_longitud = ft.TextField(
        label="Longitud Máxima n",
        hint_text="ej. 3",
        width=180,
        dense=True,
        disabled=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        prefix_icon=ft.Icons.PIN
    )

    chip_contador = ft.Chip(
        label=ft.Text("Esperando cálculo..."),
        leading=ft.Icon(ft.Icons.INFO_OUTLINE, size=16)
    )

    texto_resultado = ft.Text(
        value="Seleccione una operación e ingrese los datos para ver el resultado...",
        selectable=True,
        style=ft.TextStyle(font_family="monospace"),
        size=12
    )

    boton_calcular = ft.ElevatedButton(
        "Calcular",
        icon=ft.Icons.PLAY_ARROW,
        style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY)
    )

    boton_copiar = ft.OutlinedButton(
        "Copiar Resultado",
        icon=ft.Icons.COPY,
        disabled=True,
        on_click=copiar_resultados_click
    )

    boton_exportar = ft.OutlinedButton(
        "Exportar a TXT",
        icon=ft.Icons.DOWNLOAD,
        disabled=True,
        on_click=abrir_exportacion
    )

    def limpiar_campos_p1(e=None) -> None:
        input_texto.value = ""
        input_longitud.value = ""
        texto_resultado.value = "Seleccione una operación e ingrese los datos para ver el resultado..."
        texto_resultado.color = None
        chip_contador.label.value = "Esperando cálculo..."
        chip_contador.leading = ft.Icon(ft.Icons.INFO_OUTLINE, size=16)
        boton_copiar.disabled = True
        boton_exportar.disabled = True
        page.update()

    boton_limpiar = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        tooltip="Limpiar campos y resultados",
        on_click=limpiar_campos_p1
    )

    def cambiar_op(e) -> None:
        seleccion = opciones_dropdown.value
        if seleccion in ("Cerradura de Kleene", "Cerradura Positiva"):
            input_longitud.disabled = False
            input_texto.label = "Alfabeto Σ (elementos separados por coma, ej: 0, 1)"
            input_texto.hint_text = "ej. 0, 1 o a, b"
        else:
            input_longitud.disabled = True
            input_longitud.value = ""
            input_texto.label = "Cadena de texto w (ej. abc)"
            input_texto.hint_text = "ej. abc o 010"

        input_longitud.update()
        input_texto.update()

    opciones_dropdown = ft.Dropdown(
        label="Selecciona una operación formal",
        expand=True,
        dense=True,
        border_radius=8,
        options=[
            ft.dropdown.Option("Prefijos"),
            ft.dropdown.Option("Sufijos"),
            ft.dropdown.Option("Subcadenas"),
            ft.dropdown.Option("Cerradura de Kleene"),
            ft.dropdown.Option("Cerradura Positiva"),
        ],
        on_select=cambiar_op
    )

    # -------------------------------------------------------------------------
    # 1.3 Controladores de Cálculo y Validación Formal
    # -------------------------------------------------------------------------
    def mostrar_error(mensaje: str) -> None:
        texto_resultado.value = f"⚠️ ERROR DE VALIDACIÓN:\n{mensaje}"
        texto_resultado.color = ft.Colors.RED_600
        chip_contador.label.value = "Error"
        chip_contador.leading = ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_600, size=16)
        boton_exportar.disabled = True
        boton_copiar.disabled = True
        page.update()

    def calcular_res(e) -> None:
        op = opciones_dropdown.value
        texto = input_texto.value or ""

        texto_resultado.color = None

        if not op:
            mostrar_error("Por favor selecciona una operación de la lista.")
            return

        if not texto.strip():
            mostrar_error("Por favor ingrese la cadena o el alfabeto requerido.")
            return

        texto = texto.strip()

        try:
            if op == "Prefijos":
                res = prefijos(texto)
                resultado = (
                    f"=== PREFIJOS DE LA CADENA '{texto}' ===\n"
                    f"Definición: Pref(w) = {{ u ∈ Σ* | ∃v ∈ Σ* tal que w = uv }}\n"
                    f"Total de prefijos (|w| + 1): {len(res)}\n\n"
                    f"Pref('{texto}') = {res}"
                )
                chip_contador.label.value = f"{len(res)} prefijos"
                chip_contador.leading = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN_600, size=16)

            elif op == "Sufijos":
                res = sufijos(texto)
                resultado = (
                    f"=== SUFIJOS DE LA CADENA '{texto}' ===\n"
                    f"Definición: Suf(w) = {{ v ∈ Σ* | ∃u ∈ Σ* tal que w = uv }}\n"
                    f"Total de sufijos (|w| + 1): {len(res)}\n\n"
                    f"Suf('{texto}') = {res}"
                )
                chip_contador.label.value = f"{len(res)} sufijos"
                chip_contador.leading = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN_600, size=16)

            elif op == "Subcadenas":
                res = sorted(subcadenas(texto), key=lambda x: (len(x), x))
                resultado = (
                    f"=== SUBCADENAS DE LA CADENA '{texto}' ===\n"
                    f"Definición: Sub(w) = {{ v ∈ Σ* | ∃u,x ∈ Σ* tal que w = uvx }}\n"
                    f"Total de subcadenas únicas: {len(res)}\n\n"
                    f"Sub('{texto}') = {res}"
                )
                chip_contador.label.value = f"{len(res)} subcadenas"
                chip_contador.leading = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN_600, size=16)

            elif op in ("Cerradura de Kleene", "Cerradura Positiva"):
                alfabeto = [x.strip() for x in texto.split(",") if x.strip()]
                # Eliminar duplicados preservando orden
                alfabeto = list(dict.fromkeys(alfabeto))

                if not alfabeto:
                    mostrar_error("El alfabeto Σ no es válido o está vacío.")
                    return

                try:
                    n = int(input_longitud.value)
                except (ValueError, TypeError):
                    mostrar_error("La longitud máxima n debe ser un número entero válido (≥ 0).")
                    return

                if n < 0:
                    mostrar_error("La longitud máxima n no puede ser negativa.")
                    return

                k = len(alfabeto)
                inicio = 0 if op == "Cerradura de Kleene" else 1

                # Validación de cota superior para evitar desbordamiento de memoria
                total_combinaciones = sum(k ** i for i in range(inicio, n + 1))
                if total_combinaciones > 200000:
                    mostrar_error(
                        f"Se generarían {total_combinaciones:,} palabras combinatorias.\n"
                        f"El límite de seguridad del sistema es 200,000 elementos."
                    )
                    return

                if op == "Cerradura de Kleene":
                    res = cerradura_Kleene(alfabeto, n)
                    nombre_op = "CERRADURA DE KLEENE (Σ*)"
                    simbolo_cerr = "Σ*"
                else:
                    res = cerradura_positiva(alfabeto, n)
                    nombre_op = "CERRADURA POSITIVA (Σ+)"
                    simbolo_cerr = "Σ+"

                resultado = (
                    f"=== {nombre_op} HASTA LONGITUD n = {n} ===\n"
                    f"Alfabeto base Σ = {{{', '.join(alfabeto)}}} (|Σ| = {k})\n"
                    f"Total de palabras generadas: {len(res):,}\n\n"
                    f"{simbolo_cerr} = {res}"
                )
                chip_contador.label.value = f"{len(res):,} palabras ({simbolo_cerr})"
                chip_contador.leading = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN_600, size=16)

            else:
                mostrar_error("Operación no reconocida.")
                return

            texto_resultado.value = resultado
            texto_resultado.color = None
            boton_exportar.disabled = False
            boton_copiar.disabled = False

        except Exception as ex:
            mostrar_error(f"Ocurrió un error inesperado al procesar: {ex}")
            return

        page.update()

    boton_calcular.on_click = calcular_res

    # -------------------------------------------------------------------------
    # 1.4 Ensamblado Visual en Tarjetas Material Design 3
    # -------------------------------------------------------------------------
    card_configuracion = ft.Card(
        elevation=2,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TUNE, color=ft.Colors.PRIMARY),
                    ft.Text("Configuración de la Operación", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    boton_limpiar
                ]),
                ft.Divider(height=10),
                opciones_dropdown,
                ft.Row([input_texto, input_longitud]),
                ft.Row([
                    boton_calcular,
                    boton_copiar,
                    boton_exportar
                ], wrap=True, spacing=10)
            ], spacing=12)
        )
    )

    card_resultados = ft.Card(
        elevation=2,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.OUTPUT, color=ft.Colors.PRIMARY),
                    ft.Text("Resultados Formales", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    chip_contador
                ]),
                ft.Divider(height=10),
                ft.Container(
                    content=ft.SelectionArea(content=texto_resultado),
                    padding=14,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
                )
            ], spacing=10)
        )
    )

    vista_p1 = ft.Column([
        txt_titulo,
        txt_subtitulo,
        card_configuracion,
        card_resultados
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=16)

    return vista_p1


# =============================================================================
# SECCIÓN 2: PUNTO DE ENTRADA INTEGRADO CON BARRA DE NAVEGACIÓN
# =============================================================================

def main_integrada(page: ft.Page) -> None:
    """
    Punto de entrada unificado para la suite interactiva de Teoría de la Computación.
    Provee una barra de navegación persistente, control de temas (Claro / Oscuro)
    y diálogo informativo institucional de la ESCOM - IPN.
    """
    page.title = "Teoría de la Computación — Suite Integrada (ESCOM - IPN)"
    page.window.width = 860
    page.window.height = 880
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16

    # Instanciación de las dos vistas principales
    vista_p1 = crear_vista_practica1(page)
    vista_p2 = crear_vista_simulador(page)

    # Diálogo "Acerca de"
    def cerrar_dialogo_acerca(e=None) -> None:
        dialogo_acerca.open = False
        page.update()

    dialogo_acerca = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.SCHOOL), ft.Text("Teoría de la Computación — ESCOM IPN")]),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Suite Integrada de Prácticas 1 y 2", weight=ft.FontWeight.BOLD, size=15),
                ft.Text("Autores y Desarrolladores:", weight=ft.FontWeight.BOLD),
                ft.Text("• Antonio Navarro Domínguez (Boleta: 2025630725)"),
                ft.Text("• Mario García Castillo (Boleta: 2025630545)"),
                ft.Divider(),
                ft.Text("Módulos Integrados:"),
                ft.Text("1. Simulador de Autómatas Finitos (AFD, AFND, AFND-λ) con importación/exportación multiformato (.jff, .json, .xml) y traza de ejecución."),
                ft.Text("2. Calculadora Formal de Lenguajes: Prefijos, Sufijos, Subcadenas y Cerraduras de Kleene / Positiva."),
                ft.Text("3. Servidor Web en Contenedores Docker (Puerto 8550) con soporte completo de subida y descarga de archivos.")
            ], tight=True, spacing=6),
            width=500
        ),
        actions=[
            ft.ElevatedButton("Entendido", on_click=cerrar_dialogo_acerca)
        ]
    )

    def abrir_acerca_de(e) -> None:
        if hasattr(page, "open"):
            page.open(dialogo_acerca)
        else:
            page.dialog = dialogo_acerca
            dialogo_acerca.open = True
        page.update()

    def alternar_tema(e) -> None:
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            btn_tema.icon = ft.Icons.LIGHT_MODE
            btn_tema.tooltip = "Cambiar a modo claro"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            btn_tema.icon = ft.Icons.DARK_MODE
            btn_tema.tooltip = "Cambiar a modo oscuro"
        page.update()

    btn_tema = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Cambiar tema (Claro / Oscuro)",
        on_click=alternar_tema
    )

    btn_info = ft.IconButton(
        icon=ft.Icons.INFO_OUTLINE,
        tooltip="Acerca de este proyecto",
        on_click=abrir_acerca_de
    )

    # Barra superior institucional
    app_bar = ft.AppBar(
        leading=ft.Icon(ft.Icons.ACCOUNT_TREE, color=ft.Colors.PRIMARY),
        leading_width=40,
        title=ft.Column([
            ft.Text("ESCOM — IPN | Teoría de la Computación", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Suite Integrada: Simulador de Autómatas & Operaciones de Lenguajes", size=11, color=ft.Colors.OUTLINE)
        ], spacing=1),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[btn_tema, btn_info, ft.Container(width=10)]
    )
    page.appbar = app_bar

    # Contenedor dinámico según navegación
    contenedor_dinamico = ft.Container(content=vista_p2, expand=True)

    def cambiar_modulo(e) -> None:
        seleccion = e.control.selected_index
        if seleccion == 0:
            contenedor_dinamico.content = vista_p2
        else:
            contenedor_dinamico.content = vista_p1
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_SUGGEST_OUTLINED,
                selected_icon=ft.Icons.SETTINGS_SUGGEST,
                label="Simulador Autómatas (P2)"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALCULATE_OUTLINED,
                selected_icon=ft.Icons.CALCULATE,
                label="Operaciones Lenguajes (P1)"
            ),
        ],
        selected_index=0,
        on_change=cambiar_modulo
    )

    page.navigation_bar = nav_bar
    page.add(contenedor_dinamico)
    page.update()


# =============================================================================
# SECCIÓN 3: BLOQUE DE EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("FLET_SERVER_PORT", 8550))
    host = os.environ.get("FLET_SERVER_IP", "0.0.0.0")
    is_web = os.environ.get("FLET_FORCE_WEB_SERVER", "false").lower() in ("true", "1")

    if is_web:
        ft.run(
            main_integrada,
            host=host,
            port=port,
            upload_dir=UPLOAD_DIR,
            assets_dir=UPLOAD_DIR
        )
    else:
        ft.run(
            main_integrada,
            upload_dir=UPLOAD_DIR,
            assets_dir=UPLOAD_DIR
        )
