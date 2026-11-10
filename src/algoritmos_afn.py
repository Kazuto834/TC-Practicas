"""
Módulo de Algoritmos Formales para Autómatas No Deterministas (Práctica 3).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Mario García Castillo (Kazuto834) & Antonio Navarro Domínguez (A7LAS-1)
Responsabilidad: Simulación directa con lambda-clausura, cálculo de clausuras lambda,
                eliminación formal de transiciones lambda y construcción de subconjuntos
                (AFN -> AFD) de subconjuntos alcanzables paso a paso.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import deque
from automata import Automata, Transicion


def calcular_clausura_lambda(auto: Automata, estado: str) -> Set[str]:
    """Calcula y retorna la lambda-clausura de un estado individual."""
    return auto.clausura_lambda({estado})


def calcular_todas_clausuras_lambda(auto: Automata) -> Dict[str, Set[str]]:
    """Calcula y retorna la lambda-clausura para cada uno de los estados del autómata."""
    return {q: auto.clausura_lambda({q}) for q in sorted(list(auto.estados))}


def simulacion_directa_paso_a_paso(auto: Automata, cadena: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Ejecuta la simulación directa de un AFND-lambda sin convertirlo a AFD.
    Muestra en cada paso el conjunto de estados activos antes y después de aplicar lambda-clausura.
    """
    return auto.simular_cadena(cadena)


def eliminar_transiciones_lambda_detallado(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Transforma un AFND-lambda en un AFN sin transiciones lambda que reconoce el mismo lenguaje,
    generando una bitácora detallada paso a paso de:
      - Lambda-clausura de cada estado.
      - Nuevos estados que pasan a ser de aceptación y la justificación.
      - Nuevas transiciones añadidas con origen, símbolo y destino.
      
    Axiomas formales (Hopcroft et al., 2007; Linz, 2016):
      delta'(q, a) = lambda-cl( delta( lambda-cl(q), a ) )
      F' = { q in Q | lambda-cl(q) cap F != vacio }
      q0' = q0
    """
    afn_sin_lambda = Automata(
        alfabeto=set(auto.alfabeto),
        estados=set(auto.estados),
        estado_inicial=auto.estado_inicial,
        tipo="AFND"
    )

    clausuras = calcular_todas_clausuras_lambda(auto)
    nuevos_finales: Set[str] = set()
    razones_finales: Dict[str, List[str]] = {}

    for q in sorted(list(auto.estados)):
        clausura_q = clausuras[q]
        inter = clausura_q.intersection(auto.estados_aceptacion)
        if inter:
            nuevos_finales.add(q)
            razones_finales[q] = sorted(list(inter))

    afn_sin_lambda.estados_aceptacion = nuevos_finales

    for q in sorted(list(auto.estados)):
        afn_sin_lambda.agregar_estado(
            nombre=q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in nuevos_finales)
        )

    transiciones_agregadas: List[Dict[str, Any]] = []

    for q in sorted(list(auto.estados)):
        clausura_q = clausuras[q]
        for a in sorted(list(auto.alfabeto)):
            destinos_directos = auto.mover(clausura_q, a)
            destinos_clausurados = auto.clausura_lambda(destinos_directos)
            for dest in sorted(list(destinos_clausurados)):
                afn_sin_lambda.agregar_transicion(q, a, dest)
                transiciones_agregadas.append({
                    "origen": q,
                    "simbolo": a,
                    "destino": dest,
                    "clausura_origen": sorted(list(clausura_q)),
                    "destinos_directos": sorted(list(destinos_directos)),
                    "destinos_clausurados": sorted(list(destinos_clausurados))
                })

    afn_sin_lambda._actualizar_tipo()

    bitacora = {
        "clausuras": {q: sorted(list(clausuras[q])) for q in clausuras},
        "estados_aceptacion_originales": sorted(list(auto.estados_aceptacion)),
        "estados_aceptacion_nuevos": sorted(list(nuevos_finales)),
        "razones_aceptacion": {
            q: f"La λ-clausura {sorted(list(clausuras[q]))} contiene estado(s) final(es): {razones_finales[q]}"
            for q in nuevos_finales
        },
        "total_transiciones_agregadas": len(transiciones_agregadas),
        "transiciones_agregadas": transiciones_agregadas
    }

    return afn_sin_lambda, bitacora


def eliminar_transiciones_lambda(auto: Automata) -> Automata:
    """Función de compatibilidad: retorna directamente el AFN sin transiciones lambda."""
    afn, _ = eliminar_transiciones_lambda_detallado(auto)
    return afn


def construccion_subconjuntos_detallada(auto: Automata) -> Tuple[Automata, List[Dict[str, Any]]]:
    """
    Transforma un AFN (o AFN-lambda) en un AFD determinista equivalente.
    Construye exclusivamente los subconjuntos alcanzables a partir del estado inicial.
    Retorna el AFD resultante y la bitácora paso a paso de la generación de la tabla de transiciones,
    indicando qué subconjuntos resultan de aceptación y por qué.
    
    Axiomas formales:
      S0 = lambda-cl({q0})
      delta_D(S, a) = lambda-cl( Union_{p in S} delta(p, a) )
      F_D = { S subseteq Q | S cap F != vacio }
    """
    if not auto.estado_inicial:
        raise ValueError("El autómata original no posee estado inicial.")

    s0_set = auto.clausura_lambda({auto.estado_inicial})

    def nombre_subconjunto(conj: Set[str]) -> str:
        if not conj:
            return "∅"
        return "{" + ",".join(sorted(list(conj))) + "}"

    nombre_s0 = nombre_subconjunto(s0_set)

    afd = Automata(
        alfabeto=set(auto.alfabeto),
        estado_inicial=nombre_s0,
        tipo="AFD"
    )

    es_final_s0 = any(f in auto.estados_aceptacion for f in s0_set)
    afd.agregar_estado(nombre_s0, es_inicial=True, es_final=es_final_s0)

    cola = deque([(nombre_s0, s0_set)])
    visitados: Dict[str, Set[str]] = {nombre_s0: s0_set}
    tabla_pasos: List[Dict[str, Any]] = []

    paso_idx = 1
    while cola:
        nombre_actual, set_actual = cola.popleft()
        finales_en_subconjunto = sorted(list(set_actual.intersection(auto.estados_aceptacion)))
        es_final_actual = bool(finales_en_subconjunto)

        fila_transiciones: Dict[str, str] = {}
        descubiertos_este_paso: List[str] = []

        for a in sorted(list(auto.alfabeto)):
            destinos_directos = auto.mover(set_actual, a)
            destinos_clausurados = auto.clausura_lambda(destinos_directos)
            nombre_destino = nombre_subconjunto(destinos_clausurados)
            fila_transiciones[a] = nombre_destino

            if nombre_destino not in visitados:
                visitados[nombre_destino] = destinos_clausurados
                es_final_dest = any(f in auto.estados_aceptacion for f in destinos_clausurados)
                afd.agregar_estado(nombre_destino, es_inicial=False, es_final=es_final_dest)
                cola.append((nombre_destino, destinos_clausurados))
                descubiertos_este_paso.append(nombre_destino)

            afd.agregar_transicion(nombre_actual, a, nombre_destino)

        tabla_pasos.append({
            "paso": paso_idx,
            "subconjunto": nombre_actual,
            "estados_individuales": sorted(list(set_actual)),
            "es_final": es_final_actual,
            "razon_aceptacion": (
                f"Contiene estado(s) final(es) de aceptación: {finales_en_subconjunto}"
                if es_final_actual else "No contiene ningún estado de aceptación original."
            ),
            "transiciones": fila_transiciones,
            "nuevos_subconjuntos_descubiertos": descubiertos_este_paso
        })
        paso_idx += 1

    afd._actualizar_tipo()
    return afd, tabla_pasos


def construccion_subconjuntos(auto: Automata) -> Automata:
    """Función de compatibilidad: retorna directamente el AFD determinista por subconjuntos."""
    afd, _ = construccion_subconjuntos_detallada(auto)
    return afd
