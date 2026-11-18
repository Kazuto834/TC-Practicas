"""
Módulo de Eliminación de Estados Inaccesibles en Autómatas Finitos.

Ejercicio 2.4: Extensión del software interactivo.
Elimina los estados no alcanzables desde el estado inicial q0 mediante
recorrido en anchura (BFS) del grafo de transiciones.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
from collections import deque
from automata import Automata


def eliminar_estados_inaccesibles(auto: Automata) -> Automata:
    """
    Elimina todos los estados de Q que no pueden ser alcanzados mediante ninguna
    secuencia de transiciones a partir del estado inicial q0.

    Retorna:
        Instancia de Automata depurado sin estados inaccesibles.
    """
    auto_depurado, _ = eliminar_estados_inaccesibles_detallado(auto)
    return auto_depurado


def eliminar_estados_inaccesibles_detallado(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Versión detallada que retorna el autómata depurado y un informe
    con los estados accesibles e inaccesibles identificados.
    """
    if not auto.estado_inicial:
        return auto, {
            "estados_alcanzables": [],
            "estados_inaccesibles": sorted(list(auto.estados)),
            "total_eliminados": len(auto.estados)
        }

    alcanzables: Set[str] = {auto.estado_inicial}
    cola = deque([auto.estado_inicial])
    tabla = auto.obtener_tabla_transiciones()

    while cola:
        actual = cola.popleft()
        for simb, dests in tabla.get(actual, {}).items():
            for d in dests:
                if d not in alcanzables:
                    alcanzables.add(d)
                    cola.append(d)

    inaccesibles = auto.estados - alcanzables

    # Construir nuevo automata con solo estados alcanzables
    auto_depurado = Automata(
        alfabeto=set(auto.alfabeto),
        estado_inicial=auto.estado_inicial,
        tipo=auto.tipo
    )

    for q in alcanzables:
        meta = auto.metadatos_estados.get(q)
        pos_x = meta.pos_x if meta else 100.0
        pos_y = meta.pos_y if meta else 100.0
        auto_depurado.agregar_estado(
            nombre=q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in auto.estados_aceptacion),
            pos_x=pos_x,
            pos_y=pos_y
        )

    for t in auto.transiciones:
        if t.origen in alcanzables and t.destino in alcanzables:
            auto_depurado.agregar_transicion(t.origen, t.simbolo, t.destino)

    auto_depurado._actualizar_tipo()

    reporte = {
        "estados_originales": sorted(list(auto.estados)),
        "estados_alcanzables": sorted(list(alcanzables)),
        "estados_inaccesibles": sorted(list(inaccesibles)),
        "total_eliminados": len(inaccesibles)
    }

    setattr(auto_depurado, "reporte_inaccesibles", reporte)
    return auto_depurado, reporte

