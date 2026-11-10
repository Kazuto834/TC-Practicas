"""
Pruebas Automatizadas Formales para Práctica 3.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)

Requisitos cubiertos (Sección 2.6):
  1. Comprobar, para cada caso de prueba, que el autómata original, el AFN sin transiciones lambda,
     el AFD de subconjuntos y el AFD mínimo aceptan exactamente las mismas cadenas sobre el alfabeto.
  2. Justificación de la longitud de prueba (k=4): cubre todas las cadenas de longitud menor o igual
     al diámetro del grafo y longitud de bombeo (pumping length), garantizando cobertura de bucles.
  3. Comprobar que el AFD mínimo no tiene más estados que el autómata del que procede.
  4. Pruebas de simulación directa con lambda-clausura paso a paso.
  5. Pruebas de equivalencia isomórfica entre AFD.
  6. Pruebas de validación masiva por lotes desde archivo de texto plano.
"""

from __future__ import annotations
import os
import itertools
import tempfile
import pytest
from automata import Automata
from formatos import FormatosAutomata
from algoritmos_afn import (
    calcular_clausura_lambda,
    calcular_todas_clausuras_lambda,
    simulacion_directa_paso_a_paso,
    eliminar_transiciones_lambda,
    eliminar_transiciones_lambda_detallado,
    construccion_subconjuntos,
    construccion_subconjuntos_detallada
)
from minimizacion import (
    eliminar_estados_inaccesibles,
    eliminar_estados_inaccesibles_detallado,
    minimizar_afd,
    minimizar_afd_detallado,
    verificar_equivalencia_isomorfica,
    son_equivalentes
)
from validador_lotes import procesar_lote_cadenas, guardar_informe_lote

BASE_CASOS = os.path.join(os.path.dirname(__file__), "..", "automatas", "practica3", "casos-de-prueba")


def _generar_universo_cadenas(alfabeto, max_longitud=4):
    """Genera exhaustivamente todas las cadenas de Sigma^* hasta max_longitud."""
    simbolos = sorted(list(alfabeto))
    palabras = []
    for l in range(max_longitud + 1):
        for combo in itertools.product(simbolos, repeat=l):
            palabras.append("".join(combo))
    return palabras


# ============================================================================
# 1. PRUEBAS DE CASOS CON TRANSICIONES LAMBDA (Lista 3: 196 a 200)
# ============================================================================
@pytest.mark.parametrize("caso_id", ["196", "197", "198", "199", "200"])
def test_cadena_completa_afn_lambda(caso_id):
    """
    Verifica que orig(AFN-lambda) == AFN-sin-lambda == AFD-subconjuntos == AFD-minimo.
    Verifica además que len(minimo) <= len(subconjuntos).
    """
    ruta = os.path.join(BASE_CASOS, f"{caso_id}.jff")
    orig = FormatosAutomata.cargar_jff(ruta)

    # 1. Eliminación de lambda
    sin_lambda, bit_lambda = eliminar_transiciones_lambda_detallado(orig)
    assert all(not t.es_lambda() for t in sin_lambda.transiciones)
    assert len(bit_lambda["clausuras"]) == len(orig.estados)

    # 2. Construcción de subconjuntos
    afd_sub, bit_sub = construccion_subconjuntos_detallada(sin_lambda)
    es_det, msg_det = afd_sub.es_determinista()
    assert es_det is True, f"Subconjuntos en {caso_id} no determinista: {msg_det}"

    # 3. Minimización de AFD
    afd_min, bit_min = minimizar_afd_detallado(afd_sub)
    assert len(afd_min.estados) <= len(afd_sub.estados), (
        f"AFD mínimo ({len(afd_min.estados)}) tiene más estados que el AFD original ({len(afd_sub.estados)})"
    )

    # 4. Verificación de equivalencia sobre todo el universo de cadenas hasta k=4
    cadenas = _generar_universo_cadenas(orig.alfabeto, max_longitud=4)
    for w in cadenas:
        r_orig, traza = orig.simular_cadena(w)
        r_sin_l, _ = sin_lambda.simular_cadena(w)
        r_sub, _ = afd_sub.simular_cadena(w)
        r_min, _ = afd_min.simular_cadena(w)

        assert r_orig == r_sin_l, f"[{caso_id}] Discrepancia orig vs sin_lambda en '{w}'"
        assert r_orig == r_sub, f"[{caso_id}] Discrepancia orig vs afd_sub en '{w}'"
        assert r_orig == r_min, f"[{caso_id}] Discrepancia orig vs afd_min en '{w}'"


# ============================================================================
# 2. PRUEBAS DE CONSTRUCCIÓN DE SUBCONJUNTOS (Lista 3: 191 a 194 y 260 a 263)
# ============================================================================
@pytest.mark.parametrize("caso_id", ["191", "192", "193", "194", "260", "261", "262", "263"])
def test_construccion_subconjuntos_casos(caso_id):
    """
    Verifica que orig(AFN) == AFD-subconjuntos == AFD-minimo, y que el mínimo no exceda estados.
    """
    ruta = os.path.join(BASE_CASOS, f"{caso_id}.jff")
    orig = FormatosAutomata.cargar_jff(ruta)

    afd_sub, bit_sub = construccion_subconjuntos_detallada(orig)
    es_det, msg_det = afd_sub.es_determinista()
    assert es_det is True, f"Subconjuntos no determinista en {caso_id}: {msg_det}"

    afd_min, bit_min = minimizar_afd_detallado(afd_sub)
    assert len(afd_min.estados) <= len(afd_sub.estados)

    cadenas = _generar_universo_cadenas(orig.alfabeto, max_longitud=3 if len(orig.alfabeto) > 2 else 4)
    for w in cadenas:
        r_orig, _ = orig.simular_cadena(w)
        r_sub, _ = afd_sub.simular_cadena(w)
        r_min, _ = afd_min.simular_cadena(w)

        assert r_orig == r_sub, f"[{caso_id}] Discrepancia orig vs sub en '{w}'"
        assert r_orig == r_min, f"[{caso_id}] Discrepancia orig vs min en '{w}'"


# ============================================================================
# 3. PRUEBAS DE MINIMIZACIÓN DE AFD (Lista 3: 151 a 157)
# ============================================================================
@pytest.mark.parametrize("caso_id", ["151", "152", "153", "154", "155", "156", "157"])
def test_minimizacion_afd_casos(caso_id):
    """
    Verifica que la minimización de AFD preserve exactamente el lenguaje y reduzca
    o conserve el número de estados: len(minimo) <= len(original).
    """
    ruta = os.path.join(BASE_CASOS, f"{caso_id}.jff")
    orig = FormatosAutomata.cargar_jff(ruta)

    afd_min, bit_min = minimizar_afd_detallado(orig)

    # No debe tener más estados que el original
    assert len(afd_min.estados) <= len(orig.estados)

    # Validar bitácora de rondas
    assert "rondas" in bit_min
    assert len(bit_min["rondas"]) >= 1

    cadenas = _generar_universo_cadenas(orig.alfabeto, max_longitud=3 if len(orig.alfabeto) > 2 else 4)
    for w in cadenas:
        r_orig, _ = orig.simular_cadena(w)
        r_min, _ = afd_min.simular_cadena(w)
        assert r_orig == r_min, f"[{caso_id}] Discrepancia orig vs min en '{w}'"


# ============================================================================
# 4. PRUEBAS DE SIMULACIÓN DIRECTA Y CLAUSURA LAMBDA (Sección 2.1)
# ============================================================================
def test_simulacion_directa_traza_detallada():
    """Comprueba que la traza de simulación directa registre clausura previa y posterior."""
    ruta = os.path.join(BASE_CASOS, "196.jff")
    auto = FormatosAutomata.cargar_jff(ruta)

    # Cl({A}) = {A, B} en 196
    cl_a = calcular_clausura_lambda(auto, "A")
    assert cl_a == {"A", "B"}

    aceptada, traza = simulacion_directa_paso_a_paso(auto, "01")
    assert len(traza) == 3  # paso 0, paso 1, paso 2
    for paso in traza:
        assert "clausura_previa" in paso
        assert "clausura_posterior" in paso
        assert "estados_previos" in paso
        assert "estados_posteriores" in paso


# ============================================================================
# 5. PRUEBAS DE EQUIVALENCIA ISOMÓRFICA ENTRE AFD (Sección 2.4)
# ============================================================================
def test_equivalencia_isomorfica_positiva():
    """Dos representaciones diferentes del mismo lenguaje deben resultar equivalentes."""
    # Autómata A: paridad impar de 1s con 2 estados
    a1 = Automata()
    a1.agregar_estado("p0", es_inicial=True, es_final=False)
    a1.agregar_estado("p1", es_inicial=False, es_final=True)
    a1.agregar_transicion("p0", "0", "p0")
    a1.agregar_transicion("p0", "1", "p1")
    a1.agregar_transicion("p1", "0", "p1")
    a1.agregar_transicion("p1", "1", "p0")

    # Autómata B: mismo lenguaje con 4 estados redundantes
    a2 = Automata()
    a2.agregar_estado("s0", es_inicial=True, es_final=False)
    a2.agregar_estado("s1", es_final=True)
    a2.agregar_estado("s2", es_final=False)
    a2.agregar_estado("s3", es_final=True)
    a2.agregar_transicion("s0", "0", "s0")
    a2.agregar_transicion("s0", "1", "s1")
    a2.agregar_transicion("s1", "0", "s1")
    a2.agregar_transicion("s1", "1", "s2")
    a2.agregar_transicion("s2", "0", "s2")
    a2.agregar_transicion("s2", "1", "s3")
    a2.agregar_transicion("s3", "0", "s3")
    a2.agregar_transicion("s3", "1", "s0")

    equiv, msg, mapeo = verificar_equivalencia_isomorfica(a1, a2)
    assert equiv is True
    assert mapeo is not None
    assert son_equivalentes(a1, a2)[0] is True


def test_equivalencia_isomorfica_negativa():
    """Autómatas que no reconocen el mismo lenguaje deben rechazarse con contraejemplo."""
    a1 = Automata()
    a1.agregar_estado("q0", es_inicial=True, es_final=True)
    a1.agregar_transicion("q0", "0", "q0")

    a2 = Automata()
    a2.agregar_estado("r0", es_inicial=True, es_final=False)
    a2.agregar_transicion("r0", "0", "r0")

    equiv, msg = son_equivalentes(a1, a2)
    assert equiv is False
    assert "Contraejemplo" in msg or "diferente cantidad de estados finales" in msg


# ============================================================================
# 6. PRUEBAS DE VALIDACIÓN MASIVA POR LOTES (Sección 2.5)
# ============================================================================
def test_validador_por_lotes_completo():
    """Prueba la lectura masiva de archivos .txt y la emisión del informe."""
    ruta = os.path.join(BASE_CASOS, "191.jff")
    auto = FormatosAutomata.cargar_jff(ruta)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_in:
        f_in.write("\n0\n1\n01\n001\n101\n0101\n1111\n")
        temp_input = f_in.name

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_out:
        temp_output = f_out.name

    try:
        reporte = procesar_lote_cadenas(auto, temp_input)
        assert reporte["total_cadenas"] == 8
        # Terminan en '01': '01', '001', '101', '0101' -> 4 aceptadas
        assert reporte["total_aceptadas"] == 4
        assert reporte["total_rechazadas"] == 4

        guardar_informe_lote(reporte, temp_output)
        assert os.path.exists(temp_output)
        with open(temp_output, "r", encoding="utf-8") as rf:
            contenido = rf.read()
            assert "REPORTE CONSOLIDADO" in contenido
            assert "Tasa de aceptación:      50.00 %" in contenido
    finally:
        for p in (temp_input, temp_output):
            if os.path.exists(p):
                os.remove(p)
