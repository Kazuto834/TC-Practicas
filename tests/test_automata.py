"""
Pruebas Unitarias para el Motor Formal de Autómatas.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
"""

import pytest
from automata import Automata, Transicion, Estado


def test_afd_paridad_ceros():
    """Prueba un AFD que reconoce cadenas con número par de ceros sobre {0, 1} (Ej. 139)."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=True)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    
    auto.agregar_transicion("q0", "0", "q1")
    auto.agregar_transicion("q0", "1", "q0")
    auto.agregar_transicion("q1", "0", "q0")
    auto.agregar_transicion("q1", "1", "q1")

    es_det, msg = auto.es_determinista()
    assert es_det is True
    assert auto.tipo == "AFD"

    # Cadenas aceptadas (par de ceros)
    assert auto.simular_cadena("")[0] is True
    assert auto.simular_cadena("1")[0] is True
    assert auto.simular_cadena("00")[0] is True
    assert auto.simular_cadena("10101")[0] is True
    assert auto.simular_cadena("1110000")[0] is True

    # Cadenas rechazadas (impar de ceros)
    assert auto.simular_cadena("0")[0] is False
    assert auto.simular_cadena("10")[0] is False
    assert auto.simular_cadena("000")[0] is False
    assert auto.simular_cadena("10111")[0] is False


def test_afnd_termina_en_01():
    """Prueba un AFND que reconoce cadenas que terminan en 01 sobre {0, 1}."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    auto.agregar_estado("q2", es_inicial=False, es_final=True)

    # q0 lee 0 -> se queda en q0 o pasa a q1
    auto.agregar_transicion("q0", "0", "q0")
    auto.agregar_transicion("q0", "1", "q0")
    auto.agregar_transicion("q0", "0", "q1")
    auto.agregar_transicion("q1", "1", "q2")

    es_det, _ = auto.es_determinista()
    assert es_det is False
    assert auto.tipo == "AFND"

    # Cadenas válidas
    assert auto.simular_cadena("01")[0] is True
    assert auto.simular_cadena("0001")[0] is True
    assert auto.simular_cadena("1101")[0] is True
    assert auto.simular_cadena("10101")[0] is True

    # Cadenas inválidas
    assert auto.simular_cadena("")[0] is False
    assert auto.simular_cadena("0")[0] is False
    assert auto.simular_cadena("10")[0] is False
    assert auto.simular_cadena("010")[0] is False


def test_afnd_lambda_clausura():
    """Prueba el AFND-lambda del Anexo 3 de la especificación oficial."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=True)

    auto.agregar_transicion("q0", "a", "q1")
    auto.agregar_transicion("q0", "b", "q0")
    auto.agregar_transicion("q0", "", "q1")  # Transición lambda

    assert auto.tipo == "AFND-lambda"
    es_det, msg = auto.es_determinista()
    assert es_det is False
    assert "lambda" in msg.lower()

    # Cálculo formal de lambda-clausura
    clausura_q0 = auto.clausura_lambda({"q0"})
    assert clausura_q0 == {"q0", "q1"}

    clausura_q1 = auto.clausura_lambda({"q1"})
    assert clausura_q1 == {"q1"}

    # Cadena vacía '' debe ser aceptada gracias a la lambda-clausura inicial que alcanza q1
    aceptada_vacia, traza_vacia = auto.simular_cadena("")
    assert aceptada_vacia is True
    assert traza_vacia[0]["es_aceptacion"] is True

    # Cadena 'b' debe ser aceptada (q0 ->b-> q0 ->lambda-> q1)
    aceptada_b, traza_b = auto.simular_cadena("b")
    assert aceptada_b is True


def test_traza_paso_a_paso():
    """Comprueba que la traza incluya cada paso con sus transiciones tomadas."""
    auto = Automata()
    auto.agregar_estado("A", es_inicial=True, es_final=False)
    auto.agregar_estado("B", es_inicial=False, es_final=True)
    auto.agregar_transicion("A", "x", "B")

    aceptada, traza = auto.simular_cadena("x")
    assert aceptada is True
    assert len(traza) == 2  # Paso 0 (inicio) y Paso 1
    assert traza[1]["simbolo_leido"] == "x"
    assert traza[1]["transiciones_tomadas"] == [{"desde": "A", "lee": "x", "hacia": "B"}]


def test_afd_rechazo_simbolos_invalidos_y_estados_muertos():
    """Comprueba el rechazo formal de cadenas con símbolos inválidos o sin transición."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=True)
    auto.agregar_transicion("q0", "a", "q1")

    # Símbolo no perteneciente al alfabeto o sin transición desde q0
    assert auto.simular_cadena("b")[0] is False
    assert auto.simular_cadena("z")[0] is False

    # Estado muerto: desde q1 no hay transiciones para ningún símbolo
    assert auto.simular_cadena("aa")[0] is False
    assert auto.simular_cadena("ab")[0] is False


def test_afnd_bifurcaciones_multiples_con_caminos_muertos():
    """
    Comprueba que el AFND explore ramas concurrentes donde una rama muere
    (callejón sin salida) pero otra llega a un estado de aceptación.
    """
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    auto.agregar_estado("q2", es_inicial=False, es_final=True)

    # Desde q0 con 'a': va a q1 (rama muerta) y a q2 (rama aceptante)
    auto.agregar_transicion("q0", "a", "q1")
    auto.agregar_transicion("q0", "a", "q2")

    # Cadena 'a' debe ser aceptada porque q2 es final, aunque q1 muera
    aceptada, traza = auto.simular_cadena("a")
    assert aceptada is True
    assert "q2" in traza[1]["clausura_posterior"]

    # Cadena 'ab' debe morir en ambas ramas
    assert auto.simular_cadena("ab")[0] is False


def test_afnd_lambda_cadena_multiple():
    """
    Verifica que la lambda-clausura sea estrictamente transitiva a lo largo de
    múltiples transiciones lambda encadenadas (q0 -> q1 -> q2 -> q3).
    """
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    auto.agregar_estado("q2", es_inicial=False, es_final=False)
    auto.agregar_estado("q3", es_inicial=False, es_final=True)

    auto.agregar_transicion("q0", "", "q1")
    auto.agregar_transicion("q1", "", "q2")
    auto.agregar_transicion("q2", "", "q3")

    clausura_q0 = auto.clausura_lambda({"q0"})
    assert clausura_q0 == {"q0", "q1", "q2", "q3"}

    # Por transitividad lambda, la cadena vacía debe ser aceptada de inmediato
    aceptada, traza = auto.simular_cadena("")
    assert aceptada is True
    assert traza[0]["es_aceptacion"] is True

