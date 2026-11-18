"""
Módulo de Cálculo de la Cerradura Lambda (Cerradura Épsilon).

Ejercicio 2.1: Extensión del software interactivo.
Calcula la cerradura lambda de cada estado y de un estado seleccionado por el usuario,
generando una traza detallada paso a paso del recorrido.
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any
from collections import deque
from automata import Automata


def calcular_cerradura_lambda(
    auto: Automata,
    estado: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calcula la cerradura lambda (lambda-clausura) formal de los estados de un automata.

    Axioma formal (Hopcroft et al., 2007; Linz, 2016):
        lambda-cl(q) = {q} U { p in Q | existe un camino de q a p compuesto exclusivamente por transiciones lambda }

    Parametros:
        auto: Instancia de Automata (puede ser AFND o AFND-lambda).
        estado: (Opcional) Si se especifica, calcula y detalla la cerradura de ese estado.
                Si es None, calcula la cerradura de todos los estados del automata.

    Retorna:
        Diccionario con la informacion paso a paso y el resultado final:
        - Si estado es individual:
            {
                "estado": str,
                "cerradura": List[str],
                "pasos": List[Dict[str, Any]],
                "resumen_texto": str
            }
        - Si estado es None:
            {
                "todas_cerraduras": Dict[str, List[str]],
                "detalles": Dict[str, Dict[str, Any]],
                "resumen_texto": str
            }
    """
    if estado is not None:
        if estado not in auto.estados:
            raise ValueError(f"El estado '{estado}' no pertenece al conjunto de estados del automata.")
        return _calcular_cerradura_individual(auto, estado)

    # Calcular para todos los estados
    todas: Dict[str, List[str]] = {}
    detalles: Dict[str, Dict[str, Any]] = {}
    lineas_resumen: List[str] = ["Cálculo de Cerradura λ para todos los estados:"]

    for q in sorted(list(auto.estados)):
        info = _calcular_cerradura_individual(auto, q)
        todas[q] = info["cerradura"]
        detalles[q] = info
        lineas_resumen.append(f"  λ-cl({q}) = {{{', '.join(info['cerradura'])}}}")

    return {
        "todas_cerraduras": todas,
        "detalles": detalles,
        "resumen_texto": "\n".join(lineas_resumen)
    }


def _calcular_cerradura_individual(auto: Automata, estado: str) -> Dict[str, Any]:
    """Calcula paso a paso la cerradura lambda de un estado especifico."""
    clausura: Set[str] = {estado}
    cola = deque([estado])
    pasos: List[Dict[str, Any]] = []

    # Mapa de transiciones lambda: origen -> set de destinos
    trans_lambda: Dict[str, Set[str]] = {q: set() for q in auto.estados}
    for t in auto.transiciones:
        if t.es_lambda():
            if t.origen not in trans_lambda:
                trans_lambda[t.origen] = set()
            trans_lambda[t.origen].add(t.destino)

    paso_num = 0
    pasos.append({
        "paso": paso_num,
        "accion": "Inicializacion",
        "estado_actual": estado,
        "nuevos_alcanzados": [estado],
        "cerradura_parcial": sorted(list(clausura)),
        "descripcion": f"Se inicia con el estado base {{{estado}}}."
    })

    while cola:
        actual = cola.popleft()
        destinos = trans_lambda.get(actual, set())
        nuevos = [d for d in destinos if d not in clausura]

        paso_num += 1
        for n in nuevos:
            clausura.add(n)
            cola.append(n)

        pasos.append({
            "paso": paso_num,
            "accion": "Expansion por transiciones lambda",
            "estado_expandido": actual,
            "destinos_lambda": sorted(list(destinos)),
            "nuevos_agregados": sorted(nuevos),
            "cerradura_parcial": sorted(list(clausura)),
            "descripcion": (
                f"Desde '{actual}' mediante transiciones λ se alcanzan {sorted(list(destinos))}. "
                f"Nuevos incorporados: {sorted(nuevos)}."
            )
        })

    cerradura_ordenada = sorted(list(clausura))
    resumen = f"λ-cl({estado}) = {{{', '.join(cerradura_ordenada)}}}"

    return {
        "estado": estado,
        "cerradura": cerradura_ordenada,
        "pasos": pasos,
        "resumen_texto": resumen
    }

