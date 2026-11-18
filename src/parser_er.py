"""
Módulo de Análisis Léxico y Sintáctico de Expresiones Regulares (Práctica 4).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Tokenizer y Parser sintáctico descendente recursivo
                con precedencia de operadores (* > concatenación > +)
                y diagnóstico posicional exacto de errores sintácticos.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Set


# =============================================================================
# ÁRBOL DE SINTAXIS ABSTRACTA (AST)
# =============================================================================
class NodoAST:
    """Nodo base del AST para expresiones regulares."""
    pass


@dataclass
class NodoVacio(NodoAST):
    """Representa el lenguaje vacío ∅."""
    pass


@dataclass
class NodoLambda(NodoAST):
    """Representa la cadena vacía λ (o ε)."""
    pass


@dataclass
class NodoSimbolo(NodoAST):
    """Representa un símbolo atómico del alfabeto."""
    simbolo: str


@dataclass
class NodoUnion(NodoAST):
    """Representa la unión de dos lenguajes: izq + der."""
    izq: NodoAST
    der: NodoAST


@dataclass
class NodoConcatenacion(NodoAST):
    """Representa la concatenación de dos lenguajes: izq · der."""
    izq: NodoAST
    der: NodoAST


@dataclass
class NodoEstrella(NodoAST):
    """Representa la cerradura de Kleene: nodo*."""
    hijo: NodoAST


# =============================================================================
# PARSER DESCENDENTE RECURSIVO CON DIAGNÓSTICO POSICIONAL
# =============================================================================
class ErrorSintacticoER(Exception):
    def __init__(self, mensaje: str, posicion: int):
        self.mensaje = mensaje
        self.posicion = posicion
        super().__init__(f"Error sintáctico en columna {posicion}: {mensaje}")


class ParserExpresionRegular:
    """
    Gramática formal:
      E -> T ('+' T)*          (Unión)
      T -> F (F)*              (Concatenación implícita)
      F -> Atom ('*')*         (Cerradura de Kleene)
      Atom -> Simbolo | 'λ' | '∅' | '(' E ')'
    """

    def __init__(self, expresion: str):
        self.texto: str = expresion
        self.pos: int = 0
        self.longitud: int = len(expresion)
        self.alfabeto_detectado: Set[str] = set()

    def _mirar(self) -> Optional[str]:
        while self.pos < self.longitud and self.texto[self.pos].isspace():
            self.pos += 1
        if self.pos < self.longitud:
            return self.texto[self.pos]
        return None

    def _consumir(self) -> str:
        ch = self._mirar()
        if ch is not None:
            self.pos += 1
            return ch
        raise ErrorSintacticoER("Fin inesperado de la expresión.", self.pos)

    def parsear(self) -> NodoAST:
        """Punto de entrada principal. Retorna la raíz del AST o lanza ErrorSintacticoER."""
        if not self.texto.strip():
            # Expresión vacía equivale a lambda
            return NodoLambda()

        self.pos = 0
        ast = self._parse_union()
        if self._mirar() is not None:
            raise ErrorSintacticoER(f"Carácter inesperado '{self._mirar()}'.", self.pos)
        return ast

    def _parse_union(self) -> NodoAST:
        izq = self._parse_concatenacion()
        while self._mirar() == "+":
            self._consumir()  # consumir '+'
            der = self._parse_concatenacion()
            izq = NodoUnion(izq=izq, der=der)
        return izq

    def _parse_concatenacion(self) -> NodoAST:
        factores = []
        while True:
            ch = self._mirar()
            if ch is None or ch in ("+", ")"):
                break
            factor = self._parse_estrella()
            factores.append(factor)

        if not factores:
            raise ErrorSintacticoER("Se esperaba un operando antes del operador o fin de bloque.", self.pos)

        resultado = factores[0]
        for f in factores[1:]:
            resultado = NodoConcatenacion(izq=resultado, der=f)
        return resultado

    def _parse_estrella(self) -> NodoAST:
        nodo = self._parse_atomo()
        while self._mirar() == "*":
            self._consumir()  # consumir '*'
            nodo = NodoEstrella(hijo=nodo)
        return nodo

    def _parse_atomo(self) -> NodoAST:
        ch = self._mirar()
        if ch is None:
            raise ErrorSintacticoER("Se esperaba un símbolo u operando al final de la expresión.", self.pos)

        if ch == "(":
            pos_par = self.pos
            self._consumir()  # '('
            sub_expr = self._parse_union()
            if self._mirar() != ")":
                raise ErrorSintacticoER(f"Paréntesis abierto en pos {pos_par} sin cerrar.", self.pos)
            self._consumir()  # ')'
            return sub_expr
        elif ch in ("λ", "ε", "\\"):
            self._consumir()
            return NodoLambda()
        elif ch in ("∅", "Ø"):
            self._consumir()
            return NodoVacio()
        elif ch in ("+", "*", ")"):
            raise ErrorSintacticoER(f"Operador '{ch}' en posición inválida.", self.pos)
        else:
            simb = self._consumir()
            self.alfabeto_detectado.add(simb)
            return NodoSimbolo(simbolo=simb)

