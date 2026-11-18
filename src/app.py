"""
Módulo Principal de Integración — Suite de Teoría de la Computación (Prácticas 1, 2 y 3).
Optimizado para entorno Docker con flet[web]==0.86.5.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)
"""

from __future__ import annotations
import os
import json
import tempfile
import flet as ft

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
    from er_a_automata import er_a_automata
except ImportError:
    er_a_automata = None

try:
    from automata_a_er import automata_a_expresion_regular
except ImportError:
    automata_a_expresion_regular = None


# =====================================================================
# UTILIDADES GLOBALES PARA FLET WEB 0.86.5 EN DOCKER
# =====================================================================

def notificar(page: ft.Page, mensaje: str, es_error: bool = False) -> None:
    """Muestra un SnackBar seguro en Flet Web 0.86.5."""
    snack = ft.SnackBar(
        content=ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
        bgcolor=ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700,
        duration=3500,
    )
    if hasattr(page, "open"):
        page.open(snack)
    else:
        page.snack_bar = snack
        page.snack_bar.open = True
    page.update()


def serializar_automata_texto(auto: Automata) -> str:
    """Convierte un objeto Automata a un resumen legible y estructurado."""
    lineas = [
        f"Tipo: {auto.tipo}",
        f"Estados (Q): {{{', '.join(sorted(auto.estados))}}}",
        f"Alfabeto (Σ): {{{', '.join(sorted(auto.alfabeto))}}}",
        f"Estado Inicial (q0): {auto.estado_inicial}",
        f"Estados de Aceptación (F): {{{', '.join(sorted(auto.estados_aceptacion))}}}",
        "\nTabla de Transiciones (δ):"
    ]
    tabla = auto.obtener_tabla_transiciones()
    for origen in sorted(tabla.keys()):
        for simb, dests in sorted(tabla[origen].items()):
            etiqueta = simb if simb != "" else "λ"
            lineas.append(f"  δ({origen}, {etiqueta}) -> {{{', '.join(sorted(dests))}}}")
    return "\n".join(lineas)


def parsear_automata_desde_texto(contenido: str) -> Automata:
    """
    Construye un objeto Automata a partir de .jff, .xml, .json o texto plano.
    """
    contenido = contenido.strip()
    if not contenido:
        raise ValueError("El contenido del autómata está vacío.")

    # 1. Formato XML / JFF de JFLAP
    if contenido.startswith("<"):
        if "<structure>" in contenido or "<automaton>" in contenido:
            return FormatosAutomata.cargar_jff(contenido)
        return FormatosAutomata.cargar_xml(contenido)

    # 2. Formato JSON (tanto esquema Anexo 3 como esquema genérico)
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

    # 3. Formato texto legible línea por línea
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
# VISTA PRÁCTICA 3: ALGORITMOS DE AFN, SUBCONJUNTOS, MINIMIZACIÓN Y EQUIVALENCIA
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
    Construye la interfaz completa para Práctica 3 con API de FilePicker de Flet 0.86.5.
    """

    editor_automata_1 = ft.TextField(
        label="Definición del Autómata Principal (M1 — soporta texto, .json, .jff, .xml)",
        value=EJEMPLO_AFN_LAMBDA.strip(),
        multiline=True,
        min_lines=9,
        max_lines=12,
        text_style=ft.TextStyle(font_family="monospace", size=13),
        expand=True,
    )

    editor_automata_2 = ft.TextField(
        label="Definición del Segundo Autómata (M2 — solo para Equivalencia de AFD)",
        value=EJEMPLO_AFD_EQUIV_2.strip(),
        multiline=True,
        min_lines=6,
        max_lines=9,
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

    salida_p3 = ft.Text(
        value="Selecciona un algoritmo de la Práctica 3 y presiona 'Ejecutar Algoritmo'.",
        selectable=True,
        font_family="monospace",
        size=13,
    )

    # -----------------------------------------------------------------
    # GESTIÓN DE ARCHIVOS EN FLET 0.86.5 (DOCKER WEB + DESKTOP)
    # -----------------------------------------------------------------
    target_carga = {"editor": 1}

    def on_upload_completado(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            ruta_local = os.path.join(UPLOAD_DIR, e.file_name)
            try:
                if os.path.exists(ruta_local):
                    with open(ruta_local, "r", encoding="utf-8", errors="replace") as f:
                        contenido = f.read()
                    if target_carga["editor"] == 1:
                        editor_automata_1.value = contenido
                    else:
                        editor_automata_2.value = contenido
                    notificar(page, f"Archivo '{e.file_name}' cargado correctamente.")
                    page.update()
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
                if editor_num == 1:
                    editor_automata_1.value = contenido
                else:
                    editor_automata_2.value = contenido
                notificar(page, f"Archivo '{archivo.name}' cargado.")
                page.update()
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
            contenido_bytes = (salida_p3.value or "").encode("utf-8")
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
        editor_automata_2.visible = (alg == "equivalencia")
        btn_cargar_m2.visible = (alg == "equivalencia")
        campo_er.visible = (alg == "er_a_automata")
        editor_automata_1.visible = (alg != "er_a_automata")

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

        page.update()

    selector_algoritmo.on_select = al_cambiar_algoritmo

    def ejecutar_algoritmo_p3(e):
        alg = selector_algoritmo.value
        salida_p3.color = None

        try:
            if alg == "er_a_automata":
                if er_a_automata is None:
                    raise RuntimeError("El módulo er_a_automata.py no exporta 'er_a_automata'.")
                er = (campo_er.value or "").strip()
                if not er:
                    raise ValueError("Ingresa una expresión regular válida.")
                auto_res = er_a_automata(er)
                salida_p3.value = (
                    f"=== CONVERSIÓN ER → AUTÓMATA ===\n"
                    f"Expresión Regular: {er}\n\n"
                    f"{serializar_automata_texto(auto_res)}"
                )
                page.update()
                return

            m1 = parsear_automata_desde_texto(editor_automata_1.value or "")

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
                salida_p3.value = "\n".join(lineas)

            elif alg == "simulacion_directa":
                cadena = (campo_parametro.value or "").strip()
                res = simular_afn_lambda_directo(m1, cadena)
                if isinstance(res, tuple):
                    aceptada, traza = res
                    lineas = [
                        f"=== SIMULACIÓN DIRECTA AFN / AFN-λ ===",
                        f"Cadena evaluada: '{cadena if cadena else 'λ'}'",
                        f"Resultado: {'ACEPTADA ✔' if aceptada else 'RECHAZADA ✘'}\n",
                    ]
                    for paso in traza:
                        lineas.append(str(paso))
                    salida_p3.value = "\n".join(lineas)
                elif isinstance(res, dict):
                    aceptada = res.get("aceptada", False)
                    lineas = [
                        f"=== SIMULACIÓN DIRECTA AFN / AFN-λ ===",
                        f"Cadena evaluada: '{cadena if cadena else 'λ'}'",
                        f"Resultado: {'ACEPTADA ✔' if aceptada else 'RECHAZADA ✘'}\n",
                    ]
                    if "resumen_texto" in res:
                        lineas.append(res["resumen_texto"])
                    else:
                        for k, v in res.items():
                            lineas.append(f"{k}: {v}")
                    salida_p3.value = "\n".join(lineas)
                else:
                    salida_p3.value = str(res)

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
                lineas.append("\n--- Autómata Equivalente Sin λ ---")
                lineas.append(serializar_automata_texto(afn_sin_l))
                salida_p3.value = "\n".join(lineas)

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
                lineas.append("\n--- AFD Resultante ---")
                lineas.append(serializar_automata_texto(afd))
                salida_p3.value = "\n".join(lineas)

            elif alg == "inaccesibles":
                depurado, rep = eliminar_estados_inaccesibles_detallado(m1)
                lineas = [
                    "=== ELIMINACIÓN DE ESTADOS INACCESIBLES ===",
                    f"Estados originales: {rep['estados_originales']}",
                    f"Estados alcanzables desde q0: {rep['estados_alcanzables']}",
                    f"Estados inaccesibles eliminados ({rep['total_eliminados']}): {rep['estados_inaccesibles']}\n",
                    "--- Autómata Depurado ---",
                    serializar_automata_texto(depurado),
                ]
                salida_p3.value = "\n".join(lineas)

            elif alg == "minimizacion":
                afd_min = minimizar_afd(m1)
                lineas = [
                    "=== MINIMIZACIÓN DE AFD ===",
                    f"Estados antes: {len(m1.estados)} | Estados después: {len(afd_min.estados)}\n",
                    "--- AFD Mínimo Equivalente ---",
                    serializar_automata_texto(afd_min),
                ]
                salida_p3.value = "\n".join(lineas)

            elif alg == "equivalencia":
                m2 = parsear_automata_desde_texto(editor_automata_2.value or "")
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
                salida_p3.value = "\n".join(lineas)

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
                salida_p3.value = "\n".join(lineas)

        except Exception as ex:
            salida_p3.value = f"ERROR EN EJECUCIÓN:\n{ex}"
            salida_p3.color = ft.Colors.RED_400

        page.update()

    def cargar_ejemplo_rapido(e):
        editor_automata_1.value = EJEMPLO_AFN_LAMBDA.strip()
        editor_automata_2.value = EJEMPLO_AFD_EQUIV_2.strip()
        notificar(page, "Ejemplos de autómatas restaurados.")
        page.update()

    return ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Icon(ft.Icons.ACCOUNT_TREE, size=28, color=ft.Colors.PURPLE_400),
                    ft.Column(
                        [
                            ft.Text("Práctica 3: Autómatas No Deterministas, Minimización y Equivalencia", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Cerradura λ, simulación directa, AFN-λ → AFN → AFD, minimización y equivalencia.", size=12, color=ft.Colors.GREY_400),
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
                        ],
                        spacing=12,
                    ),
                )
            ),
            ft.Text("Salida y Trazas Paso a Paso:", weight=ft.FontWeight.BOLD, size=14),
            ft.Container(
                content=ft.SelectionArea(
                    content=ft.Column([salida_p3], scroll=ft.ScrollMode.AUTO)
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
# PUNTO DE ENTRADA PRINCIPAL CON BARRA DE NAVEGACIÓN UNIFICADA
# =====================================================================

def main_integrada(page: ft.Page):
    """Punto de entrada integrado que conmuta entre Práctica 1, Práctica 2 y Práctica 3."""
    page.title = "Teoría de la Computación — Suite Integrada (Prácticas 1, 2 y 3)"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    vista_p1 = crear_vista_practica1(page)
    vista_p2 = crear_vista_simulador(page)
    vista_p3 = crear_vista_practica3(page)

    vistas = [vista_p1, vista_p2, vista_p3]
    contenedor_dinamico = ft.Container(content=vista_p3, expand=True)

    def cambiar_modulo(e):
        indice = e.control.selected_index
        contenedor_dinamico.content = vistas[indice]
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
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
        ],
        selected_index=2,
        on_change=cambiar_modulo,
    )

    page.navigation_bar = nav_bar
    page.add(contenedor_dinamico)
    page.update()


if __name__ == "__main__":
    os.environ.setdefault("FLET_SECRET_KEY", "teoria-computacion-escom-2026")
    ft.run(main_integrada, upload_dir=UPLOAD_DIR)