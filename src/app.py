"""
===============================================================================
MÓDULO DE INTEGRACIÓN DE APLICACIONES INTERACTIVAS (PRÁCTICAS 1 Y 2)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación
Institución: Escuela Superior de Cómputo (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Punto de entrada principal de la aplicación con interfaz gráfica (Flet).
    Conforme a las Secciones 3 y 3.4 del documento oficial de la Práctica 2,
    integra armónicamente en una misma aplicación:
      1. El Simulador de Autómatas Finitos (AFD, AFND, AFND-λ) con definición
         interactiva, carga/exportación multiformato y simulación paso a paso.
      2. La Calculadora de Operaciones sobre Lenguajes y Cadenas de la Práctica 1:
         prefijos, sufijos, subcadenas, cerradura de Kleene y cerradura positiva.
      
    Mantiene una barra de navegación persistente (ft.NavigationBar) para alternar
    de forma fluida entre ambos módulos.

Navegación del Módulo:
    1. Importaciones y Dependencias
    2. Vista de Operaciones sobre Cadenas y Alfabetos (Práctica 1)
    3. Integración con el Simulador de Autómatas Finitos (Práctica 2)
    4. Barra de Navegación y Ensamblado Principal (main_integrada)
    5. Bloque de Ejecución
===============================================================================
"""

from __future__ import annotations
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
from gui_simulador import crear_vista_simulador


# =============================================================================
# SECCIÓN 1: VISTA DE OPERACIONES SOBRE CADENAS Y ALFABETOS (PRÁCTICA 1)
# =============================================================================

def crear_vista_practica1(page: ft.Page) -> ft.Control:
    """
    Construye y encapsula la vista de operaciones de la Práctica 1 requerida
    por el Ejercicio 3.4: subcadenas, prefijos, sufijos, cerradura de Kleene
    y cerradura positiva con validación de límites de seguridad.
    
    Parámetros:
        page (ft.Page): Instancia de página activa en Flet.
        
    Retorna:
        ft.Control: Contenedor con la interfaz de operaciones sobre lenguajes.
    """
    # -------------------------------------------------------------------------
    # 1.1 Sistema de Exportación de Resultados a Archivo de Texto (.txt)
    # -------------------------------------------------------------------------
    def guardar_archivo(e: ft.FilePickerResultEvent) -> None:
        if e.path:
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(texto_resultado.value)

                snack = ft.SnackBar(ft.Text("Archivo guardado con éxito."))
                if hasattr(page, "open"):
                    page.open(snack)
                else:
                    page.snack_bar = snack
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                mostrar_error(f"Error al guardar el archivo: {ex}")

    exportar_dialogo = ft.FilePicker()
    exportar_dialogo.on_result = guardar_archivo
    page.services.append(exportar_dialogo)

    async def abrir_exportacion(e) -> None:
        try:
            await exportar_dialogo.save_file(
                dialog_title="Guardar resultados como...",
                file_name="resultados_lenguajes.txt",
                src_bytes=(texto_resultado.value or "").encode("utf-8"),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt"]
            )
        except Exception as ex:
            mostrar_error(f"Error al abrir el selector de archivos: {ex}")


    # -------------------------------------------------------------------------
    # 1.2 Controles Visuales de Entrada y Configuración
    # -------------------------------------------------------------------------
    titulo = ft.Text(
        "Operaciones con Cadenas y Alfabetos (Práctica 1)",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_GREY_800
    )

    input_texto = ft.TextField(
        label="Cadena de texto (ej: abc)",
        width=450
    )

    input_longitud = ft.TextField(
        label="Longitud Máxima n",
        width=450,
        disabled=True,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    texto_resultado = ft.Text(
        value="Seleccione una operación e ingrese los datos para ver el resultado...",
        selectable=True
    )

    boton_exportar = ft.ElevatedButton(
        "Exportar a TXT",
        icon=ft.Icons.SAVE,
        disabled=True,
        on_click=abrir_exportacion
    )

    def cambiar_op(e) -> None:
        """Adapta los campos de entrada según la operación seleccionada."""
        seleccion = e.control.value

        if seleccion in ("Cerradura de Kleene", "Cerradura Positiva"):
            input_longitud.disabled = False
            input_texto.label = "Alfabeto Σ (separado por comas, ej: 0, 1)"
        else:
            input_longitud.disabled = True
            input_longitud.value = ""
            input_texto.label = "Cadena de texto w (ej: abc)"

        input_longitud.update()
        input_texto.update()

    opciones_dropdown = ft.Dropdown(
        label="Selecciona una operación",
        width=450,
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
    # 1.3 Controladores de Cálculo y Validación de Entrada
    # -------------------------------------------------------------------------
    def mostrar_error(mensaje: str) -> None:
        texto_resultado.value = f"ERROR: {mensaje}"
        texto_resultado.color = ft.Colors.RED_400
        boton_exportar.disabled = True
        page.update()

    def calcular_res(e) -> None:
        op = opciones_dropdown.value
        texto = input_texto.value or ""

        texto_resultado.color = None

        if not op or not texto.strip():
            mostrar_error("Por favor selecciona una operación y escribe la cadena o el alfabeto.")
            return

        texto = texto.strip()

        try:
            if op == "Prefijos":
                res = prefijos(texto)
                resultado = f"Prefijos de '{texto}':\n{res}"

            elif op == "Sufijos":
                res = sufijos(texto)
                resultado = f"Sufijos de '{texto}':\n{res}"

            elif op == "Subcadenas":
                res = subcadenas(texto)
                resultado = f"Subcadenas de '{texto}' ({len(res)} elementos):\n{res}"

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

                # Validación de cota superior de combinaciones para estabilidad de memoria
                total_combinaciones = sum(k ** i for i in range(inicio, n + 1))
                if total_combinaciones > 200000:
                    mostrar_error(
                        f"Se generarían {total_combinaciones} palabras.\n"
                        "El límite de seguridad del sistema es 200,000 elementos."
                    )
                    return

                if op == "Cerradura de Kleene":
                    res = cerradura_Kleene(alfabeto, n)
                else:
                    res = cerradura_positiva(alfabeto, n)

                resultado = (
                    f"Cálculo exitoso ({len(res)} elementos generados):\n{res}"
                )

            else:
                mostrar_error("La operación seleccionada no es válida.")
                return

            texto_resultado.value = resultado
            texto_resultado.color = ft.Colors.GREEN_600
            boton_exportar.disabled = False

        except Exception as ex:
            mostrar_error(f"Ocurrió un error al calcular: {ex}")
            return

        page.update()

    boton_calcular = ft.ElevatedButton(
        "Calcular",
        icon=ft.Icons.PLAY_ARROW,
        on_click=calcular_res
    )

    fila_botones = ft.Row([boton_calcular, boton_exportar])

    contenedor_resultado = ft.Container(
        content=ft.SelectionArea(
            content=texto_resultado
        ),
        padding=15,
        border_radius=5,
        expand=True,
        border=ft.Border.all(1, ft.Colors.GREY_400),
        bgcolor=ft.Colors.GREY_50
    )


    # -------------------------------------------------------------------------
    # 1.4 Ensamblado de la Vista de Práctica 1
    # -------------------------------------------------------------------------
    vista_p1 = ft.Column([
        titulo,
        opciones_dropdown,
        input_texto,
        input_longitud,
        fila_botones,
        contenedor_resultado
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    return vista_p1


# =============================================================================
# SECCIÓN 2: PUNTO DE ENTRADA INTEGRADO CON BARRA DE NAVEGACIÓN
# =============================================================================

def main_integrada(page: ft.Page) -> None:
    """
    Punto de entrada principal con barra de navegación persistente entre:
      - Destino 0: Simulador de Autómatas Finitos (Práctica 2)
      - Destino 1: Operaciones sobre Cadenas y Lenguajes (Práctica 1)
    """
    page.title = "Teoría de la Computación — Suite Integrada de Prácticas"
    page.window.width = 720
    page.window.height = 820
    page.padding = 15

    # Instanciación de las dos vistas principales
    vista_p1 = crear_vista_practica1(page)
    vista_p2 = crear_vista_simulador(page)

    # Contenedor dinámico cuyo contenido se reemplaza según la navegación
    contenedor_dinamico = ft.Container(content=vista_p2, expand=True)

    # Controlador de conmutación de la barra de navegación
    def cambiar_modulo(e) -> None:
        seleccion = e.control.selected_index
        if seleccion == 0:
            contenedor_dinamico.content = vista_p2
        else:
            contenedor_dinamico.content = vista_p1
        page.update()

    # Barra de navegación persistente
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.PLAY_CIRCLE,
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
    ft.run(main_integrada)
