"""
Módulo de Conversión de Expresión Regular a Autómata (Teorema de Kleene - Parte I).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Compilación inductiva de Thompson (ER -> AFND-lambda)
                y canalización automática a AFD mínimo (Hopcroft).
"""

from __future__ import annotations
from typing import Tuple, Set
from automata import Automata
from parser_er import (
    ParserExpresionRegular,
    NodoAST,
    NodoVacio,
    NodoLambda,
    NodoSimbolo,
    NodoUnion,
    NodoConcatenacion,
    NodoEstrella
)
from algoritmos_afn import (
    construccion_subconjuntos,
    transformar_afn_sin_lambda_detallado,
)
from minimizacion import minimizar_afd



class CompiladorThompson:
    """Implementa la construcción inductiva de Thompson para generar un AFND-lambda."""

    def __init__(self):
        self._contador_estados: int = 0

    def _nuevo_estado(self) -> str:
        nombre = f"q{self._contador_estados}"
        self._contador_estados += 1
        return nombre

    def construir(self, ast: NodoAST) -> Automata:
        """Construye el AFND-lambda a partir del AST de la expresión regular."""
        ini, fin, auto = self._construir_recursivo(ast)
        auto.estado_inicial = ini
        auto.estados_aceptacion = {fin}
        auto.metadatos_estados[ini].es_inicial = True
        auto.metadatos_estados[fin].es_final = True
        auto._actualizar_tipo()
        return auto

    def _construir_recursivo(self, nodo: NodoAST) -> Tuple[str, str, Automata]:
        if isinstance(nodo, NodoVacio):
            # Lenguaje vacío: dos estados sin caminos entre ellos
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            return ini, fin, auto

        elif isinstance(nodo, NodoLambda):
            # Palabra vacía: transición lambda directa de ini a fin
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            auto.agregar_transicion(ini, "", fin)
            return ini, fin, auto

        elif isinstance(nodo, NodoSimbolo):
            # Símbolo atómico: transición con símbolo 'a'
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_simbolo(nodo.simbolo)
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            auto.agregar_transicion(ini, nodo.simbolo, fin)
            return ini, fin, auto

        elif isinstance(nodo, NodoUnion):
            # Unión R1 + R2: bifurcación lambda desde nuevo inicio hacia ambos, y unión en nuevo final
            ini1, fin1, auto1 = self._construir_recursivo(nodo.izq)
            ini2, fin2, auto2 = self._construir_recursivo(nodo.der)

            nuevo_ini = self._nuevo_estado()
            nuevo_fin = self._nuevo_estado()

            auto_union = Automata(
                alfabeto=auto1.alfabeto.union(auto2.alfabeto),
                estados=auto1.estados.union(auto2.estados)
            )
            auto_union.transiciones.extend(auto1.transiciones)
            auto_union.transiciones.extend(auto2.transiciones)
            auto_union.metadatos_estados.update(auto1.metadatos_estados)
            auto_union.metadatos_estados.update(auto2.metadatos_estados)

            auto_union.agregar_estado(nuevo_ini)
            auto_union.agregar_estado(nuevo_fin)

            auto_union.agregar_transicion(nuevo_ini, "", ini1)
            auto_union.agregar_transicion(nuevo_ini, "", ini2)
            auto_union.agregar_transicion(fin1, "", nuevo_fin)
            auto_union.agregar_transicion(fin2, "", nuevo_fin)

            return nuevo_ini, nuevo_fin, auto_union

        elif isinstance(nodo, NodoConcatenacion):
            # Concatenación R1 · R2: enlazar fin1 con ini2 mediante lambda
            ini1, fin1, auto1 = self._construir_recursivo(nodo.izq)
            ini2, fin2, auto2 = self._construir_recursivo(nodo.der)

            auto_concat = Automata(
                alfabeto=auto1.alfabeto.union(auto2.alfabeto),
                estados=auto1.estados.union(auto2.estados)
            )
            auto_concat.transiciones.extend(auto1.transiciones)
            auto_concat.transiciones.extend(auto2.transiciones)
            auto_concat.metadatos_estados.update(auto1.metadatos_estados)
            auto_concat.metadatos_estados.update(auto2.metadatos_estados)

            auto_concat.agregar_transicion(fin1, "", ini2)
            return ini1, fin2, auto_concat

        elif isinstance(nodo, NodoEstrella):
            # Cerradura de Kleene R*: nuevo inicio y final con atajo lambda y lazo de retorno
            ini_sub, fin_sub, auto_sub = self._construir_recursivo(nodo.hijo)

            nuevo_ini = self._nuevo_estado()
            nuevo_fin = self._nuevo_estado()

            auto_estrella = Automata(
                alfabeto=set(auto_sub.alfabeto),
                estados=set(auto_sub.estados)
            )
            auto_estrella.transiciones.extend(auto_sub.transiciones)
            auto_estrella.metadatos_estados.update(auto_sub.metadatos_estados)

            auto_estrella.agregar_estado(nuevo_ini)
            auto_estrella.agregar_estado(nuevo_fin)

            auto_estrella.agregar_transicion(nuevo_ini, "", ini_sub)
            auto_estrella.agregar_transicion(nuevo_ini, "", nuevo_fin)  # Atajo palabra vacía
            auto_estrella.agregar_transicion(fin_sub, "", ini_sub)     # Lazo de retorno
            auto_estrella.agregar_transicion(fin_sub, "", nuevo_fin)

            return nuevo_ini, nuevo_fin, auto_estrella

        raise ValueError(f"Nodo AST desconocido: {type(nodo)}")


def er_a_afnd_lambda(expresion: str) -> Automata:
    """Convierte una cadena de expresión regular en notación del curso a un AFND-lambda."""
    parser = ParserExpresionRegular(expresion)
    ast = parser.parsear()
    compilador = CompiladorThompson()
    return compilador.construir(ast)


def er_a_afd_minimo(expresion: str) -> Automata:
    """
    Canalización completa de compilación:
      Expresión Regular -> Thompson (AFND-lambda) -> Subconjuntos (AFD) -> Hopcroft (AFD mínimo)
    """
    afnd_lambda = er_a_afnd_lambda(expresion)
    afd_completo = construccion_subconjuntos(afnd_lambda)
    afd_min = minimizar_afd(afd_completo)
    return afd_min


# Alias para compatibilidad con suites de integración
er_a_automata = er_a_afnd_lambda


def er_a_pipeline_completo(expresion: str) -> dict:
    """
    Canalización completa de compilación (Ejercicio 2 - Práctica 4):
      Expresión Regular
        → AFND-λ (Construcción inductiva de Thompson)
        → AFN sin λ (Eliminación formal de transiciones λ)
        → AFD (Construcción de subconjuntos)
        → AFD Mínimo (Refinamiento de particiones)
    
    Retorna un diccionario con cada autómata intermedio listo para inspección o exportación .jff.
    """
    afnd_lambda = er_a_afnd_lambda(expresion)
    afn_sin_lambda, reporte_sin_lambda = transformar_afn_sin_lambda_detallado(afnd_lambda)
    afd_subconjuntos = construccion_subconjuntos(afn_sin_lambda)
    afd_minimo = minimizar_afd(afd_subconjuntos)

    return {
        "expresion": expresion,
        "afnd_lambda": afnd_lambda,
        "afn_sin_lambda": afn_sin_lambda,
        "reporte_sin_lambda": reporte_sin_lambda,
        "afd": afd_subconjuntos,
        "afd_minimo": afd_minimo,
        "estados_afnd_lambda": len(afnd_lambda.estados),
        "estados_afn_sin_lambda": len(afn_sin_lambda.estados),
        "estados_afd": len(afd_subconjuntos.estados),
        "estados_afd_minimo": len(afd_minimo.estados),
    }



