"""
Módulo de Algoritmos Formales para Autómatas No Deterministas (Práctica 3).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Simulación directa con lambda-clausura, eliminación de transiciones lambda
                y construcción de subconjuntos (AFN -> AFD) de subconjuntos alcanzables.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
from collections import deque
from automata import Automata, Transicion


def simulacion_directa_paso_a_paso(auto: Automata, cadena: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Ejecuta la simulación directa de un AFND-lambda sin convertirlo a AFD.
    Muestra en cada paso el conjunto de estados activos antes y después de aplicar lambda-clausura.
    """
    return auto.simular_cadena(cadena)


def eliminar_transiciones_lambda(auto: Automata) -> Automata:
    """
    Transforma un AFND-lambda en un AFN sin transiciones lambda que reconoce el mismo lenguaje.
    
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

    # 1. Determinar nuevos estados de aceptación F'
    nuevos_finales: Set[str] = set()
    for q in auto.estados:
        clausura_q = auto.clausura_lambda({q})
        if any(f in auto.estados_aceptacion for f in clausura_q):
            nuevos_finales.add(q)
    afn_sin_lambda.estados_aceptacion = nuevos_finales

    # 2. Registrar estados en el nuevo autómata con metadatos
    for q in auto.estados:
        afn_sin_lambda.agregar_estado(
            nombre=q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in nuevos_finales)
        )

    # 3. Calcular nuevas transiciones delta'(q, a) para cada a in Sigma
    for q in auto.estados:
        clausura_q = auto.clausura_lambda({q})
        for a in auto.alfabeto:
            # delta(lambda-cl(q), a)
            destinos_directos = auto.mover(clausura_q, a)
            # lambda-cl( destinos_directos )
            destinos_clausurados = auto.clausura_lambda(destinos_directos)
            for dest in destinos_clausurados:
                afn_sin_lambda.agregar_transicion(q, a, dest)

    afn_sin_lambda._actualizar_tipo()
    return afn_sin_lambda


def construccion_subconjuntos(auto: Automata) -> Automata:
    """
    Transforma un AFN (o AFN-lambda) en un AFD determinista equivalente.
    Construye exclusivamente los subconjuntos alcanzables a partir del estado inicial.
    
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

    # Cola de subconjuntos por explorar: (nombre_str, set_de_estados)
    cola = deque([(nombre_s0, s0_set)])
    visitados: Dict[str, Set[str]] = {nombre_s0: s0_set}

    while cola:
        nombre_actual, set_actual = cola.popleft()

        for a in sorted(list(auto.alfabeto)):
            # Mover y clausurar
            destinos_directos = auto.mover(set_actual, a)
            destinos_clausurados = auto.clausura_lambda(destinos_directos)
            nombre_destino = nombre_subconjunto(destinos_clausurados)

            if nombre_destino not in visitados:
                visitados[nombre_destino] = destinos_clausurados
                es_final = any(f in auto.estados_aceptacion for f in destinos_clausurados)
                afd.agregar_estado(nombre_destino, es_inicial=False, es_final=es_final)
                cola.append((nombre_destino, destinos_clausurados))

            afd.agregar_transicion(nombre_actual, a, nombre_destino)

    afd._actualizar_tipo()
    return afd

