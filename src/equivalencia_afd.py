"""
Módulo de Decisión de Equivalencia entre Autómatas Finitos Deterministas.

Ejercicio 2.4: Extensión del software interactivo.
Decide si dos AFD son equivalentes mediante la minimización y comprobación de
isomorfismo estructural (coincidencia salvo el nombre de los estados).
"""

from __future__ import annotations
import itertools
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque
from automata import Automata
from minimizacion_afd import minimizar_afd


def son_equivalentes(
    afd1: Automata,
    afd2: Automata,
    limite_longitud: int = 6
) -> Tuple[bool, str]:
    """
    Decide si dos AFD reconocen exactamente el mismo lenguaje.
    Comprueba si sus autómatas mínimos coinciden salvo el nombre de los estados (isomorfismo).

    Axioma formal (Teorema de Myhill-Nerode; Hopcroft, Motwani, & Ullman, 2007, Secc. 4.4):
        El AFD mínimo que reconoce un lenguaje regular L es único salvo isomorfismo
        (renombramiento biyectivo de estados que preserva q0, F y delta).

    Retorna:
        (equivalentes: bool, razon_o_detalle: str)
    """
    es_equiv, mensaje, _ = decidir_equivalencia_detallada(afd1, afd2, limite_longitud=limite_longitud)
    return es_equiv, mensaje


def decidir_equivalencia_detallada(
    afd1: Automata,
    afd2: Automata,
    limite_longitud: int = 6
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Versión extendida con informe detallado del isomorfismo o contraejemplo explicativo.
    """
    # 1. Verificar compatibilidad de alfabetos
    alfabeto1 = {s for s in afd1.alfabeto if s != ""}
    alfabeto2 = {s for s in afd2.alfabeto if s != ""}
    if alfabeto1 != alfabeto2:
        msg = f"Los alfabetos difieren: {sorted(list(alfabeto1))} vs {sorted(list(alfabeto2))}."
        return False, msg, {"error": "alfabetos_distintos"}

    # 2. Minimizar ambos autómatas
    min1 = minimizar_afd(afd1)
    min2 = minimizar_afd(afd2)

    if len(min1.estados) != len(min2.estados):
        msg = (
            f"No son equivalentes: Sus autómatas mínimos tienen diferente número de estados "
            f"({len(min1.estados)} vs {len(min2.estados)})."
        )
        contraejemplo = _buscar_contraejemplo(afd1, afd2, alfabeto1, limite_longitud)
        return False, f"{msg} Contraejemplo: '{contraejemplo}'." if contraejemplo is not None else msg, {
            "estados_min1": len(min1.estados),
            "estados_min2": len(min2.estados),
            "contraejemplo": contraejemplo
        }

    # 3. Comprobar isomorfismo entre min1 y min2 partiendo de sus estados iniciales
    if not min1.estado_inicial or not min2.estado_inicial:
        return False, "Uno de los autómatas mínimos carece de estado inicial.", {}

    mapeo_1_a_2: Dict[str, str] = {min1.estado_inicial: min2.estado_inicial}
    mapeo_2_a_1: Dict[str, str] = {min2.estado_inicial: min1.estado_inicial}

    # Si los estados iniciales difieren en condición de aceptación, no son equivalentes
    ini1_es_final = min1.estado_inicial in min1.estados_aceptacion
    ini2_es_final = min2.estado_inicial in min2.estados_aceptacion
    if ini1_es_final != ini2_es_final:
        msg = "No son equivalentes: La palabra vacía λ es aceptada por uno y rechazada por el otro."
        return False, msg, {"contraejemplo": ""}

    cola = deque([(min1.estado_inicial, min2.estado_inicial)])
    tabla1 = min1.obtener_tabla_transiciones()
    tabla2 = min2.obtener_tabla_transiciones()
    alfabeto_ordenado = sorted(list(alfabeto1))

    while cola:
        q1, q2 = cola.popleft()

        for a in alfabeto_ordenado:
            dest1_set = tabla1.get(q1, {}).get(a, set())
            dest2_set = tabla2.get(q2, {}).get(a, set())

            d1 = next(iter(dest1_set)) if dest1_set else None
            d2 = next(iter(dest2_set)) if dest2_set else None

            # Si uno tiene transición y el otro no
            if (d1 is None) != (d2 is None):
                contraejemplo = _buscar_contraejemplo(afd1, afd2, alfabeto1, limite_longitud)
                return False, f"Discrepancia en transición con símbolo '{a}'.", {"contraejemplo": contraejemplo}

            if d1 is not None and d2 is not None:
                # Comprobar si ya estaba mapeado
                if d1 in mapeo_1_a_2:
                    if mapeo_1_a_2[d1] != d2:
                        contraejemplo = _buscar_contraejemplo(afd1, afd2, alfabeto1, limite_longitud)
                        return False, f"Conflicto de isomorfismo en transición '{a}'.", {"contraejemplo": contraejemplo}
                elif d2 in mapeo_2_a_1:
                    if mapeo_2_a_1[d2] != d1:
                        contraejemplo = _buscar_contraejemplo(afd1, afd2, alfabeto1, limite_longitud)
                        return False, f"Conflicto de isomorfismo biyectivo en '{a}'.", {"contraejemplo": contraejemplo}
                else:
                    # Nuevo par de estados mapeados
                    d1_es_final = d1 in min1.estados_aceptacion
                    d2_es_final = d2 in min2.estados_aceptacion
                    if d1_es_final != d2_es_final:
                        contraejemplo = _buscar_contraejemplo(afd1, afd2, alfabeto1, limite_longitud)
                        return False, f"Inconsistencia de aceptación entre estados {d1} y {d2}.", {"contraejemplo": contraejemplo}

                    mapeo_1_a_2[d1] = d2
                    mapeo_2_a_1[d2] = d1
                    cola.append((d1, d2))

    detalles = {
        "isomorfismo": mapeo_1_a_2,
        "estados_minimos": len(min1.estados),
        "alfabeto": alfabeto_ordenado
    }
    return True, "Los autómatas son equivalentes: sus AFD mínimos coinciden formalmente salvo renombramiento de estados.", detalles


def _buscar_contraejemplo(afd1: Automata, afd2: Automata, alfabeto: Set[str], limite: int) -> Optional[str]:
    """Encuentra la palabra más corta en la que afd1 y afd2 difieren."""
    alf = sorted(list(alfabeto))
    for long in range(limite + 1):
        for combo in itertools.product(alf, repeat=long):
            palabra = "".join(combo)
            r1, _ = afd1.simular_cadena(palabra)
            r2, _ = afd2.simular_cadena(palabra)
            if r1 != r2:
                return palabra
    return None

