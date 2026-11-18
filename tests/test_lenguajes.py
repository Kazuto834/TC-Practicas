"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS: OPERACIONES SOBRE CADENAS Y LENGUAJES
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Verifica formalmente las operaciones sobre cadenas y alfabetos de la
    Práctica 1 reutilizadas en la Práctica 2 (conforme a los Ejercicios 1 y 3.4):
      - Prefijos (longitud 0, 1 y n)
      - Sufijos (longitud 0, 1 y n)
      - Subcadenas (incluyendo la cadena vacía lambda)
      - Cerradura de Kleene (Sigma*)
      - Cerradura Positiva (Sigma+)
===============================================================================
"""

import pytest
from lenguajes import (
    prefijos,
    sufijos,
    subcadenas,
    cerradura_Kleene,
    cerradura_positiva,
)


# =============================================================================
# SECCIÓN 1: PRUEBAS DE PREFIJOS, SUFIJOS Y SUBCADENAS
# =============================================================================

def test_cadena_vacia():
    """Verifica el comportamiento con la cadena vacía lambda."""
    assert prefijos("") == [""]
    assert sufijos("") == [""]
    assert subcadenas("") == [""]


def test_cadena_longitud_uno():
    """Verifica operaciones con cadenas unitarias |w| = 1."""
    assert set(prefijos("a")) == {"", "a"}
    assert set(sufijos("a")) == {"", "a"}
    assert set(subcadenas("a")) == {"", "a"}


def test_prefijos_y_sufijos_longitud_multiple():
    """Verifica orden y completitud de prefijos y sufijos en cadenas de longitud n > 1."""
    cadena = "abc"
    esperado_pref = ["", "a", "ab", "abc"]
    esperado_suf = ["abc", "bc", "c", ""]

    assert prefijos(cadena) == esperado_pref
    assert sufijos(cadena) == esperado_suf


def test_subcadenas_completitud():
    """Verifica que se generen todas las subcadenas sin duplicados y con lambda."""
    cadena = "aba"
    resultado = subcadenas(cadena)
    esperado = {"", "a", "b", "ab", "ba", "aba"}

    assert set(resultado) == esperado
    assert "" in resultado


# =============================================================================
# SECCIÓN 2: PRUEBAS DE CERRADURA DE KLEENE Y POSITIVA
# =============================================================================

def test_diferencia_kleene_y_positiva_longitud_cero():
    """
    Verifica que la cerradura de Kleene incluya lambda en longitud 0
    mientras que la cerradura positiva no incluya elementos.
    """
    alfabeto = {"a", "b"}

    res_kleene = cerradura_Kleene(alfabeto, maxlength=0)
    res_positiva = cerradura_positiva(alfabeto, maxlength=0)

    assert res_kleene == [""]
    assert res_positiva == []
    assert res_kleene != res_positiva


def test_alfabeto_un_simbolo():
    """Verifica la generación recursiva con alfabeto unario Sigma = {a}."""
    alfabeto = {"a"}

    res_kleene = cerradura_Kleene(alfabeto, maxlength=4)
    assert set(res_kleene) == {"", "a", "aa", "aaa", "aaaa"}

    res_positiva = cerradura_positiva(alfabeto, maxlength=4)
    assert set(res_positiva) == {"a", "aa", "aaa", "aaaa"}


def test_cerraduras_alfabeto_binario():
    """Verifica la generación exhaustiva sobre alfabeto binario Sigma = {0, 1}."""
    alfabeto = ["0", "1"]

    res_k2 = cerradura_Kleene(alfabeto, maxlength=2)
    esperado_k2 = {"", "0", "1", "00", "01", "10", "11"}
    assert set(res_k2) == esperado_k2
    assert len(res_k2) == 1 + 2 + 4  # 7 palabras

    res_p2 = cerradura_positiva(alfabeto, maxlength=2)
    esperado_p2 = {"0", "1", "00", "01", "10", "11"}
    assert set(res_p2) == esperado_p2
    assert "" not in res_p2
    assert len(res_p2) == 6
