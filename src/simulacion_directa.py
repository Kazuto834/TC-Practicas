"""
Módulo de Simulación Directa Paso a Paso para AFN y AFN-lambda.

Ejercicio 2.1: Extensión del software interactivo.
Simula un AFN-lambda directamente, sin convertirlo a AFD: en cada paso muestra
el conjunto de estados activos antes y después de aplicar la cerradura lambda.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional, Any
from automata import Automata


def simular_afn_lambda_directo(
    auto: Automata,
    cadena: str
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Ejecuta la simulacion formal directa de un AFND o AFND-lambda sin transformarlo a AFD.

    Axioma formal (Hopcroft et al., 2007; Linz, 2016):
        Activos_0 = lambda-cl({q0})
        Para cada simbolo a_i:
            Directos_i = Union_{q in Activos_{i-1}} delta(q, a_i)
            Activos_i = lambda-cl(Directos_i)
        Aceptacion: Activos_{|w|} cap F != vacio

    Parametros:
        auto: Instancia de Automata configurado.
        cadena: Palabra a evaluar w in Sigma*.

    Retorna:
        (aceptada: bool, traza_detallada: List[Dict[str, Any]])
    """
    traza: List[Dict[str, Any]] = []

    if not auto.estado_inicial:
        return False, [{"paso": 0, "error": "El autómata no posee estado inicial definido."}]

    # Paso 0: Conjunto inicial antes y despues de cerradura lambda
    inicial_puro: Set[str] = {auto.estado_inicial}
    activos_actuales: Set[str] = auto.clausura_lambda(inicial_puro)
    es_aceptacion_paso0 = any(q in auto.estados_aceptacion for q in activos_actuales)

    traza.append({
        "paso": 0,
        "simbolo_leido": None,
        "estados_antes_cerradura": sorted(list(inicial_puro)),
        "estados_despues_cerradura": sorted(list(activos_actuales)),
        "transiciones_tomadas": [],
        "es_aceptacion": es_aceptacion_paso0,
        "descripcion": (
            f"Configuración inicial: Estado base '{auto.estado_inicial}'. "
            f"Antes de λ-cl: {{{', '.join(sorted(inicial_puro))}}}, "
            f"después de λ-cl: {{{', '.join(sorted(activos_actuales))}}}."
        )
    })

    if not cadena:
        # Cadena vacia
        return es_aceptacion_paso0, traza

    for i, char in enumerate(cadena, start=1):
        if char not in auto.alfabeto:
            traza.append({
                "paso": i,
                "simbolo_leido": char,
                "error": f"El símbolo '{char}' no pertenece al alfabeto {sorted(list(auto.alfabeto))}.",
                "estados_antes_cerradura": sorted(list(activos_actuales)),
                "estados_despues_cerradura": [],
                "transiciones_tomadas": [],
                "es_aceptacion": False,
                "descripcion": f"Rechazo: Símbolo '{char}' ajeno al alfabeto."
            })
            return False, traza

        # Buscar transiciones activas con el simbolo actual
        destinos_directos: Set[str] = set()
        transiciones_usadas: List[Dict[str, str]] = []

        for t in auto.transiciones:
            if t.origen in activos_actuales and t.simbolo == char:
                destinos_directos.add(t.destino)
                transiciones_usadas.append({
                    "origen": t.origen,
                    "simbolo": t.simbolo,
                    "destino": t.destino
                })

        # Aplicar cerradura lambda a los destinos directos
        activos_siguientes = auto.clausura_lambda(destinos_directos)
        es_aceptacion_paso = any(q in auto.estados_aceptacion for q in activos_siguientes)

        paso_dict = {
            "paso": i,
            "simbolo_leido": char,
            "estados_antes_transicion": sorted(list(activos_actuales)),
            "transiciones_tomadas": transiciones_usadas,
            "estados_antes_cerradura": sorted(list(destinos_directos)),
            "estados_despues_cerradura": sorted(list(activos_siguientes)),
            "es_aceptacion": es_aceptacion_paso,
            "descripcion": (
                f"Paso {i} (lee '{char}'): Activos previos={sorted(list(activos_actuales))}. "
                f"Destinos directos (antes de λ-cl)={sorted(list(destinos_directos))}. "
                f"Activos resultantes (después de λ-cl)={sorted(list(activos_siguientes))}."
            )
        }
        traza.append(paso_dict)

        activos_actuales = activos_siguientes

        if not activos_actuales:
            # Bloqueo total (sumidero sin salida)
            traza.append({
                "paso": i + 1,
                "simbolo_leido": None,
                "error": "Bloqueo: No existen transiciones válidas activas (conjunto vacío).",
                "estados_antes_cerradura": [],
                "estados_despues_cerradura": [],
                "es_aceptacion": False,
                "descripcion": "El autómata se bloquea por falta de caminos de transición."
            })
            return False, traza

    aceptada = any(q in auto.estados_aceptacion for q in activos_actuales)
    return aceptada, traza

