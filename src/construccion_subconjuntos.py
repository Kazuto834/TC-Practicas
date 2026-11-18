"""
Módulo de Construcción de Subconjuntos (Conversión AFN / AFN-lambda -> AFD).

Ejercicio 2.3: Extensión del software interactivo.
Transforma un AFN en un AFD equivalente construyendo exclusivamente los subconjuntos
alcanzables desde el estado inicial, mostrando la tabla de transiciones conforme se genera
e indicando qué subconjuntos resultan de aceptación y por qué.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
from collections import deque
from automata import Automata


def formatear_nombre_subconjunto(conjunto: Set[str]) -> str:
    """Retorna una representación textual canónica de un subconjunto de estados."""
    if not conjunto:
        return "∅"
    return "{" + ", ".join(sorted(list(conjunto))) + "}"


def construccion_subconjuntos(auto: Automata) -> Automata:
    """
    Transforma un AFN (o AFN-lambda) en un AFD equivalente construyendo solo subconjuntos alcanzables.

    Axiomas formales (Rabin & Scott, 1959; Hopcroft et al., 2007, Secc. 2.3.5):
        1. S0 = lambda-cl({q0})
        2. delta_D(S, a) = lambda-cl( Union_{p in S} delta(p, a) )
        3. F_D = { S in Q_D | S cap F_N != vacio }

    Retorna:
        Instancia de Automata determinista (AFD) equivalente, con el atributo
        `reporte_subconjuntos` conteniendo la traza paso a paso.
    """
    afd, _ = construccion_subconjuntos_detallada(auto)
    return afd


def construccion_subconjuntos_detallada(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Transforma un AFN en un AFD y genera un informe estructurado detallando la tabla de
    transiciones generada dinámicamente y la justificación de aceptación de cada subconjunto.
    """
    if not auto.estado_inicial:
        raise ValueError("El autómata original no posee estado inicial definido.")

    # Alfabeto formal sin transiciones lambda
    alfabeto = sorted(list({s for s in auto.alfabeto if s != "" and s.lower() not in ("lambda", "epsilon", "λ", "ε")}))

    # 1. Subconjunto inicial S0 = lambda-cl({q0})
    s0_set = auto.clausura_lambda({auto.estado_inicial})
    nombre_s0 = formatear_nombre_subconjunto(s0_set)

    afd = Automata(
        alfabeto=set(alfabeto),
        estado_inicial=nombre_s0,
        tipo="AFD"
    )

    finales_en_s0 = s0_set.intersection(auto.estados_aceptacion)
    es_final_s0 = len(finales_en_s0) > 0
    razon_s0 = (
        f"Es de aceptación porque contiene el/los estado(s) final(es) original(es): {sorted(list(finales_en_s0))}."
        if es_final_s0 else
        f"No es de aceptación porque ninguno de sus estados pertenece a F={sorted(list(auto.estados_aceptacion))}."
    )

    afd.agregar_estado(nombre_s0, es_inicial=True, es_final=es_final_s0)

    # Registro de subconjuntos descubiertos: nombre -> set de estados originales
    visitados: Dict[str, Set[str]] = {nombre_s0: s0_set}
    cola = deque([(nombre_s0, s0_set)])

    subconjuntos_info: Dict[str, Dict[str, Any]] = {
        nombre_s0: {
            "nombre": nombre_s0,
            "estados_originales": sorted(list(s0_set)),
            "es_inicial": True,
            "es_final": es_final_s0,
            "finales_contenidos": sorted(list(finales_en_s0)),
            "justificacion": razon_s0
        }
    }

    pasos_construccion: List[Dict[str, Any]] = []
    tabla_generada: List[Dict[str, Any]] = []

    # 2. Exploración BFS de subconjuntos alcanzables
    ronda = 0
    while cola:
        ronda += 1
        nombre_actual, set_actual = cola.popleft()
        fila_tabla: Dict[str, str] = {"subconjunto": nombre_actual}
        transiciones_paso: Dict[str, str] = {}

        for a in alfabeto:
            # Mover y clausurar
            directos = auto.mover(set_actual, a)
            clausurados = auto.clausura_lambda(directos)
            nombre_destino = formatear_nombre_subconjunto(clausurados)

            fila_tabla[a] = nombre_destino
            transiciones_paso[a] = nombre_destino

            # Si es un subconjunto nuevo alcanzable
            if nombre_destino not in visitados:
                visitados[nombre_destino] = clausurados
                finales_en_dest = clausurados.intersection(auto.estados_aceptacion)
                es_final_dest = len(finales_en_dest) > 0

                razon_dest = (
                    f"Es de aceptación porque contiene el/los estado(s) final(es) original(es): {sorted(list(finales_en_dest))}."
                    if es_final_dest else
                    f"No es de aceptación porque no contiene estados de F={sorted(list(auto.estados_aceptacion))}."
                )

                subconjuntos_info[nombre_destino] = {
                    "nombre": nombre_destino,
                    "estados_originales": sorted(list(clausurados)),
                    "es_inicial": False,
                    "es_final": es_final_dest,
                    "finales_contenidos": sorted(list(finales_en_dest)),
                    "justificacion": razon_dest
                }

                afd.agregar_estado(nombre_destino, es_inicial=False, es_final=es_final_dest)
                cola.append((nombre_destino, clausurados))

            afd.agregar_transicion(nombre_actual, a, nombre_destino)

        tabla_generada.append(fila_tabla)
        pasos_construccion.append({
            "ronda": ronda,
            "subconjunto_evaluado": nombre_actual,
            "estados_base": sorted(list(set_actual)),
            "transiciones": transiciones_paso,
            "nuevos_alcanzados_en_ronda": [
                dest for dest in transiciones_paso.values()
                if dest in [item["nombre"] for item in subconjuntos_info.values()]
            ]
        })

    afd._actualizar_tipo()

    reporte = {
        "subconjunto_inicial": nombre_s0,
        "total_subconjuntos_alcanzables": len(visitados),
        "alfabeto": alfabeto,
        "tabla_transiciones": tabla_generada,
        "justificacion_subconjuntos": subconjuntos_info,
        "pasos_construccion": pasos_construccion
    }

    setattr(afd, "reporte_subconjuntos", reporte)
    return afd, reporte

