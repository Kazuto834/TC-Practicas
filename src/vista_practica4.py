"""
Módulo de Interfaz Gráfica — Práctica 4: Expresiones Regulares y Teorema de Kleene.
Optimizado para entorno Docker con flet[web]==0.86.5.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)
"""

from __future__ import annotations
import json
import os
import tempfile
from typing import Callable, Dict, List, Optional, Tuple
import flet as ft

from automata import Automata
from formatos import FormatosAutomata
from parser_er import ErrorSintacticoER
from er_a_automata import (
    er_a_pipeline_completo,
    exportar_automata_jff,
)
from automata_a_er import (
    automata_a_expresion_regular,
    verificar_determinismo_detallado,
    comparar_expresiones_regulares,
)

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "flet_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================================
# MACROS Y VALIDADORES PREDEFINIDOS (EJERCICIO 1)
# =====================================================================

MACROS_ESTANDAR: Dict[str, str] = {
    "D": "0+1+2+3+4+5+6+7+8+9",
    "N": "1+2+3+4+5+6+7+8+9",
    "L": "a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p+q+r+s+t+u+v+w+x+y+z",
    "M": "A+B+C+D+E+F+G+H+I+J+K+L+M+N+O+P+Q+R+S+T+U+V+W+X+Y+Z",
}

VALIDADORES_DEFECTO: Dict[str, Dict[str, str]] = {
    "correo": {
        "nombre": "Correo Electrónico Institucional / Estándar",
        "er": "(L+D)(L+D+_+\\-+.)*@(L+D)(L+D+\\-)*(.[L][L]+)+",
        "ejemplo_valido": "antonio.navarro@alumno.ipn.mx",
        "ejemplo_invalido": "usuario@@dominio..com",
        "descripcion": "Valida usuario alfanumérico, arroba, dominio y extensión de al menos 2 letras.",
    },
    "telefono": {
        "nombre": "Teléfono Nacional (México / LADA)",
        "er": "(\\+52+λ)(NDDDDDDDDD+(\\(NDD\\)DDDDDDD)+((NDD)\\-DDD\\-DDDD))",
        "ejemplo_valido": "+52(551)2345678",
        "ejemplo_invalido": "012-345-6789",
        "descripcion": "Acepta 10 dígitos con prefijo opcional +52, lada entre paréntesis o guiones.",
    },
    "boleta_ipn": {
        "nombre": "Boleta IPN (10 dígitos)",
        "er": "(201+202)DDDDDDD",
        "ejemplo_valido": "2023630145",
        "ejemplo_invalido": "199863014",
        "descripcion": "Acepta números de boleta de 10 dígitos iniciando con 201 o 202.",
    },
    "numero_real": {
        "nombre": "Número Decimal con Signo Opcional",
        "er": "(\\++\\-+λ)DD*(.DD*+λ)",
        "ejemplo_valido": "-3.1416",
        "ejemplo_invalido": "+.45",
        "descripcion": "Acepta enteros y decimales con signo opcional (+ o -) y parte entera obligatoria.",
    },
    "identificador": {
        "nombre": "Identificador de Lenguaje de Programación",
        "er": "(L+M+_)(L+M+D+_)*",
        "ejemplo_valido": "_contador_1",
        "ejemplo_invalido": "1variable",
        "descripcion": "Inicia con letra o guion bajo, seguido de letras, dígitos o guiones bajos.",
    },
}


def _parsear_macros_usuario(texto_macros: str) -> Dict[str, str]:
    """Convierte líneas 'CLAVE = EXPRESION' en un diccionario de macros."""
    macros = dict(MACROS_ESTANDAR)
    for linea in (texto_macros or "").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip()
        if len(clave) == 1 and valor:
            macros[clave] = valor
    return macros


def _evaluar_cadena_en_afd(afd: Automata, cadena: str) -> Tuple[bool, List[str]]:
    """Simula una cadena sobre un AFD mínimo y retorna (aceptada, traza_estados)."""
    if not afd.estado_inicial:
        return False, ["Sin estado inicial"]

    tabla = afd.obtener_tabla_transiciones()
    actual = afd.estado_inicial
    traza = [actual]

    for ch in cadena:
        destinos = tabla.get(actual, {}).get(ch, set())
        if not destinos:
            traza.append(f"──({ch})──▶ ∅ (sin transición)")
            return False, traza
        siguiente = sorted(list(destinos))[0]
        traza.append(f"──({ch})──▶ {siguiente}")
        actual = siguiente

    return (actual in afd.estados_aceptacion), traza


def _parsear_automata_p4(contenido: str) -> Automata:
    """Parsea un autómata desde .jff, .xml, .json o definición textual."""
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
    estados_declarados: List[str] = []
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
                for d in [x.strip() for x in der.split(",") if x.strip()]:
                    auto.agregar_transicion(origen, simb, d)

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
# VISTA PRINCIPAL PRÁCTICA 4
# =====================================================================

def crear_vista_practica4(
    page: ft.Page,
    construir_grafo_automata_canvas: Callable[..., ft.Control],
    construir_tabla_transiciones_visual: Callable[..., ft.Control],
    notificar: Callable[[ft.Page, str, bool], None],
) -> ft.Control:
    """Construye la vista completa de la Práctica 4 (3 ejercicios)."""

    # Pickers Web seguros para Flet 0.86.5
    picker_guardar_p4 = ft.FilePicker()
    picker_cargar_gnfa = ft.FilePicker()
    page.services.extend([picker_guardar_p4, picker_cargar_gnfa])

    # =================================================================
    # SECCIÓN 1: VALIDADORES CON EXPRESIONES REGULARES
    # =================================================================
    dd_validador = ft.Dropdown(
        label="Validador predefinido",
        value="correo",
        width=360,
        options=[
            ft.dropdown.Option(k, v["nombre"])
            for k, v in VALIDADORES_DEFECTO.items()
        ],
    )

    txt_desc_validador = ft.Text(
        VALIDADORES_DEFECTO["correo"]["descripcion"],
        size=12,
        color=ft.Colors.GREY_400,
    )

    campo_er_validador = ft.TextField(
        label="Expresión Regular (notación del curso: +, *, λ, ∅, escapes \\)",
        value=VALIDADORES_DEFECTO["correo"]["er"],
        text_style=ft.TextStyle(font_family="monospace", size=13),
        expand=True,
    )

    campo_macros_validador = ft.TextField(
        label="Macros / Clases de Símbolos (1 letra = expansión)",
        value=(
            "D = 0+1+2+3+4+5+6+7+8+9\n"
            "N = 1+2+3+4+5+6+7+8+9\n"
            "L = a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p+q+r+s+t+u+v+w+x+y+z\n"
            "M = A+B+C+D+E+F+G+H+I+J+K+L+M+N+O+P+Q+R+S+T+U+V+W+X+Y+Z"
        ),
        multiline=True,
        min_lines=3,
        max_lines=5,
        text_style=ft.TextStyle(font_family="monospace", size=12),
        expand=True,
    )

    campo_cadena_validar = ft.TextField(
        label="Cadena de prueba a validar",
        value=VALIDADORES_DEFECTO["correo"]["ejemplo_valido"],
        prefix_icon=ft.Icons.SPELLCHECK,
        expand=True,
    )

    resultado_validador = ft.Column(spacing=10)

    def al_seleccionar_validador(e):
        clave = dd_validador.value
        if clave in VALIDADORES_DEFECTO:
            info = VALIDADORES_DEFECTO[clave]
            txt_desc_validador.value = info["descripcion"]
            campo_er_validador.value = info["er"]
            campo_cadena_validar.value = info["ejemplo_valido"]
            page.update()

    dd_validador.on_select = al_seleccionar_validador

    def probar_validador_click(e):
        er = (campo_er_validador.value or "").strip()
        cadena = campo_cadena_validar.value or ""
        macros = _parsear_macros_usuario(campo_macros_validador.value or "")

        try:
            pipeline = er_a_pipeline_completo(er, macros=macros)
            afd_min = pipeline["afd_minimo"]
            aceptada, traza = _evaluar_cadena_en_afd(afd_min, cadena)

            badge_color = ft.Colors.GREEN_400 if aceptada else ft.Colors.RED_400
            veredicto = "CADENA VÁLIDA (ACEPTADA) ✔" if aceptada else "CADENA INVÁLIDA (RECHAZADA) ✘"

            resultado_validador.controls = [
                ft.Container(
                    padding=14,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.12, badge_color),
                    border=ft.Border.all(1, badge_color),
                    content=ft.Column(
                        [
                            ft.Text(veredicto, size=16, weight=ft.FontWeight.BOLD, color=badge_color),
                            ft.Text(
                                f"Cadena evaluada: '{cadena if cadena else 'λ'}'  |  "
                                f"Estados del AFD mínimo: {len(afd_min.estados)}",
                                size=13,
                            ),
                            ft.Text(
                                "Recorrido: " + " ".join(traza),
                                size=12,
                                font_family="monospace",
                                color=ft.Colors.GREY_300,
                                selectable=True,
                            ),
                        ],
                        spacing=6,
                    ),
                )
            ]
        except ErrorSintacticoER as err_sin:
            resultado_validador.controls = [
                ft.Text(
                    str(err_sin),
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]
        except Exception as ex:
            resultado_validador.controls = [
                ft.Text(
                    f"Error al evaluar expresión regular: {ex}",
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]
        page.update()

    vista_ej1 = ft.Column(
        [
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    dd_validador,
                                    ft.OutlinedButton(
                                        "Cargar Ejemplo Válido",
                                        icon=ft.Icons.CHECK,
                                        on_click=lambda _: (
                                            setattr(
                                                campo_cadena_validar,
                                                "value",
                                                VALIDADORES_DEFECTO.get(dd_validador.value, {}).get("ejemplo_valido", ""),
                                            ),
                                            page.update(),
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        "Cargar Ejemplo Inválido",
                                        icon=ft.Icons.CLOSE,
                                        on_click=lambda _: (
                                            setattr(
                                                campo_cadena_validar,
                                                "value",
                                                VALIDADORES_DEFECTO.get(dd_validador.value, {}).get("ejemplo_invalido", ""),
                                            ),
                                            page.update(),
                                        ),
                                    ),
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                            txt_desc_validador,
                            campo_er_validador,
                            campo_macros_validador,
                            ft.Row(
                                [
                                    campo_cadena_validar,
                                    ft.Button(
                                        "Validar Cadena",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=probar_validador_click,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                    ),
                )
            ),
            resultado_validador,
        ],
        spacing=12,
    )

    # =================================================================
    # SECCIÓN 2: EXPRESIÓN REGULAR -> AUTÓMATA FINITO (THOMPSON + AFD MIN)
    # =================================================================
    estado_ej2 = {"pipeline": None}

    campo_er_ej2 = ft.TextField(
        label="Expresión Regular (operadores: * > concatenación > +, λ, ∅, escapes \\)",
        value="(a+b)*abb",
        hint_text="Ej: (a+b)*abb  |  0(0+1)*1  |  (a+λ)b*",
        prefix_icon=ft.Icons.FUNCTIONS,
        text_style=ft.TextStyle(font_family="monospace", size=14),
        expand=True,
    )

    campo_macros_ej2 = ft.TextField(
        label="Macros opcionales (ej: D = 0+1+2+3+4+5+6+7+8+9)",
        value="",
        hint_text="Dejar vacío si usas símbolos directos como a, b, 0, 1",
        text_style=ft.TextStyle(font_family="monospace", size=12),
        expand=True,
    )

    dd_etapa_ej2 = ft.Dropdown(
        label="Etapa de la conversión a visualizar",
        value="afn_lambda",
        width=360,
        options=[
            ft.dropdown.Option("afn_lambda", "1. AFN-λ Resultante (Construcción de Thompson)"),
            ft.dropdown.Option("afn_sin_lambda", "2. AFN Equivalente sin Transiciones λ"),
            ft.dropdown.Option("afd", "3. AFD Determinista (Construcción de Subconjuntos)"),
            ft.dropdown.Option("afd_minimo", "4. AFD Mínimo Equivalente (Hopcroft)"),
            ft.dropdown.Option("pasos_thompson", "5. Autómatas Parciales de Thompson (Paso a Paso)"),
        ],
    )

    btn_descargar_jff_ej2 = ft.OutlinedButton(
        "Descargar .JFF (JFLAP)",
        icon=ft.Icons.DOWNLOAD,
        disabled=True,
    )

    contenedor_res_ej2 = ft.Column(
        [
            ft.Text(
                "Ingresa una expresión regular y presiona 'Convertir ER → Autómata'.",
                color=ft.Colors.GREY_400,
            )
        ],
        spacing=12,
    )

    def renderizar_etapa_ej2(e=None):
        pipe = estado_ej2["pipeline"]
        if not pipe:
            return

        etapa = dd_etapa_ej2.value
        controles: List[ft.Control] = [
            ft.Container(
                padding=12,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.BLUE_400),
                border=ft.Border.all(1, ft.Colors.BLUE_400),
                content=ft.Text(
                    f"ER: '{pipe['expresion_original']}'   |   "
                    f"AFN-λ: {len(pipe['afn_lambda'].estados)} estados   |   "
                    f"AFN sin λ: {len(pipe['afn_sin_lambda'].estados)} estados   |   "
                    f"AFD: {pipe['estados_afd_antes_min']} estados   |   "
                    f"AFD Mínimo: {pipe['estados_afd_despues_min']} estados",
                    size=13,
                    weight=ft.FontWeight.W_500,
                    selectable=True,
                ),
            )
        ]

        if etapa == "pasos_thompson":
            for paso in pipe["pasos_thompson"]:
                controles.append(
                    ft.Container(
                        padding=12,
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"Paso {paso['paso']}: {paso['operacion']} — Subexpresión: {paso['subexpresion']}",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.AMBER_300,
                                ),
                                ft.Text(paso["descripcion"], size=12, color=ft.Colors.GREY_300),
                                construir_grafo_automata_canvas(
                                    paso["automata"],
                                    titulo=f"Parcial #{paso['paso']}: {paso['subexpresion']}",
                                    ancho=600,
                                    alto=250,
                                ),
                            ],
                            spacing=6,
                        ),
                    )
                )
        else:
            titulos_etapa = {
                "afn_lambda": "AFN-λ (Construcción Inductiva de Thompson)",
                "afn_sin_lambda": "AFN Equivalente sin Transiciones λ",
                "afd": "AFD Equivalente (Construcción de Subconjuntos)",
                "afd_minimo": "AFD Mínimo Equivalente (Hopcroft)",
            }
            auto_sel = pipe[etapa]
            tit = titulos_etapa[etapa]
            controles.append(
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "lg": 7},
                            controls=[
                                construir_grafo_automata_canvas(
                                    auto_sel,
                                    titulo=tit,
                                    ancho=640,
                                    alto=330,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "lg": 5},
                            controls=[
                                construir_tabla_transiciones_visual(
                                    auto_sel,
                                    titulo=f"Tabla δ — {tit}",
                                )
                            ],
                        ),
                    ],
                    spacing=12,
                    run_spacing=12,
                )
            )

        contenedor_res_ej2.controls = controles
        if e is not None:
            page.update()

    dd_etapa_ej2.on_select = renderizar_etapa_ej2

    def convertir_er_a_automata_click(e):
        er = (campo_er_ej2.value or "").strip()
        macros = _parsear_macros_usuario(campo_macros_ej2.value or "")
        try:
            pipe = er_a_pipeline_completo(er, macros=macros)
            estado_ej2["pipeline"] = pipe
            btn_descargar_jff_ej2.disabled = False
            renderizar_etapa_ej2()
            notificar(page, "Expresión regular compilada con éxito (Thompson → AFD mínimo).", False)
        except ErrorSintacticoER as err_sin:
            estado_ej2["pipeline"] = None
            btn_descargar_jff_ej2.disabled = True
            contenedor_res_ej2.controls = [
                ft.Text(
                    str(err_sin),
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]
        except Exception as ex:
            estado_ej2["pipeline"] = None
            btn_descargar_jff_ej2.disabled = True
            contenedor_res_ej2.controls = [
                ft.Text(
                    f"Error en conversión ER → Autómata: {ex}",
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]
        page.update()

    async def descargar_jff_ej2_click(e):
        pipe = estado_ej2["pipeline"]
        if not pipe:
            return
        etapa = dd_etapa_ej2.value
        auto_export = pipe["afn_lambda"] if etapa == "pasos_thompson" else pipe[etapa]
        try:
            xml_jff = exportar_automata_jff(auto_export)
            await picker_guardar_p4.save_file(
                dialog_title="Exportar autómata para JFLAP (.jff)",
                file_name=f"automata_{etapa}.jff",
                src_bytes=xml_jff.encode("utf-8"),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["jff"],
            )
            notificar(page, f"Archivo automata_{etapa}.jff listo para abrir en JFLAP.", False)
        except Exception as ex:
            notificar(page, f"Error al exportar .jff: {ex}", True)

    btn_descargar_jff_ej2.on_click = descargar_jff_ej2_click

    vista_ej2 = ft.Column(
        [
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        [
                            ft.Row([campo_er_ej2], spacing=10),
                            ft.Row([campo_macros_ej2], spacing=10),
                            ft.Row(
                                [
                                    ft.Button(
                                        "Convertir ER → Autómata",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=convertir_er_a_automata_click,
                                    ),
                                    dd_etapa_ej2,
                                    btn_descargar_jff_ej2,
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                    ),
                )
            ),
            contenedor_res_ej2,
        ],
        spacing=12,
    )

    # =================================================================
    # SECCIÓN 3: AUTÓMATA FINITO -> EXPRESIÓN REGULAR (GNFA)
    # =================================================================
    EJEMPLO_AFD_GNFA = """estados: q0, q1, q2
alfabeto: a, b
inicial: q0
finales: q2
transiciones:
q0, a -> q0
q0, b -> q1
q1, a -> q2
q1, b -> q1
q2, a -> q0
q2, b -> q1"""

    estado_gnfa = {"auto_archivo": None, "nombre_archivo": None}

    txt_banner_gnfa = ft.Text("", size=13, color=ft.Colors.BLUE_200, expand=True)
    banner_gnfa = ft.Container(
        visible=False,
        padding=10,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE_400),
        border=ft.Border.all(1, ft.Colors.BLUE_400),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                txt_banner_gnfa,
                ft.TextButton(
                    "Quitar archivo / Editar manual",
                    icon=ft.Icons.EDIT,
                    on_click=lambda _: limpiar_archivo_gnfa(),
                ),
            ]
        ),
    )

    editor_automata_gnfa = ft.TextField(
        label="Definición del Autómata Finito (o sube un archivo .jff / .json / .xml / .txt)",
        value=EJEMPLO_AFD_GNFA,
        multiline=True,
        min_lines=6,
        max_lines=9,
        text_style=ft.TextStyle(font_family="monospace", size=13),
        expand=True,
    )

    campo_orden_eliminacion = ft.TextField(
        label="Orden personalizado de eliminación de estados (opcional, separado por comas)",
        hint_text="Ej: q1, q0, q2 (vacío = orden alfabético)",
        expand=True,
    )

    campo_er_jflap = ft.TextField(
        label="Expresión Regular obtenida en JFLAP (opcional, para comprobar equivalencia)",
        hint_text="Ej: (a+bb*a)*(bb*a)",
        prefix_icon=ft.Icons.COMPARE_ARROWS,
        expand=True,
    )

    contenedor_res_ej3 = ft.Column(
        [
            ft.Text(
                "Define o sube un autómata y presiona 'Convertir Autómata → ER (GNFA)'.",
                color=ft.Colors.GREY_400,
            )
        ],
        spacing=12,
    )

    def aplicar_archivo_gnfa(nombre: str, contenido: str):
        auto = _parsear_automata_p4(contenido)
        estado_gnfa["auto_archivo"] = auto
        estado_gnfa["nombre_archivo"] = nombre
        txt_banner_gnfa.value = (
            f"Archivo cargado: '{nombre}' | Tipo: {auto.tipo} | "
            f"Estados: {len(auto.estados)} | Transiciones: {len(auto.transiciones)}"
        )
        banner_gnfa.visible = True
        editor_automata_gnfa.visible = False
        notificar(page, f"Autómata '{nombre}' cargado para conversión a ER.", False)
        page.update()

    def limpiar_archivo_gnfa():
        estado_gnfa["auto_archivo"] = None
        estado_gnfa["nombre_archivo"] = None
        banner_gnfa.visible = False
        editor_automata_gnfa.visible = True
        page.update()

    def on_upload_gnfa(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            ruta = os.path.join(UPLOAD_DIR, e.file_name)
            try:
                if os.path.exists(ruta):
                    with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                        aplicar_archivo_gnfa(e.file_name, f.read())
            except Exception as ex:
                notificar(page, f"Error leyendo archivo: {ex}", True)

    picker_cargar_gnfa.on_upload = on_upload_gnfa

    async def subir_automata_gnfa_click(e):
        try:
            archivos = await picker_cargar_gnfa.pick_files(
                dialog_title="Seleccionar Autómata (.jff, .json, .xml, .txt)",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.ANY,
            )
            if not archivos:
                return
            arch = archivos[0]
            if getattr(arch, "path", None):
                with open(arch.path, "r", encoding="utf-8", errors="replace") as f:
                    aplicar_archivo_gnfa(arch.name, f.read())
                return
            url = page.get_upload_url(arch.name, 600)
            await picker_cargar_gnfa.upload([ft.FilePickerUploadFile(name=arch.name, upload_url=url)])
        except Exception as ex:
            notificar(page, f"Error al cargar archivo: {ex}", True)

    def convertir_automata_a_er_click(e):
        try:
            auto = (
                estado_gnfa["auto_archivo"]
                if estado_gnfa["auto_archivo"] is not None
                else _parsear_automata_p4(editor_automata_gnfa.value or "")
            )

            det_info = verificar_determinismo_detallado(auto)
            orden_raw = (campo_orden_eliminacion.value or "").strip()
            orden = [x.strip() for x in orden_raw.split(",") if x.strip()] if orden_raw else None

            er_final, historial = automata_a_expresion_regular(auto, orden_eliminacion=orden)

            controles: List[ft.Control] = []

            # Aviso de verificación de determinismo (estado y símbolo conflictivo si aplica)
            color_det = ft.Colors.GREEN_400 if det_info["es_determinista"] else ft.Colors.AMBER_300
            controles.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.10, color_det),
                    border=ft.Border.all(1, color_det),
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.VERIFIED if det_info["es_determinista"] else ft.Icons.WARNING_AMBER,
                                color=color_det,
                            ),
                            ft.Text(det_info["motivo"], size=13, color=color_det, expand=True),
                        ]
                    ),
                )
            )

            # Resultado principal de ER obtenida
            controles.append(
                ft.Container(
                    padding=14,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN_400),
                    border=ft.Border.all(1, ft.Colors.GREEN_400),
                    content=ft.Column(
                        [
                            ft.Text("Expresión Regular Equivalente (GNFA):", size=13, color=ft.Colors.GREY_300),
                            ft.Text(
                                er_final,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                font_family="monospace",
                                color=ft.Colors.GREEN_300,
                                selectable=True,
                            ),
                        ],
                        spacing=4,
                    ),
                )
            )

            # Comparación opcional con ER obtenida en JFLAP
            er_jflap = (campo_er_jflap.value or "").strip()
            if er_jflap:
                comp = comparar_expresiones_regulares(er_final, er_jflap)
                c_eq = ft.Colors.GREEN_400 if comp["equivalentes"] else ft.Colors.RED_400
                controles.append(
                    ft.Container(
                        padding=12,
                        border_radius=8,
                        bgcolor=ft.Colors.with_opacity(0.10, c_eq),
                        border=ft.Border.all(1, c_eq),
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"Comparación con JFLAP ('{er_jflap}'): "
                                    f"{'EQUIVALENTES ✔' if comp['equivalentes'] else 'NO EQUIVALENTES ✘'}",
                                    weight=ft.FontWeight.BOLD,
                                    color=c_eq,
                                ),
                                ft.Text(comp["mensaje"], size=12, selectable=True),
                            ],
                            spacing=4,
                        ),
                    )
                )

            # Pasos de eliminación progresiva de estados en el GNFA
            for idx, paso in enumerate(historial, start=1):
                gnfa_snap = paso.get("gnfa_automata")
                bloque_paso: List[ft.Control] = [
                    ft.Text(
                        f"Paso {idx}: {paso['paso']}",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_300,
                    ),
                    ft.Text(paso["detalle"], size=12, color=ft.Colors.GREY_300, selectable=True),
                ]
                if isinstance(gnfa_snap, Automata) and gnfa_snap.estados:
                    bloque_paso.append(
                        construir_grafo_automata_canvas(
                            gnfa_snap,
                            titulo=f"GNFA — {paso['paso']}",
                            ancho=620,
                            alto=260,
                        )
                    )
                controles.append(
                    ft.Container(
                        padding=12,
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        content=ft.Column(bloque_paso, spacing=6),
                    )
                )

            contenedor_res_ej3.controls = controles
        except Exception as ex:
            contenedor_res_ej3.controls = [
                ft.Text(
                    f"Error en conversión Autómata → ER: {ex}",
                    color=ft.Colors.RED_400,
                    font_family="monospace",
                    size=13,
                    selectable=True,
                )
            ]
        page.update()

    vista_ej3 = ft.Column(
        [
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        [
                            banner_gnfa,
                            editor_automata_gnfa,
                            ft.Row([campo_orden_eliminacion, campo_er_jflap], spacing=10),
                            ft.Row(
                                [
                                    ft.Button(
                                        "Convertir Autómata → ER (GNFA)",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=convertir_automata_a_er_click,
                                    ),
                                    ft.OutlinedButton(
                                        "Subir Autómata (.jff / .json / .xml)",
                                        icon=ft.Icons.UPLOAD_FILE,
                                        on_click=subir_automata_gnfa_click,
                                    ),
                                ],
                                wrap=True,
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                    ),
                )
            ),
            contenedor_res_ej3,
        ],
        spacing=12,
    )

    # =================================================================
    # NAVEGACIÓN INTERNA ENTRE LOS 3 EJERCICIOS DE LA PRÁCTICA 4
    # =================================================================
    vistas_ejercicios = {
        1: vista_ej1,
        2: vista_ej2,
        3: vista_ej3,
    }
    contenedor_ejercicio = ft.Container(content=vista_ej1, expand=True)

    btn_tab_1 = ft.Button("1. Validadores con ER", icon=ft.Icons.SPELLCHECK)
    btn_tab_2 = ft.OutlinedButton("2. ER → Autómata (Thompson)", icon=ft.Icons.ACCOUNT_TREE)
    btn_tab_3 = ft.OutlinedButton("3. Autómata → ER (GNFA)", icon=ft.Icons.FUNCTIONS)

    def seleccionar_ejercicio(num: int):
        contenedor_ejercicio.content = vistas_ejercicios[num]
        btn_tab_1.style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700 if num == 1 else None,
            color=ft.Colors.WHITE if num == 1 else None,
        )
        btn_tab_2.style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700 if num == 2 else None,
            color=ft.Colors.WHITE if num == 2 else None,
        )
        btn_tab_3.style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700 if num == 3 else None,
            color=ft.Colors.WHITE if num == 3 else None,
        )
        page.update()

    btn_tab_1.on_click = lambda _: seleccionar_ejercicio(1)
    btn_tab_2.on_click = lambda _: seleccionar_ejercicio(2)
    btn_tab_3.on_click = lambda _: seleccionar_ejercicio(3)

    return ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Icon(ft.Icons.FUNCTIONS, size=28, color=ft.Colors.AMBER_400),
                    ft.Column(
                        [
                            ft.Text(
                                "Práctica 4: Expresiones Regulares y Teorema de Kleene",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Validación de patrones, compilación Thompson → AFD mínimo y eliminación de estados GNFA.",
                                size=12,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        spacing=2,
                    ),
                ]
            ),
            ft.Divider(),
            ft.Row([btn_tab_1, btn_tab_2, btn_tab_3], wrap=True, spacing=10),
            contenedor_ejercicio,
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=12,
    )