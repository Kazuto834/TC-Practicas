"""
Módulo de Análisis Léxico y Sintáctico de Expresiones Regulares (Práctica 4).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Tokenizer y Parser sintáctico descendente recursivo
                con precedencia de operadores (* > concatenación > +),
                soporte de clases de símbolos (macros), escapes literales
                y diagnóstico posicional exacto de errores sintácticos.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Set


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
    """Error sintáctico que indica la posición exacta (índice y columna) del fallo."""

    def __init__(self, mensaje: str, posicion: int, expresion: str = ""):
        self.mensaje = mensaje
        self.posicion = posicion
        self.expresion = expresion
        if expresion:
            puntero = " " * max(0, posicion) + "^"
            detalle = (
                f"Error sintáctico en posición {posicion} (columna {posicion + 1}): {mensaje}\n"
                f"  Expresión: {expresion}\n"
                f"             {puntero}"
            )
        else:
            detalle = f"Error sintáctico en posición {posicion} (columna {posicion + 1}): {mensaje}"
        super().__init__(detalle)


# Alias de compatibilidad
ErrorSintaxisER = ErrorSintacticoER


def expandir_macros_er(expresion: str, macros: Optional[Dict[str, str]] = None) -> str:
    """
    Expande abreviaturas / clases de símbolos definidas por el usuario
    (por ejemplo: D = 0+1+2+3+4+5+6+7+8+9) respetando caracteres escapados con '\\'.
    """
    if not macros:
        return expresion

    salida = []
    i = 0
    n = len(expresion)
    while i < n:
        ch = expresion[i]
        if ch == "\\" and i + 1 < n:
            salida.append(expresion[i:i + 2])
            i += 2
            continue
        if ch in macros:
            salida.append(f"({macros[ch]})")
        else:
            salida.append(ch)
        i += 1
    return "".join(salida)


class ParserExpresionRegular:
    """
    Gramática formal (precedencia: * > concatenación > +):
      E    -> T ('+' T)*          (Unión)
      T    -> F (F)*              (Concatenación implícita)
      F    -> Atom ('*')*         (Cerradura de Kleene)
      Atom -> Simbolo | '\\' char | 'λ' | '∅' | '(' E ')'
    """

    OPERADORES_NO_SOPORTADOS = {"|", "?", "[", "]", "{", "}", "^", "$"}

    def __init__(self, expresion: str, macros: Optional[Dict[str, str]] = None):
        self.expresion_original: str = expresion
        self.texto: str = expandir_macros_er(expresion, macros)
        self.pos: int = 0
        self.longitud: int = len(self.texto)
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
        raise ErrorSintacticoER("Fin inesperado de la expresión.", self.pos, self.texto)

    def parsear(self) -> NodoAST:
        """Punto de entrada principal. Retorna la raíz del AST o lanza ErrorSintacticoER."""
        if not self.texto or not self.texto.strip():
            raise ErrorSintacticoER(
                "La expresión regular no puede estar vacía (usa 'λ' para la palabra vacía).",
                0,
                self.texto,
            )

        self.pos = 0
        ast = self._parse_union()
        sobrante = self._mirar()
        if sobrante is not None:
            if sobrante == ")":
                raise ErrorSintacticoER(
                    "Paréntesis de cierre ')' sin apertura correspondiente.",
                    self.pos,
                    self.texto,
                )
            raise ErrorSintacticoER(
                f"Carácter inesperado '{sobrante}'.",
                self.pos,
                self.texto,
            )
        return ast

    def _parse_union(self) -> NodoAST:
        izq = self._parse_concatenacion()
        while self._mirar() == "+":
            pos_op = self.pos
            self._consumir()  # consumir '+'
            siguiente = self._mirar()
            if siguiente is None or siguiente in ("+", ")"):
                raise ErrorSintacticoER(
                    "Falta el operando derecho después del operador de unión '+'.",
                    pos_op,
                    self.texto,
                )
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
            raise ErrorSintacticoER(
                "Se esperaba un operando antes del operador o fin de bloque.",
                self.pos,
                self.texto,
            )

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
            raise ErrorSintacticoER(
                "Se esperaba un símbolo u operando al final de la expresión.",
                self.pos,
                self.texto,
            )

        if ch == "(":
            pos_par = self.pos
            self._consumir()  # '('
            if self._mirar() == ")":
                raise ErrorSintacticoER(
                    "Paréntesis vacíos '()' no permitidos; usa 'λ' para la palabra vacía.",
                    pos_par,
                    self.texto,
                )
            sub_expr = self._parse_union()
            if self._mirar() != ")":
                raise ErrorSintacticoER(
                    f"Paréntesis abierto en posición {pos_par} sin cerrar.",
                    self.pos,
                    self.texto,
                )
            self._consumir()  # ')'
            return sub_expr

        if ch == "\\":
            pos_esc = self.pos
            self.pos += 1  # consumir '\' sin saltar espacios siguientes
            if self.pos >= self.longitud:
                raise ErrorSintacticoER(
                    "Barra invertida '\\' sin carácter escapado al final de la expresión.",
                    pos_esc,
                    self.texto,
                )
            literal = self.texto[self.pos]
            self.pos += 1
            self.alfabeto_detectado.add(literal)
            return NodoSimbolo(simbolo=literal)

        if ch in ("λ", "ε"):
            self._consumir()
            return NodoLambda()

        if ch in ("∅", "Ø"):
            self._consumir()
            return NodoVacio()

        if ch in ("+", "*", ")"):
            raise ErrorSintacticoER(
                f"Operador o delimitador '{ch}' en posición inválida.",
                self.pos,
                self.texto,
            )

        if ch in self.OPERADORES_NO_SOPORTADOS:
            raise ErrorSintacticoER(
                f"Símbolo '{ch}' no pertenece a la notación del curso (usa '+' para unión o '\\{ch}' como literal).",
                self.pos,
                self.texto,
            )

        simb = self._consumir()
        self.alfabeto_detectado.add(simb)
        return NodoSimbolo(simbolo=simb)