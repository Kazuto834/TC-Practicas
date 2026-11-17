"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS: MOTOR FORMAL DE AUTÓMATAS (AFD, AFND, AFND-λ)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Pruebas exhaustivas para la quíntupla matemática formal de autómatas finitos
    (conforme a los Ejercicios 2, 3 y 3.5 de la Práctica 2):
      - Aceptación y rechazo riguroso de cadenas en AFD.
      - Simulación concurrente de bifurcaciones en AFND.
      - Cálculo de λ-clausura reflexiva y transitiva (incluyendo ciclos).
      - Reconocimiento de cadenas en AFND-λ dependientes de la λ-clausura (3.5).
      - Generación de traza paso a paso detallada.
      - Validación de consistencia matemática de la quíntupla.
===============================================================================
"""

import pytest
from automata import Automata, Transicion, Estado


# =============================================================================
# SECCIÓN 1: PRUEBAS EN AUTÓMATAS FINITOS DETERMINISTAS (AFD)
# =============================================================================

def test_afd_paridad_ceros():
    """
    Prueba un AFD que reconoce cadenas con número par de ceros sobre {0, 1}
    (Ejercicio 139 de la Lista 2). Verifica aceptación y rechazo riguroso (3.5).
    """
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

    # Cadenas aceptadas (número par de ceros)
    assert auto.simular_cadena("")[0] is True
    assert auto.simular_cadena("1")[0] is True
    assert auto.simular_cadena("00")[0] is True
    assert auto.simular_cadena("10101")[0] is True
    assert auto.simular_cadena("1110000")[0] is True

    # Cadenas rechazadas (número impar de ceros)
    assert auto.simular_cadena("0")[0] is False
    assert auto.simular_cadena("10")[0] is False
    assert auto.simular_cadena("000")[0] is False
    assert auto.simular_cadena("10111")[0] is False


def test_afd_rechazo_simbolos_invalidos_y_estados_muertos():
    """Comprueba el rechazo formal ante símbolos extraños o ausencia de transiciones."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=True)
    auto.agregar_transicion("q0", "a", "q1")

    # Símbolo no perteneciente al alfabeto
    aceptada_inv, traza_inv = auto.simular_cadena("z")
    assert aceptada_inv is False
    assert "error" in traza_inv[-1]

    # Estado sumidero / sin transición para 'b'
    assert auto.simular_cadena("b")[0] is False

    # Ausencia de transición desde q1
    assert auto.simular_cadena("aa")[0] is False


# =============================================================================
# SECCIÓN 2: PRUEBAS EN AUTÓMATAS NO DETERMINISTAS (AFND)
# =============================================================================

def test_afnd_termina_en_01():
    """Prueba un AFND estándar que reconoce cadenas que terminan en 01 sobre {0, 1}."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    auto.agregar_estado("q2", es_inicial=False, es_final=True)

    # q0 lee 0 -> se mantiene en q0 o transita a q1 (no determinismo)
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


def test_afnd_bifurcaciones_multiples_con_caminos_muertos():
    """
    Comprueba que el simulador explore todas las ramas concurrentes
    cuando un camino llega a un callejón sin salida pero otro llega a aceptación.
    """
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False)
    auto.agregar_estado("q1", es_inicial=False, es_final=False)
    auto.agregar_estado("q2", es_inicial=False, es_final=True)

    auto.agregar_transicion("q0", "a", "q1")
    auto.agregar_transicion("q0", "a", "q2")

    aceptada, traza = auto.simular_cadena("a")
    assert aceptada is True
    assert "q2" in traza[1]["clausura_posterior"]

    # Cadena 'ab' muere en ambas ramas
    assert auto.simular_cadena("ab")[0] is False


# =============================================================================
# SECCIÓN 3: PRUEBAS EN AFND-λ Y CÁLCULO DE LAMBDA-CLAUSURA (3.5)
# =============================================================================

def test_afnd_lambda_clausura():
    """
    Prueba el AFND-lambda del Anexo 3 de la especificación oficial.
    Requisito 3.5: La aceptación de una cadena cuyo reconocimiento requiera la λ-clausura.
    """
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
    assert auto.clausura_lambda({"q0"}) == {"q0", "q1"}
    assert auto.clausura_lambda({"q1"}) == {"q1"}

    # Cadena vacía '' aceptada gracias a que q0 alcanza q1 por lambda-clausura
    aceptada_vacia, traza_vacia = auto.simular_cadena("")
    assert aceptada_vacia is True
    assert traza_vacia[0]["es_aceptacion"] is True

    # Cadena 'b' aceptada: q0 -b-> q0 -lambda-> q1
    aceptada_b, traza_b = auto.simular_cadena("b")
    assert aceptada_b is True


def test_afnd_lambda_transitividad_multiple():
    """Verifica transitividad estricta en cadenas de transiciones lambda q0 -> q1 -> q2 -> q3."""
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

    # La cadena vacía alcanza el estado de aceptación q3
    aceptada, traza = auto.simular_cadena("")
    assert aceptada is True
    assert traza[0]["es_aceptacion"] is True


def test_ciclo_transiciones_lambda():
    """Verifica que ciclos en transiciones lambda no provoquen bucles infinitos."""
    auto = Automata()
    auto.agregar_estado("A", es_inicial=True)
    auto.agregar_estado("B")
    auto.agregar_transicion("A", "", "B")
    auto.agregar_transicion("B", "", "A")

    clausura = auto.clausura_lambda({"A"})
    assert clausura == {"A", "B"}


# =============================================================================
# SECCIÓN 4: PRUEBAS DE TRAZA, TRANSICIÓN EXTENDIDA Y CONSISTENCIA
# =============================================================================

def test_traza_paso_a_paso():
    """Comprueba que la traza registre fielmente cada paso con su información."""
    auto = Automata()
    auto.agregar_estado("A", es_inicial=True, es_final=False)
    auto.agregar_estado("B", es_inicial=False, es_final=True)
    auto.agregar_transicion("A", "x", "B")

    aceptada, traza = auto.simular_cadena("x")
    assert aceptada is True
    assert len(traza) == 2  # Paso 0 (inicio) y Paso 1
    assert traza[1]["simbolo_leido"] == "x"
    assert traza[1]["transiciones_tomadas"] == [{"desde": "A", "lee": "x", "hacia": "B"}]


def test_mover_conjunto_estados():
    """Verifica la función Delta(S, a) sobre subconjuntos de estados."""
    auto = Automata()
    auto.agregar_estado("q0")
    auto.agregar_estado("q1")
    auto.agregar_estado("q2")
    auto.agregar_transicion("q0", "a", "q1")
    auto.agregar_transicion("q2", "a", "q1")

    assert auto.mover({"q0", "q2"}, "a") == {"q1"}
    assert auto.mover({"q1"}, "a") == set()


def test_validar_consistencia_automata():
    """Verifica la detección de anomalías e inconsistencias formales."""
    # Autómata consistente
    auto_valido = Automata()
    auto_valido.agregar_estado("q0", es_inicial=True, es_final=True)
    auto_valido.agregar_transicion("q0", "0", "q0")
    es_cons, errores = auto_valido.validar_consistencia()
    assert es_cons is True
    assert len(errores) == 0

    # Autómata inconsistente: sin estado inicial
    auto_invalido = Automata(estados={"q0", "q1"}, alfabeto={"0"})
    es_cons, errores = auto_invalido.validar_consistencia()
    assert es_cons is False
    assert any("inicial" in err for err in errores)
