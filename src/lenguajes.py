"""
===============================================================================
MÓDULO DE OPERACIONES SOBRE CADENAS Y LENGUAJES FORMALES (PRÁCTICA 1 & 2)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación
Institución: Escuela Superior de Cómputo (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Provee las operaciones fundamentales sobre cadenas y alfabetos reutilizadas
    desde la Práctica 1 e integradas en la interfaz de la Práctica 2
    (conforme a la Sección 1 y Sección 3.4 de la especificación):
      - Prefijos de una cadena
      - Sufijos de una cadena
      - Subcadenas de una cadena
      - Cerradura de Kleene (Sigma*)
      - Cerradura Positiva (Sigma+)

Navegación del Módulo:
    1. Operaciones sobre Cadenas: prefijos, sufijos, subcadenas
    2. Cerraduras sobre Alfabetos: cerradura_Kleene, cerradura_positiva
===============================================================================
"""

from __future__ import annotations
import itertools
from typing import List, Set, Sequence, Union


# =============================================================================
# SECCIÓN 1: OPERACIONES SOBRE CADENAS FORMALES
# =============================================================================

def prefijos(cadena: str) -> List[str]:
    """
    Calcula el conjunto ordenado de prefijos de una cadena dada w.
    
    Definición formal:
        Pref(w) = { u in Sigma* | existe v in Sigma* tal que w = uv }
    
    Parámetros:
        cadena (str): Cadena de entrada w.
        
    Retorna:
        List[str]: Lista con todos los prefijos desde lambda (cadena vacía) hasta w.
    """
    return [cadena[:i] for i in range(len(cadena) + 1)]


def sufijos(cadena: str) -> List[str]:
    """
    Calcula el conjunto ordenado de sufijos de una cadena dada w.
    
    Definición formal:
        Suf(w) = { v in Sigma* | existe u in Sigma* tal que w = uv }
        
    Parámetros:
        cadena (str): Cadena de entrada w.
        
    Retorna:
        List[str]: Lista con todos los sufijos desde w hasta lambda (cadena vacía).
    """
    return [cadena[i:] for i in range(len(cadena) + 1)]


def subcadenas(cadena: str) -> List[str]:
    """
    Calcula todas las subcadenas posibles de una cadena dada w.
    
    Definición formal:
        Sub(w) = { v in Sigma* | existen u, x in Sigma* tales que w = uvx }
        
    Parámetros:
        cadena (str): Cadena de entrada w.
        
    Retorna:
        List[str]: Lista única de subcadenas, incluyendo la cadena vacía lambda.
    """
    conjunto_subcadenas: Set[str] = {""}

    longitud = len(cadena)
    for inicio in range(longitud):
        for fin in range(inicio + 1, longitud + 1):
            conjunto_subcadenas.add(cadena[inicio:fin])

    return list(conjunto_subcadenas)


# =============================================================================
# SECCIÓN 2: CERRADURAS SOBRE ALFABETOS FORMALES
# =============================================================================

def cerradura_Kleene(alfabeto: Union[Sequence[str], Set[str]], maxlength: int) -> List[str]:
    """
    Genera la cerradura estrella de Kleene de un alfabeto Sigma hasta una longitud n.
    
    Definición formal:
        Sigma* = Union_{i=0}^{maxlength} Sigma^i
        donde Sigma^0 = {lambda}
        
    Parámetros:
        alfabeto (Sequence[str] | Set[str]): Símbolos del alfabeto Sigma.
        maxlength (int): Longitud máxima de las combinaciones (longitud >= 0).
        
    Retorna:
        List[str]: Lista de palabras ordenadas crecientemente por longitud.
    """
    simbolos = list(alfabeto)
    resultado: List[str] = []

    for longitud in range(maxlength + 1):
        for combinacion in itertools.product(simbolos, repeat=longitud):
            resultado.append("".join(combinacion))

    return resultado


def cerradura_positiva(alfabeto: Union[Sequence[str], Set[str]], maxlength: int) -> List[str]:
    """
    Genera la cerradura positiva de un alfabeto Sigma hasta una longitud n.
    
    Definición formal:
        Sigma+ = Union_{i=1}^{maxlength} Sigma^i = Sigma* - {lambda}
        
    Parámetros:
        alfabeto (Sequence[str] | Set[str]): Símbolos del alfabeto Sigma.
        maxlength (int): Longitud máxima de las combinaciones (longitud >= 1).
        
    Retorna:
        List[str]: Lista de palabras generadas con longitud entre 1 y maxlength.
    """
    simbolos = list(alfabeto)
    resultado: List[str] = []

    for longitud in range(1, maxlength + 1):
        for combinacion in itertools.product(simbolos, repeat=longitud):
            resultado.append("".join(combinacion))

    return resultado
