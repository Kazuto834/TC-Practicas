"""
Módulo de Eliminación de Transiciones Lambda en Autómatas Finitos.

Ejercicio 2.2: Extensión del software interactivo.
Transforma un AFN-lambda en un AFN sin transiciones lambda que reconoce el mismo lenguaje,
mostrando las transiciones que se añaden y los estados que pasan a ser de aceptación.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
from automata import Automata, Transicion


def eliminar_transiciones_lambda(auto: Automata) -> Automata:
    """
    Transforma un AFND-lambda en un AFN equivalente sin transiciones vacías (lambda).

    Axiomas formales (Hopcroft, Motwani, & Ullman, 2007, Secc. 2.5.5; Linz, 2016, Teorema 2.2):
        1. F' = { q in Q | lambda-cl(q) cap F != vacio }
        2. delta'(q, a) = lambda-cl( delta( lambda-cl(q), a ) ),  para todo q in Q, a in Sigma
        3. q0' = q0

    Retorna:
        Instancia de Automata equivalente sin transiciones lambda,
        con el atributo `reporte_eliminacion` conteniendo la bitácora paso a paso.
    """
    resultado, _ = transformar_afn_sin_lambda_detallado(auto)
    return resultado


def transformar_afn_sin_lambda_detallado(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Versión extendida que retorna el autómata transformado y un diccionario
    con la bitácora exhaustiva de estados promovidos a aceptación y transiciones añadidas.
    """
    # Alfabeto estricto sin simbolos lambda
    alfabeto_puro = {s for s in auto.alfabeto if s != "" and s.lower() not in ("lambda", "epsilon", "λ", "ε")}

    # 1. Identificar estados que pasan a ser de aceptación
    nuevos_finales: Set[str] = set()
    estados_promovidos: List[Dict[str, Any]] = []

    for q in sorted(list(auto.estados)):
        clausura_q = auto.clausura_lambda({q})
        finales_en_clausura = clausura_q.intersection(auto.estados_aceptacion)
        if finales_en_clausura:
            nuevos_finales.add(q)
            if q not in auto.estados_aceptacion:
                estados_promovidos.append({
                    "estado": q,
                    "razon": (
                        f"El estado '{q}' pasa a ser de aceptación porque su cerradura λ "
                        f"contiene al menos un estado final original: {sorted(list(finales_en_clausura))}."
                    ),
                    "finales_alcanzados": sorted(list(finales_en_clausura)),
                    "cerradura_lambda": sorted(list(clausura_q))
                })

    # Crear el nuevo automata sin lambda
    afn_sin_lambda = Automata(
        alfabeto=alfabeto_puro,
        estado_inicial=auto.estado_inicial,
        estados_aceptacion=nuevos_finales,
        tipo="AFND"
    )

    # Copiar estados y metadatos de posicion
    for q in auto.estados:
        meta = auto.metadatos_estados.get(q)
        pos_x = meta.pos_x if meta else 100.0
        pos_y = meta.pos_y if meta else 100.0
        afn_sin_lambda.agregar_estado(
            nombre=q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in nuevos_finales),
            pos_x=pos_x,
            pos_y=pos_y
        )

    # 2. Identificar transiciones existentes no-lambda originales
    trans_originales_no_lambda: Set[Tuple[str, str, str]] = set()
    for t in auto.transiciones:
        if not t.es_lambda():
            trans_originales_no_lambda.add((t.origen, t.simbolo, t.destino))

    # 3. Construir nuevas transiciones delta'(q, a) = lambda-cl( delta( lambda-cl(q), a ) )
    transiciones_anadidas: List[Dict[str, Any]] = []

    for q in sorted(list(auto.estados)):
        clausura_q = auto.clausura_lambda({q})
        for a in sorted(list(alfabeto_puro)):
            directos = auto.mover(clausura_q, a)
            destinos_finales = auto.clausura_lambda(directos)

            for dest in sorted(list(destinos_finales)):
                afn_sin_lambda.agregar_transicion(q, a, dest)
                if (q, a, dest) not in trans_originales_no_lambda:
                    transiciones_anadidas.append({
                        "origen": q,
                        "simbolo": a,
                        "destino": dest,
                        "razon": (
                            f"Añadida porque desde '{q}' con λ-cl={sorted(list(clausura_q))} "
                            f"se transita con '{a}' a {sorted(list(directos))} "
                            f"cuya λ-cl incluye a '{dest}'."
                        )
                    })

    afn_sin_lambda._actualizar_tipo()

    reporte = {
        "estados_totales": len(afn_sin_lambda.estados),
        "finales_originales": sorted(list(auto.estados_aceptacion)),
        "finales_resultantes": sorted(list(nuevos_finales)),
        "estados_promovidos": estados_promovidos,
        "total_estados_promovidos": len(estados_promovidos),
        "transiciones_anadidas": transiciones_anadidas,
        "total_transiciones_anadidas": len(transiciones_anadidas)
    }

    setattr(afn_sin_lambda, "reporte_eliminacion", reporte)
    return afn_sin_lambda, reporte

