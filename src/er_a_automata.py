"""
Módulo de Conversión de Expresión Regular a Autómata (Teorema de Kleene - Parte I).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Compilación inductiva de Thompson (ER -> AFND-lambda) con registro
                paso a paso de autómatas parciales y canalización completa hasta
                AFD mínimo (Práctica 3) y exportación a .jff.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from automata import Automata
from formatos import FormatosAutomata
from parser_er import (
    ParserExpresionRegular,
    ErrorSintacticoER,
    ErrorSintaxisER,
    NodoAST,
    NodoVacio,
    NodoLambda,
    NodoSimbolo,
    NodoUnion,
    NodoConcatenacion,
    NodoEstrella,
)
from eliminacion_lambda import eliminar_transiciones_lambda
from construccion_subconjuntos import construccion_subconjuntos
from eliminacion_inaccesibles import eliminar_estados_inaccesibles

try:
    from minimizacion import minimizar_afd
except ImportError:
    from minimizacion_afd import minimizar_afd


class CompiladorThompson:
    """Implementa la construcción inductiva de Thompson registrando cada autómata parcial."""

    def __init__(self):
        self._contador_estados: int = 0
        self.pasos_parciales: List[Dict[str, Any]] = []

    def _nuevo_estado(self) -> str:
        nombre = f"q{self._contador_estados}"
        self._contador_estados += 1
        return nombre

    def _clonar_parcial(self, auto: Automata, ini: str, fin: str) -> Automata:
        """Crea una copia limpia del autómata parcial marcando su inicio y aceptación."""
        copia = Automata(
            alfabeto=set(auto.alfabeto),
            estado_inicial=ini,
        )
        for q in auto.estados:
            copia.agregar_estado(
                q,
                es_inicial=(q == ini),
                es_final=(q == fin),
            )
        for t in auto.transiciones:
            copia.agregar_transicion(t.origen, t.simbolo, t.destino)
        copia._actualizar_tipo()
        return copia

    def _registrar_paso(
        self,
        operacion: str,
        subexpresion: str,
        descripcion: str,
        auto: Automata,
        ini: str,
        fin: str,
    ) -> None:
        self.pasos_parciales.append({
            "paso": len(self.pasos_parciales) + 1,
            "operacion": operacion,
            "subexpresion": subexpresion,
            "descripcion": descripcion,
            "automata": self._clonar_parcial(auto, ini, fin),
        })

    def construir(self, ast: NodoAST) -> Automata:
        """Construye el AFND-lambda completo a partir del AST de la expresión regular."""
        self.pasos_parciales = []
        ini, fin, auto, _ = self._construir_recursivo(ast)
        auto.estado_inicial = ini
        auto.estados_aceptacion = {fin}
        auto.metadatos_estados[ini].es_inicial = True
        auto.metadatos_estados[fin].es_final = True
        auto._actualizar_tipo()
        return auto

    def _construir_recursivo(self, nodo: NodoAST) -> Tuple[str, str, Automata, str]:
        if isinstance(nodo, NodoVacio):
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            self._registrar_paso(
                "Caso Base (∅)",
                "∅",
                f"Lenguaje vacío ∅: estados {ini} (inicio) y {fin} (aceptación) sin transición.",
                auto,
                ini,
                fin,
            )
            return ini, fin, auto, "∅"

        elif isinstance(nodo, NodoLambda):
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            auto.agregar_transicion(ini, "", fin)
            self._registrar_paso(
                "Caso Base (λ)",
                "λ",
                f"Palabra vacía λ: transición {ini} --λ--> {fin}.",
                auto,
                ini,
                fin,
            )
            return ini, fin, auto, "λ"

        elif isinstance(nodo, NodoSimbolo):
            ini = self._nuevo_estado()
            fin = self._nuevo_estado()
            auto = Automata()
            auto.agregar_simbolo(nodo.simbolo)
            auto.agregar_estado(ini)
            auto.agregar_estado(fin)
            auto.agregar_transicion(ini, nodo.simbolo, fin)
            self._registrar_paso(
                "Caso Base (Símbolo)",
                nodo.simbolo,
                f"Símbolo '{nodo.simbolo}': transición {ini} --{nodo.simbolo}--> {fin}.",
                auto,
                ini,
                fin,
            )
            return ini, fin, auto, nodo.simbolo

        elif isinstance(nodo, NodoUnion):
            ini1, fin1, auto1, e1 = self._construir_recursivo(nodo.izq)
            ini2, fin2, auto2, e2 = self._construir_recursivo(nodo.der)

            nuevo_ini = self._nuevo_estado()
            nuevo_fin = self._nuevo_estado()

            auto_union = Automata(
                alfabeto=auto1.alfabeto.union(auto2.alfabeto),
                estados=auto1.estados.union(auto2.estados),
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

            etq = f"({e1}+{e2})"
            self._registrar_paso(
                "Unión (+)",
                etq,
                f"Unión '{e1}' + '{e2}': {nuevo_ini} bifurca con λ a {ini1}, {ini2}; {fin1}, {fin2} convergen con λ a {nuevo_fin}.",
                auto_union,
                nuevo_ini,
                nuevo_fin,
            )
            return nuevo_ini, nuevo_fin, auto_union, etq

        elif isinstance(nodo, NodoConcatenacion):
            ini1, fin1, auto1, e1 = self._construir_recursivo(nodo.izq)
            ini2, fin2, auto2, e2 = self._construir_recursivo(nodo.der)

            auto_concat = Automata(
                alfabeto=auto1.alfabeto.union(auto2.alfabeto),
                estados=auto1.estados.union(auto2.estados),
            )
            auto_concat.transiciones.extend(auto1.transiciones)
            auto_concat.transiciones.extend(auto2.transiciones)
            auto_concat.metadatos_estados.update(auto1.metadatos_estados)
            auto_concat.metadatos_estados.update(auto2.metadatos_estados)

            auto_concat.agregar_transicion(fin1, "", ini2)

            etq = f"{e1}{e2}"
            self._registrar_paso(
                "Concatenación",
                etq,
                f"Concatenación '{e1}' seguido de '{e2}': enlace {fin1} --λ--> {ini2}.",
                auto_concat,
                ini1,
                fin2,
            )
            return ini1, fin2, auto_concat, etq

        elif isinstance(nodo, NodoEstrella):
            ini_sub, fin_sub, auto_sub, e1 = self._construir_recursivo(nodo.hijo)

            nuevo_ini = self._nuevo_estado()
            nuevo_fin = self._nuevo_estado()

            auto_estrella = Automata(
                alfabeto=set(auto_sub.alfabeto),
                estados=set(auto_sub.estados),
            )
            auto_estrella.transiciones.extend(auto_sub.transiciones)
            auto_estrella.metadatos_estados.update(auto_sub.metadatos_estados)

            auto_estrella.agregar_estado(nuevo_ini)
            auto_estrella.agregar_estado(nuevo_fin)

            auto_estrella.agregar_transicion(nuevo_ini, "", ini_sub)
            auto_estrella.agregar_transicion(nuevo_ini, "", nuevo_fin)
            auto_estrella.agregar_transicion(fin_sub, "", ini_sub)
            auto_estrella.agregar_transicion(fin_sub, "", nuevo_fin)

            etq = f"({e1})*"
            self._registrar_paso(
                "Cerradura de Kleene (*)",
                etq,
                f"Cerradura ({e1})*: atajo {nuevo_ini} --λ--> {nuevo_fin} y lazo de retorno {fin_sub} --λ--> {ini_sub}.",
                auto_estrella,
                nuevo_ini,
                nuevo_fin,
            )
            return nuevo_ini, nuevo_fin, auto_estrella, etq

        raise ValueError(f"Nodo AST desconocido: {type(nodo)}")


def _renombrar_estados_canonicos(auto: Automata, prefijo: str = "q") -> Automata:
    """Renombra estados compuestos '{q0, q1}' a nombres limpios s0, s1... o m0, m1..."""
    ordenados = sorted(list(auto.estados))
    if auto.estado_inicial in ordenados:
        ordenados.remove(auto.estado_inicial)
        ordenados.insert(0, auto.estado_inicial)

    mapa = {viejo: f"{prefijo}{i}" for i, viejo in enumerate(ordenados)}
    nuevo = Automata(
        alfabeto=set(auto.alfabeto),
        estado_inicial=mapa[auto.estado_inicial] if auto.estado_inicial else None,
        tipo=auto.tipo,
    )
    for viejo in ordenados:
        nuevo.agregar_estado(
            mapa[viejo],
            es_inicial=(viejo == auto.estado_inicial),
            es_final=(viejo in auto.estados_aceptacion),
        )
    for t in auto.transiciones:
        nuevo.agregar_transicion(mapa[t.origen], t.simbolo, mapa[t.destino])
    nuevo._actualizar_tipo()
    return nuevo


def er_a_afnd_lambda(
    expresion: str,
    macros: Optional[Dict[str, str]] = None,
) -> Automata:
    """Convierte una cadena de expresión regular en notación del curso a un AFND-lambda."""
    parser = ParserExpresionRegular(expresion, macros=macros)
    ast = parser.parsear()
    compilador = CompiladorThompson()
    return compilador.construir(ast)


def er_a_afd_minimo(
    expresion: str,
    macros: Optional[Dict[str, str]] = None,
) -> Automata:
    """
    Canalización completa de compilación:
      Expresión Regular -> Thompson (AFND-lambda) -> Eliminación λ -> Subconjuntos (AFD) -> Hopcroft (AFD mínimo)
    """
    return er_a_pipeline_completo(expresion, macros=macros)["afd_minimo"]


def er_a_pipeline_completo(
    expresion: str,
    macros: Optional[Dict[str, str]] = None,
    renombrar_afd: bool = True,
) -> Dict[str, Any]:
    """
    Ejecuta el flujo completo del Ejercicio 2:
      1. Análisis sintáctico de la ER (notación del curso).
      2. Construcción de Thompson -> AFN-λ con todos los autómatas parciales paso a paso.
      3. Eliminación de transiciones λ -> AFN sin λ (Práctica 3).
      4. Construcción de subconjuntos -> AFD (Práctica 3).
      5. Eliminación de inaccesibles y Minimización -> AFD mínimo (Práctica 3).
    """
    parser = ParserExpresionRegular(expresion, macros=macros)
    ast = parser.parsear()

    compilador = CompiladorThompson()
    afn_lambda = compilador.construir(ast)

    afn_sin_lambda = eliminar_transiciones_lambda(afn_lambda)
    afd_bruto = construccion_subconjuntos(afn_sin_lambda)
    afd_accesible = eliminar_estados_inaccesibles(afd_bruto)
    afd_minimo = minimizar_afd(afd_accesible)

    if renombrar_afd:
        afd_limpio = _renombrar_estados_canonicos(afd_accesible, "s")
        afd_min_limpio = _renombrar_estados_canonicos(afd_minimo, "m")
    else:
        afd_limpio = afd_accesible
        afd_min_limpio = afd_minimo

    return {
        "expresion_original": expresion,
        "expresion_expandida": parser.texto,
        "pasos_thompson": compilador.pasos_parciales,
        "afn_lambda": afn_lambda,
        "afn_sin_lambda": afn_sin_lambda,
        "afd": afd_limpio,
        "afd_minimo": afd_min_limpio,
        "estados_afd_antes_min": len(afd_accesible.estados),
        "estados_afd_despues_min": len(afd_min_limpio.estados),
    }


def exportar_automata_jff(auto: Automata) -> str:
    """Exporta un objeto Automata a XML estándar de JFLAP (.jff)."""
    return FormatosAutomata.serializar_jff(auto)

