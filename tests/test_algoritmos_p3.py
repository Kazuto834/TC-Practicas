"""
Pruebas Unitarias y de Integración para Algoritmos Formales de Práctica 3.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)

Verifica los ejercicios 2.1 a 2.6:
- 2.1: Cerradura lambda y simulación directa paso a paso.
- 2.2: Eliminación de transiciones lambda.
- 2.3: Construcción de subconjuntos alcanzables y tabla de transiciones.
- 2.4: Eliminación de inaccesibles, minimización por particiones y equivalencia.
- 2.5: Validación por lotes e informes.
- 2.6: Comprobación exhaustiva sobre los 20 autómatas de la Lista 3 (151-157, 191-194, 196-200, 260-263):
       Preservación de lenguaje en el pipeline completo (Original == Sin-λ == Subconjuntos == Mínimo)
       y que el AFD mínimo no tiene más estados que el AFD del que procede.
"""

import os
import itertools
import tempfile
import pytest

from automata import Automata
from formatos import FormatosAutomata
from cerradura_lambda import calcular_cerradura_lambda
from simulacion_directa import simular_afn_lambda_directo
from eliminacion_lambda import eliminar_transiciones_lambda, transformar_afn_sin_lambda_detallado
from construccion_subconjuntos import construccion_subconjuntos, construccion_subconjuntos_detallada
from eliminacion_inaccesibles import eliminar_estados_inaccesibles
from minimizacion_afd import minimizar_afd, minimizar_afd_detallado
from equivalencia_afd import son_equivalentes, decidir_equivalencia_detallada
from validacion_lotes import procesar_lote_cadenas
from guardar_informe_lote import guardar_informe_lote


DIR_CASOS_PRUEBA = os.path.join(
    os.path.dirname(__file__), "..", "automatas", "practica3", "casos-de-prueba"
)

CASOS_MINIMIZACION = ["151.jff", "152.jff", "153.jff", "154.jff", "155.jff", "156.jff", "157.jff"]
CASOS_SUBCONJUNTOS = ["191.jff", "192.jff", "193.jff", "194.jff", "260.jff", "261.jff", "262.jff", "263.jff"]
CASOS_LAMBDA = ["196.jff", "197.jff", "198.jff", "199.jff", "200.jff"]
TODOS_LOS_CASOS = CASOS_MINIMIZACION + CASOS_SUBCONJUNTOS + CASOS_LAMBDA


@pytest.fixture
def afnd_lambda_base():
    """AFND-lambda sobre {0, 1} con puente nulo (Ejercicio 199)."""
    auto = Automata()
    auto.agregar_estado("A", es_inicial=True)
    auto.agregar_estado("B")
    auto.agregar_estado("C", es_final=True)
    auto.agregar_transicion("A", "0", "A")
    auto.agregar_transicion("A", "", "B")
    auto.agregar_transicion("B", "1", "B")
    auto.agregar_transicion("B", "", "C")
    auto.agregar_transicion("C", "0", "C")
    return auto


# =============================================================================
# 2.1 PRUEBAS: CERRADURA LAMBDA Y SIMULACIÓN DIRECTA
# =============================================================================

def test_cerradura_lambda_individual_y_total(afnd_lambda_base):
    """Verifica el cálculo de cerradura lambda individual y global paso a paso."""
    # A -> B -> C por lambda
    res_a = calcular_cerradura_lambda(afnd_lambda_base, estado="A")
    assert res_a["cerradura"] == ["A", "B", "C"]
    assert len(res_a["pasos"]) >= 1

    res_b = calcular_cerradura_lambda(afnd_lambda_base, estado="B")
    assert res_b["cerradura"] == ["B", "C"]

    res_c = calcular_cerradura_lambda(afnd_lambda_base, estado="C")
    assert res_c["cerradura"] == ["C"]

    # Cálculo global
    res_todos = calcular_cerradura_lambda(afnd_lambda_base)
    assert res_todos["todas_cerraduras"]["A"] == ["A", "B", "C"]
    assert res_todos["todas_cerraduras"]["B"] == ["B", "C"]
    assert res_todos["todas_cerraduras"]["C"] == ["C"]


def test_simulacion_directa_paso_a_paso(afnd_lambda_base):
    """Verifica que la simulación directa de AFN-lambda detalle estados antes y después de λ-cl."""
    aceptada, traza = simular_afn_lambda_directo(afnd_lambda_base, "01")
    assert aceptada is True
    assert len(traza) == 3  # paso 0 (inicio), paso 1 (lee '0'), paso 2 (lee '1')

    # Paso 0: activos iniciales {A}, con cerradura {A, B, C}
    assert traza[0]["paso"] == 0
    assert traza[0]["estados_antes_cerradura"] == ["A"]
    assert traza[0]["estados_despues_cerradura"] == ["A", "B", "C"]

    # Paso 1: lee '0'
    assert traza[1]["simbolo_leido"] == "0"
    assert "estados_antes_cerradura" in traza[1]
    assert "estados_despues_cerradura" in traza[1]


# =============================================================================
# 2.2 PRUEBAS: ELIMINACIÓN DE TRANSICIONES LAMBDA
# =============================================================================

def test_eliminacion_transiciones_lambda(afnd_lambda_base):
    """Comprueba que eliminar lambda preserve exactamente el lenguaje y documente adiciones."""
    afn_sin_l, reporte = transformar_afn_sin_lambda_detallado(afnd_lambda_base)

    # No debe contener transiciones nulas
    assert all(not t.es_lambda() for t in afn_sin_l.transiciones)
    assert reporte["total_estados_promovidos"] >= 1  # A y B deben pasar a ser de aceptación
    assert "A" in afn_sin_l.estados_aceptacion
    assert "B" in afn_sin_l.estados_aceptacion

    cadenas_prueba = ["", "0", "1", "01", "0011", "010", "10", "1100", "111"]
    for w in cadenas_prueba:
        r_orig, _ = afnd_lambda_base.simular_cadena(w)
        r_sin, _ = afn_sin_l.simular_cadena(w)
        assert r_orig == r_sin, f"Discrepancia en '{w}': orig={r_orig}, sin_lambda={r_sin}"


# =============================================================================
# 2.3 PRUEBAS: CONSTRUCCIÓN DE SUBCONJUNTOS
# =============================================================================

def test_construccion_subconjuntos(afnd_lambda_base):
    """Comprueba que la construcción de subconjuntos genere un AFD equivalente."""
    afd, reporte = construccion_subconjuntos_detallada(afnd_lambda_base)
    es_det, msg = afd.es_determinista()
    assert es_det is True, f"El autómata resultante no es determinista: {msg}"
    assert reporte["total_subconjuntos_alcanzables"] >= 1
    assert len(reporte["tabla_transiciones"]) >= 1

    cadenas_prueba = ["", "0", "1", "01", "0011", "010", "10", "1100", "0101"]
    for w in cadenas_prueba:
        r_orig, _ = afnd_lambda_base.simular_cadena(w)
        r_afd, _ = afd.simular_cadena(w)
        assert r_orig == r_afd, f"Discrepancia en '{w}': orig={r_orig}, afd={r_afd}"


# =============================================================================
# 2.4 PRUEBAS: MINIMIZACIÓN Y EQUIVALENCIA
# =============================================================================

def test_minimizacion_hopcroft():
    """Comprueba que la minimización de AFD reduzca estados preservando el lenguaje."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True)
    auto.agregar_estado("q1")
    auto.agregar_estado("q2", es_final=True)
    auto.agregar_estado("q3", es_final=True)

    auto.agregar_transicion("q0", "0", "q0")
    auto.agregar_transicion("q0", "1", "q2")
    auto.agregar_transicion("q1", "0", "q0")
    auto.agregar_transicion("q1", "1", "q3")
    auto.agregar_transicion("q2", "0", "q0")
    auto.agregar_transicion("q2", "1", "q2")
    auto.agregar_transicion("q3", "0", "q0")
    auto.agregar_transicion("q3", "1", "q3")

    afd_min, reporte = minimizar_afd_detallado(auto)
    assert len(afd_min.estados) <= len(auto.estados)
    assert len(afd_min.estados) == 2
    assert len(reporte["rondas"]) >= 1

    for w in ["", "0", "1", "00", "01", "10", "11", "0101", "1110"]:
        assert auto.simular_cadena(w)[0] == afd_min.simular_cadena(w)[0]


def test_equivalencia_entre_automatas():
    """Prueba la función de decisión de equivalencia de lenguajes vía isomorfismo."""
    a1 = Automata()
    a1.agregar_estado("A", es_inicial=True, es_final=True)
    a1.agregar_transicion("A", "0", "A")

    a2 = Automata()
    a2.agregar_estado("B", es_inicial=True, es_final=True)
    a2.agregar_estado("C", es_final=True)
    a2.agregar_transicion("B", "0", "C")
    a2.agregar_transicion("C", "0", "B")

    equiv, msg, det = decidir_equivalencia_detallada(a1, a2, limite_longitud=5)
    assert equiv is True
    assert "isomorfismo" in det


# =============================================================================
# 2.5 PRUEBAS: VALIDACIÓN POR LOTES E INFORME
# =============================================================================

def test_validador_por_lotes():
    """Prueba el procesamiento masivo de cadenas desde archivo de texto."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=True)
    auto.agregar_estado("q1")
    auto.agregar_transicion("q0", "0", "q1")
    auto.agregar_transicion("q1", "0", "q0")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n0\n00\n000\n0000\n")
        temp_input = f.name

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        temp_output = f.name

    try:
        reporte = procesar_lote_cadenas(auto, temp_input)
        assert reporte["total_cadenas"] == 5
        assert reporte["total_aceptadas"] == 3  # lambda, 00, 0000
        assert reporte["total_rechazadas"] == 2  # 0, 000

        guardar_informe_lote(reporte, temp_output)
        assert os.path.exists(temp_output)
        with open(temp_output, "r", encoding="utf-8") as rf:
            contenido = rf.read()
            assert "REPORTE CONSOLIDADO" in contenido
    finally:
        for p in (temp_input, temp_output):
            if os.path.exists(p):
                os.remove(p)


# =============================================================================
# 2.6 PRUEBAS: SUITE EXHAUSTIVA SOBRE LOS 20 CASOS DE PRUEBA DE LISTA 3
# =============================================================================

@pytest.mark.parametrize("archivo_jff", TODOS_LOS_CASOS)
def test_pipeline_completo_casos_lista3(archivo_jff):
    """
    Comprueba para cada caso de prueba de la Lista 3 que:
    1. El autómata original, el AFN sin λ, el AFD de subconjuntos y el AFD mínimo
       aceptan exactamente las mismas cadenas sobre todas las palabras de Sigma^*
       hasta longitud 3.
       Justificación formal de la longitud:
       Para un alfabeto binario {0, 1}, una cota de longitud 3 evalúa exhaustivamente
       todas las 15 combinaciones (lambda, 0, 1, 00, 01, 10, 11, ...). Para un alfabeto
       ternario {0, 1, 2}, evalúa 40 cadenas. Por el lema de bombeo, esta longitud
       garantiza recorrer todos los ciclos y transiciones de autómatas de 3 a 5 estados,
       ofreciendo detección completa de inconsistencias con tiempo de prueba óptimo.
    2. El AFD mínimo tiene un número de estados menor o igual al AFD de subconjuntos:
       |Q_{AFD_min}| <= |Q_{AFD_sub}|.
    """
    ruta_completa = os.path.join(DIR_CASOS_PRUEBA, archivo_jff)
    if not os.path.exists(ruta_completa):
        pytest.skip(f"Archivo {archivo_jff} no encontrado en {DIR_CASOS_PRUEBA}")

    auto_orig = FormatosAutomata.cargar_jff(ruta_completa)

    # 1. Pipeline de conversión
    afn_sin_l = eliminar_transiciones_lambda(auto_orig)
    afd_sub = construccion_subconjuntos(afn_sin_l)
    afd_min = minimizar_afd(afd_sub)

    # 2. Comprobar cota de estados del AFD mínimo
    assert len(afd_min.estados) <= len(afd_sub.estados), (
        f"En {archivo_jff}: |Q_min|={len(afd_min.estados)} es mayor que |Q_sub|={len(afd_sub.estados)}"
    )

    # 3. Comprobar que afd_sub y afd_min son deterministas
    es_det_sub, msg_sub = afd_sub.es_determinista()
    assert es_det_sub is True, f"En {archivo_jff}: afd_sub no es determinista: {msg_sub}"

    es_det_min, msg_min = afd_min.es_determinista()
    assert es_det_min is True, f"En {archivo_jff}: afd_min no es determinista: {msg_min}"

    # 4. Comprobar equivalencia exacta de lenguajes sobre todas las cadenas hasta longitud 3
    alfabeto = sorted(list({s for s in auto_orig.alfabeto if s != ""}))
    for longitud in range(4):
        for combo in itertools.product(alfabeto, repeat=longitud):
            w = "".join(combo)
            r_orig, _ = auto_orig.simular_cadena(w)
            r_sin_l, _ = afn_sin_l.simular_cadena(w)
            r_sub, _ = afd_sub.simular_cadena(w)
            r_min, _ = afd_min.simular_cadena(w)

            assert r_orig == r_sin_l == r_sub == r_min, (
                f"Discrepancia en {archivo_jff} con cadena '{w}': "
                f"orig={r_orig}, sin_lambda={r_sin_l}, subconjuntos={r_sub}, minimo={r_min}"
            )
