"""
Pruebas Unitarias para Algoritmos Formales de Práctica 3.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)
"""

import os
import tempfile
import pytest
from automata import Automata
from algoritmos_afn import eliminar_transiciones_lambda, construccion_subconjuntos
from minimizacion import eliminar_estados_inaccesibles, minimizar_afd, son_equivalentes
from validador_lotes import procesar_lote_cadenas, guardar_informe_lote


@pytest.fixture
def afnd_lambda_prueba():
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


def test_eliminacion_transiciones_lambda(afnd_lambda_prueba):
    """Comprueba que eliminar lambda preserve exactamente el lenguaje."""
    afn_sin_lambda = eliminar_transiciones_lambda(afnd_lambda_prueba)
    
    # No debe contener transiciones nulas
    assert all(not t.es_lambda() for t in afn_sin_lambda.transiciones)
    
    # Comprobar sobre diversas cadenas
    cadenas_prueba = ["", "0", "1", "01", "0011", "010", "10", "1100", "111"]
    for w in cadenas_prueba:
        res_orig, _ = afnd_lambda_prueba.simular_cadena(w)
        res_sin_l, _ = afn_sin_lambda.simular_cadena(w)
        assert res_orig == res_sin_l, f"Discrepancia en cadena '{w}': orig={res_orig}, sin_lambda={res_sin_l}"


def test_construccion_subconjuntos_y_determinismo(afnd_lambda_prueba):
    """Comprueba que la construcción de subconjuntos produzca un AFD determinista equivalente."""
    afd = construccion_subconjuntos(afnd_lambda_prueba)
    es_det, msg = afd.es_determinista()
    assert es_det is True, f"El autómata resultante no es determinista: {msg}"

    cadenas_prueba = ["", "0", "1", "01", "0011", "010", "10", "1100", "0101"]
    for w in cadenas_prueba:
        res_afn, _ = afnd_lambda_prueba.simular_cadena(w)
        res_afd, _ = afd.simular_cadena(w)
        assert res_afn == res_afd, f"Discrepancia en subconjuntos con '{w}': afn={res_afn}, afd={res_afd}"


def test_minimizacion_hopcroft():
    """Comprueba que la minimización de AFD reduzca estados preservando el lenguaje."""
    # AFD redundante de 4 estados que acepta cadenas que terminan en 1
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

    afd_min = minimizar_afd(auto)
    assert len(afd_min.estados) <= len(auto.estados)
    # q2 y q3 son equivalentes, y q1 es inaccesible -> se reduce a 2 estados
    assert len(afd_min.estados) == 2

    # Preservación de lenguaje
    for w in ["", "0", "1", "00", "01", "10", "11", "0101", "1110"]:
        assert auto.simular_cadena(w)[0] == afd_min.simular_cadena(w)[0]


def test_equivalencia_entre_automatas():
    """Prueba la función de decisión de equivalencia de lenguajes."""
    a1 = Automata()
    a1.agregar_estado("A", es_inicial=True, es_final=True)
    a1.agregar_transicion("A", "0", "A")

    a2 = Automata()
    a2.agregar_estado("B", es_inicial=True, es_final=True)
    a2.agregar_estado("C", es_final=True)
    a2.agregar_transicion("B", "0", "C")
    a2.agregar_transicion("C", "0", "B")

    equiv, msg = son_equivalentes(a1, a2, limite_longitud=5)
    assert equiv is True


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
            assert "total_cadenas" not in contenido  # Formato legible en tabla
    finally:
        for p in (temp_input, temp_output):
            if os.path.exists(p):
                os.remove(p)

