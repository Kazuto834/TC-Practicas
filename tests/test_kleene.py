"""
Pruebas del Teorema de Kleene Bidireccional (Práctica 4).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Cobertura:
  - Parser de expresiones regulares (AST)
  - Construcción de Thompson (ER → AFND-λ)
  - Eliminación de estados GNFA (Autómata → ER)
  - Viaje redondo completo (ER → AFD mín → ER → AFD mín ≡)
"""

import sys
import os
import itertools

import pytest

# Garantizar que el directorio src esté en el path para imports bare
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser_er import (
    ParserExpresionRegular,
    NodoAST,
    NodoVacio,
    NodoLambda,
    NodoSimbolo,
    NodoUnion,
    NodoConcatenacion,
    NodoEstrella,
    ErrorSintacticoER,
)
from er_a_automata import er_a_afnd_lambda, er_a_afd_minimo, CompiladorThompson
from automata_a_er import automata_a_expresion_regular
from automata import Automata


# =====================================================================
# Utilidades auxiliares
# =====================================================================

def _acepta(auto: Automata, cadena: str) -> bool:
    """Atajo: devuelve True si el autómata acepta la cadena."""
    aceptada, _ = auto.simular_cadena(cadena)
    return aceptada


def _generar_cadenas(alfabeto: str, max_longitud: int):
    """Genera todas las cadenas sobre *alfabeto* con longitud ≤ max_longitud."""
    cadenas = []
    for n in range(max_longitud + 1):
        for combo in itertools.product(alfabeto, repeat=n):
            cadenas.append("".join(combo))
    return cadenas


# =====================================================================
# Clase 1: Pruebas del Parser de Expresiones Regulares
# =====================================================================

class TestParserER:
    """Pruebas unitarias para el análisis léxico-sintáctico de expresiones regulares."""

    def test_parser_simbolo_simple(self):
        """Parsear 'a' debe producir un NodoSimbolo con simbolo='a'."""
        parser = ParserExpresionRegular("a")
        ast = parser.parsear()
        assert isinstance(ast, NodoSimbolo)
        assert ast.simbolo == "a"

    def test_parser_union(self):
        """Parsear 'a+b' debe producir NodoUnion(NodoSimbolo('a'), NodoSimbolo('b'))."""
        parser = ParserExpresionRegular("a+b")
        ast = parser.parsear()
        assert isinstance(ast, NodoUnion)
        assert isinstance(ast.izq, NodoSimbolo) and ast.izq.simbolo == "a"
        assert isinstance(ast.der, NodoSimbolo) and ast.der.simbolo == "b"

    def test_parser_concatenacion(self):
        """Parsear 'ab' debe producir NodoConcatenacion(NodoSimbolo('a'), NodoSimbolo('b'))."""
        parser = ParserExpresionRegular("ab")
        ast = parser.parsear()
        assert isinstance(ast, NodoConcatenacion)
        assert isinstance(ast.izq, NodoSimbolo) and ast.izq.simbolo == "a"
        assert isinstance(ast.der, NodoSimbolo) and ast.der.simbolo == "b"

    def test_parser_estrella(self):
        """Parsear 'a*' debe producir NodoEstrella(NodoSimbolo('a'))."""
        parser = ParserExpresionRegular("a*")
        ast = parser.parsear()
        assert isinstance(ast, NodoEstrella)
        assert isinstance(ast.hijo, NodoSimbolo) and ast.hijo.simbolo == "a"

    def test_parser_expresion_compleja(self):
        """Parsear '(a+b)*c' debe producir NodoConcatenacion(NodoEstrella(NodoUnion(...)), NodoSimbolo('c'))."""
        parser = ParserExpresionRegular("(a+b)*c")
        ast = parser.parsear()
        # Raíz: concatenación
        assert isinstance(ast, NodoConcatenacion)
        # Lado izquierdo: estrella de unión
        assert isinstance(ast.izq, NodoEstrella)
        assert isinstance(ast.izq.hijo, NodoUnion)
        assert isinstance(ast.izq.hijo.izq, NodoSimbolo) and ast.izq.hijo.izq.simbolo == "a"
        assert isinstance(ast.izq.hijo.der, NodoSimbolo) and ast.izq.hijo.der.simbolo == "b"
        # Lado derecho: símbolo 'c'
        assert isinstance(ast.der, NodoSimbolo) and ast.der.simbolo == "c"

    def test_parser_lambda(self):
        """Parsear 'λ' debe producir NodoLambda."""
        parser = ParserExpresionRegular("λ")
        ast = parser.parsear()
        assert isinstance(ast, NodoLambda)

    def test_parser_vacio(self):
        """Parsear '∅' debe producir NodoVacio."""
        parser = ParserExpresionRegular("∅")
        ast = parser.parsear()
        assert isinstance(ast, NodoVacio)

    def test_parser_error_parentesis(self):
        """Parsear '(a+b' (paréntesis sin cerrar) debe lanzar ErrorSintacticoER."""
        parser = ParserExpresionRegular("(a+b")
        with pytest.raises(ErrorSintacticoER):
            parser.parsear()

    def test_parser_error_operador_inicio(self):
        """Parsear '*a' (operador al inicio) debe lanzar ErrorSintacticoER."""
        parser = ParserExpresionRegular("*a")
        with pytest.raises(ErrorSintacticoER):
            parser.parsear()

    def test_parser_precedencia(self):
        """
        Parsear 'a+bc*' debe respetar la precedencia: * > concat > +
        Resultado esperado: NodoUnion(NodoSimbolo('a'), NodoConcatenacion(NodoSimbolo('b'), NodoEstrella(NodoSimbolo('c'))))
        """
        parser = ParserExpresionRegular("a+bc*")
        ast = parser.parsear()
        # Raíz: unión
        assert isinstance(ast, NodoUnion)
        # Lado izquierdo de la unión: símbolo 'a'
        assert isinstance(ast.izq, NodoSimbolo) and ast.izq.simbolo == "a"
        # Lado derecho de la unión: concatenación de 'b' con 'c*'
        assert isinstance(ast.der, NodoConcatenacion)
        assert isinstance(ast.der.izq, NodoSimbolo) and ast.der.izq.simbolo == "b"
        assert isinstance(ast.der.der, NodoEstrella)
        assert isinstance(ast.der.der.hijo, NodoSimbolo) and ast.der.der.hijo.simbolo == "c"


# =====================================================================
# Clase 2: Pruebas de la Construcción de Thompson (ER → AFND-λ)
# =====================================================================

class TestThompson:
    """Pruebas de la compilación inductiva de Thompson y la canalización completa."""

    def test_thompson_simbolo(self):
        """AFND-λ para 'a': acepta 'a', rechaza '', 'b', 'aa'."""
        auto = er_a_afnd_lambda("a")
        assert _acepta(auto, "a") is True
        assert _acepta(auto, "") is False
        assert _acepta(auto, "b") is False
        assert _acepta(auto, "aa") is False

    def test_thompson_union(self):
        """AFND-λ para 'a+b': acepta 'a','b'; rechaza '','ab','c'."""
        auto = er_a_afnd_lambda("a+b")
        assert _acepta(auto, "a") is True
        assert _acepta(auto, "b") is True
        assert _acepta(auto, "") is False
        assert _acepta(auto, "ab") is False
        assert _acepta(auto, "c") is False

    def test_thompson_concatenacion(self):
        """AFND-λ para 'ab': acepta 'ab'; rechaza 'a','b','','ba'."""
        auto = er_a_afnd_lambda("ab")
        assert _acepta(auto, "ab") is True
        assert _acepta(auto, "a") is False
        assert _acepta(auto, "b") is False
        assert _acepta(auto, "") is False
        assert _acepta(auto, "ba") is False

    def test_thompson_estrella(self):
        """AFND-λ para 'a*': acepta '','a','aa','aaa'; rechaza 'b','ab'."""
        auto = er_a_afnd_lambda("a*")
        assert _acepta(auto, "") is True
        assert _acepta(auto, "a") is True
        assert _acepta(auto, "aa") is True
        assert _acepta(auto, "aaa") is True
        assert _acepta(auto, "b") is False
        assert _acepta(auto, "ab") is False

    def test_thompson_compleja(self):
        """AFND-λ para '(a+b)*c': acepta 'c','ac','bc','abc','bac','aabbc'; rechaza '','a','b','ca'."""
        auto = er_a_afnd_lambda("(a+b)*c")
        for cadena_ok in ["c", "ac", "bc", "abc", "bac", "aabbc"]:
            assert _acepta(auto, cadena_ok) is True, f"Debió aceptar '{cadena_ok}'"
        for cadena_no in ["", "a", "b", "ca"]:
            assert _acepta(auto, cadena_no) is False, f"Debió rechazar '{cadena_no}'"

    def test_pipeline_completo(self):
        """
        Canalización completa ER → Thompson → Subconjuntos → Hopcroft para '(a+b)*ab'.
        El AFD mínimo resultante debe ser determinista y reconocer el lenguaje correcto.
        """
        afd = er_a_afd_minimo("(a+b)*ab")
        es_det, _ = afd.es_determinista()
        assert es_det is True, "El resultado de er_a_afd_minimo debe ser determinista."

        for cadena_ok in ["ab", "aab", "bab", "ababab"]:
            assert _acepta(afd, cadena_ok) is True, f"Debió aceptar '{cadena_ok}'"
        for cadena_no in ["", "a", "b", "ba", "aba"]:
            assert _acepta(afd, cadena_no) is False, f"Debió rechazar '{cadena_no}'"


# =====================================================================
# Clase 3: Pruebas de Conversión Autómata → Expresión Regular (GNFA)
# =====================================================================

class TestAutomataAER:
    """Pruebas de la eliminación de estados (GNFA) y equivalencia del lenguaje resultante."""

    def test_afd_simple_a_er(self):
        """
        Construye un AFD que acepta a*b, lo convierte a ER con GNFA,
        recompila esa ER y verifica equivalencia de lenguaje sobre ~20 cadenas.
        """
        # AFD para a*b
        afd_original = Automata()
        afd_original.agregar_estado("q0", es_inicial=True)
        afd_original.agregar_estado("q1", es_final=True)
        afd_original.agregar_transicion("q0", "a", "q0")
        afd_original.agregar_transicion("q0", "b", "q1")

        # Convertir a ER
        er_str, historial = automata_a_expresion_regular(afd_original)
        assert isinstance(er_str, str) and len(er_str) > 0, "La ER resultante no debe estar vacía."
        assert len(historial) > 0, "Debe existir al menos un paso de historial."

        # Recompilar la ER obtenida
        afd_recompilado = er_a_afd_minimo(er_str)

        # Verificar equivalencia sobre cadenas de prueba
        cadenas_prueba = _generar_cadenas("ab", 4)  # 2^0 + 2^1 + 2^2 + 2^3 + 2^4 = 31 cadenas
        for cadena in cadenas_prueba:
            resultado_orig = _acepta(afd_original, cadena)
            resultado_nuevo = _acepta(afd_recompilado, cadena)
            assert resultado_orig == resultado_nuevo, (
                f"Discrepancia en '{cadena}': original={resultado_orig}, "
                f"recompilado={resultado_nuevo} (ER generada: '{er_str}')"
            )

    def test_ciclo_completo_kleene(self):
        """
        Ciclo completo del Teorema de Kleene:
          ER₁ = '(0+1)*01'  →  AFD₁ mín  →  ER₂ (GNFA)  →  AFD₂ mín
        Verifica que AFD₁ ≡ AFD₂ sobre todas las cadenas binarias de longitud ≤ 5.
        """
        er_original = "(0+1)*01"
        afd1 = er_a_afd_minimo(er_original)

        # AFD₁ → ER₂
        er2, _ = automata_a_expresion_regular(afd1)

        # ER₂ → AFD₂
        afd2 = er_a_afd_minimo(er2)

        # Verificar equivalencia exhaustiva
        cadenas = _generar_cadenas("01", 5)
        for cadena in cadenas:
            r1 = _acepta(afd1, cadena)
            r2 = _acepta(afd2, cadena)
            assert r1 == r2, (
                f"Discrepancia en '{cadena}': AFD₁={r1}, AFD₂={r2} "
                f"(ER intermedia: '{er2}')"
            )


# =====================================================================
# Clase 4: Pruebas de Viaje Redondo del Teorema de Kleene
# =====================================================================

class TestKleeneBidireccional:
    """
    Verificación paramétrica del viaje redondo:
      ER → AFD mín → ER' → AFD' mín
    Para múltiples expresiones regulares representativas.
    """

    @pytest.mark.parametrize(
        "er",
        [
            "a*",
            "a+b",
            "(a+b)*",
            "ab*a",
            "(0+1)*00(0+1)*",
        ],
        ids=[
            "kleene_simple_a*",
            "union_a+b",
            "kleene_union_(a+b)*",
            "concat_ab*a",
            "binarias_con_00",
        ],
    )
    def test_roundtrip_er(self, er: str):
        """
        Viaje redondo para una expresión regular dada:
          1. Compilar ER a AFD mínimo.
          2. Convertir AFD a ER' vía GNFA.
          3. Compilar ER' a un segundo AFD mínimo.
          4. Verificar equivalencia de lenguaje sobre todas las cadenas
             del alfabeto detectado con longitud ≤ 4.
        """
        # Paso 1: ER → AFD₁
        afd1 = er_a_afd_minimo(er)

        # Paso 2: AFD₁ → ER'
        er_generada, historial = automata_a_expresion_regular(afd1)
        assert isinstance(er_generada, str), "La conversión GNFA debe retornar una cadena."

        # Paso 3: ER' → AFD₂
        afd2 = er_a_afd_minimo(er_generada)

        # Determinar alfabeto de prueba
        alfabeto = "".join(sorted(afd1.alfabeto))
        if not alfabeto:
            alfabeto = "ab"

        # Paso 4: Verificación exhaustiva
        cadenas = _generar_cadenas(alfabeto, 4)
        for cadena in cadenas:
            r1 = _acepta(afd1, cadena)
            r2 = _acepta(afd2, cadena)
            assert r1 == r2, (
                f"[ER='{er}'] Discrepancia en '{cadena}': "
                f"AFD₁={r1}, AFD₂={r2} (ER intermedia: '{er_generada}')"
            )
