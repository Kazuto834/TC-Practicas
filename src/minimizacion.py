"""
Módulo de Minimización y Equivalencia de Autómatas Finitos Deterministas (Práctica 3).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autores: Antonio Navarro Domínguez (A7LAS-1) & Mario García Castillo (Kazuto834)
Responsabilidad: Eliminación de estados inaccesibles, minimización por refinamiento de
                particiones (Hopcroft / Moore) paso a paso, y prueba formal de
                equivalencia isomórfica entre autómatas mínimos.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque
import itertools
from automata import Automata


def eliminar_estados_inaccesibles_detallado(auto: Automata) -> Tuple[Automata, Set[str], Set[str]]:
    """
    Elimina los estados no alcanzables desde el estado inicial q0.
    Retorna:
      (auto_accesible, estados_alcanzables, estados_eliminados)
    """
    if not auto.estado_inicial:
        return auto, set(auto.estados), set()

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

    eliminados = set(auto.estados) - alcanzables

    auto_depurado = Automata(
        alfabeto=set(auto.alfabeto),
        estado_inicial=auto.estado_inicial,
        tipo=auto.tipo
    )

    for q in alcanzables:
        auto_depurado.agregar_estado(
            nombre=q,
            es_inicial=(q == auto.estado_inicial),
            es_final=(q in auto.estados_aceptacion)
        )

    for t in auto.transiciones:
        if t.origen in alcanzables and t.destino in alcanzables:
            auto_depurado.agregar_transicion(t.origen, t.simbolo, t.destino)

    auto_depurado._actualizar_tipo()
    return auto_depurado, alcanzables, eliminados


def eliminar_estados_inaccesibles(auto: Automata) -> Automata:
    """Función de compatibilidad: retorna directamente el autómata con estados accesibles."""
    auto_dep, _, _ = eliminar_estados_inaccesibles_detallado(auto)
    return auto_dep


def minimizar_afd_detallado(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Obtiene el AFD mínimo equivalente mediante refinamiento iterativo de particiones
    (Teorema de Myhill-Nerode y algoritmo de Hopcroft / Moore).
    Retorna el AFD mínimo y la bitácora paso a paso de cada ronda de partición.
    """
    auto_accesible, alcanzables, eliminados = eliminar_estados_inaccesibles_detallado(auto)

    estados = auto_accesible.estados
    finales = auto_accesible.estados_aceptacion
    no_finales = estados - finales

    # Caso borde: sin estados de aceptación
    if not finales:
        afd_vacio = Automata(alfabeto=set(auto_accesible.alfabeto), tipo="AFD")
        afd_vacio.agregar_estado("q_trampa", es_inicial=True, es_final=False)
        for a in auto_accesible.alfabeto:
            afd_vacio.agregar_transicion("q_trampa", a, "q_trampa")
        bitacora_vacio = {
            "inaccesibles_eliminados": sorted(list(eliminados)),
            "particion_inicial": [sorted(list(estados))],
            "rondas": [],
            "particion_final": [["q_trampa"]],
            "mapeo_bloques": {"q_trampa": sorted(list(estados))}
        }
        return afd_vacio, bitacora_vacio

    # Partición inicial P0
    if not no_finales:
        particion: List[Set[str]] = [set(finales)]
    else:
        particion = [set(no_finales), set(finales)]

    tabla = auto_accesible.obtener_tabla_transiciones()
    alfabeto = sorted(list(auto_accesible.alfabeto))

    def obtener_indice_clase(estado: Optional[str], partes: List[Set[str]]) -> int:
        if not estado:
            return -1
        for idx, grupo in enumerate(partes):
            if estado in grupo:
                return idx
        return -1

    rondas_log: List[Dict[str, Any]] = []
    ronda_num = 0

    # Registrar P0
    rondas_log.append({
        "ronda": 0,
        "particion": [sorted(list(g)) for g in particion],
        "descripcion": "Partición inicial P0 = { No Finales, Finales }"
    })

    cambio = True
    while cambio:
        ronda_num += 1
        cambio = False
        nueva_particion: List[Set[str]] = []
        detalles_ronda = []

        for g_idx, grupo in enumerate(particion):
            if len(grupo) <= 1:
                nueva_particion.append(grupo)
                detalles_ronda.append({
                    "grupo_original": sorted(list(grupo)),
                    "subgrupos": [sorted(list(grupo))],
                    "dividido": False
                })
                continue

            firmas: Dict[Tuple[int, ...], Set[str]] = {}
            firmas_legibles: Dict[str, Dict[str, int]] = {}

            for q in sorted(list(grupo)):
                firma_lista = []
                legible_q = {}
                for a in alfabeto:
                    dests = tabla.get(q, {}).get(a, set())
                    dest = next(iter(dests)) if dests else None
                    dest_idx = obtener_indice_clase(dest, particion)
                    firma_lista.append(dest_idx)
                    legible_q[a] = dest_idx
                firma = tuple(firma_lista)
                if firma not in firmas:
                    firmas[firma] = set()
                firmas[firma].add(q)
                firmas_legibles[q] = legible_q

            subgrupos = [firmas[f] for f in firmas]
            nueva_particion.extend(subgrupos)

            se_dividio = len(subgrupos) > 1
            if se_dividio:
                cambio = True

            detalles_ronda.append({
                "grupo_original": sorted(list(grupo)),
                "firmas": {q: firmas_legibles[q] for q in sorted(list(grupo))},
                "subgrupos": [sorted(list(sg)) for sg in subgrupos],
                "dividido": se_dividio
            })

        particion = nueva_particion
        rondas_log.append({
            "ronda": ronda_num,
            "particion": [sorted(list(g)) for g in particion],
            "detalles": detalles_ronda,
            "hubo_cambio": cambio
        })

    # Construir el autómata mínimo representativo
    bloque_a_nombre: Dict[int, str] = {}
    estado_a_bloque: Dict[str, str] = {}

    for idx, grupo in enumerate(particion):
        nombre_bloque = "[" + ",".join(sorted(list(grupo))) + "]"
        bloque_a_nombre[idx] = nombre_bloque
        for q in grupo:
            estado_a_bloque[q] = nombre_bloque

    inicial_bloque = estado_a_bloque[auto_accesible.estado_inicial]

    afd_min = Automata(
        alfabeto=set(auto_accesible.alfabeto),
        estado_inicial=inicial_bloque,
        tipo="AFD"
    )

    for idx, grupo in enumerate(particion):
        nombre_b = bloque_a_nombre[idx]
        es_ini = (nombre_b == inicial_bloque)
        es_fin = any(q in finales for q in grupo)
        afd_min.agregar_estado(nombre_b, es_inicial=es_ini, es_final=es_fin)

    for idx, grupo in enumerate(particion):
        nombre_orig = bloque_a_nombre[idx]
        rep = next(iter(grupo))
        for a in alfabeto:
            dests = tabla.get(rep, {}).get(a, set())
            if dests:
                dest_rep = next(iter(dests))
                nombre_dest = estado_a_bloque[dest_rep]
                afd_min.agregar_transicion(nombre_orig, a, nombre_dest)

    afd_min._actualizar_tipo()

    bitacora = {
        "inaccesibles_eliminados": sorted(list(eliminados)),
        "estados_accesibles": sorted(list(alcanzables)),
        "particion_inicial": rondas_log[0]["particion"],
        "rondas": rondas_log,
        "particion_final": [sorted(list(g)) for g in particion],
        "mapeo_bloques": {bloque_a_nombre[i]: sorted(list(g)) for i, g in enumerate(particion)}
    }

    return afd_min, bitacora


def minimizar_afd(auto: Automata) -> Automata:
    """Función de compatibilidad: retorna directamente el AFD mínimo equivalente."""
    afd_min, _ = minimizar_afd_detallado(auto)
    return afd_min


def verificar_equivalencia_isomorfica(afd1: Automata, afd2: Automata) -> Tuple[bool, str, Optional[Dict[str, str]]]:
    """
    Decide si dos AFD son equivalentes mediante la comparación de sus AFD mínimos.
    De acuerdo con el Teorema de Myhill-Nerode, dos autómatas son equivalentes si y sólo si
    sus autómatas mínimos coinciden salvo el nombre de los estados (son isomorfos).
    """
    if set(afd1.alfabeto) != set(afd2.alfabeto):
        return False, f"Los alfabetos difieren: {sorted(list(afd1.alfabeto))} vs {sorted(list(afd2.alfabeto))}.", None

    min1 = minimizar_afd(afd1)
    min2 = minimizar_afd(afd2)

    if len(min1.estados) != len(min2.estados):
        return False, f"Los AFD mínimos tienen diferente número de estados ({len(min1.estados)} vs {len(min2.estados)}).", None

    if len(min1.estados_aceptacion) != len(min2.estados_aceptacion):
        return False, f"Los AFD mínimos tienen diferente cantidad de estados finales ({len(min1.estados_aceptacion)} vs {len(min2.estados_aceptacion)}).", None

    if not min1.estado_inicial or not min2.estado_inicial:
        return (min1.estado_inicial == min2.estado_inicial), "Autómatas sin estado inicial definido.", None

    # Mapeo isomorfo biyectivo por BFS
    mapeo: Dict[str, str] = {min1.estado_inicial: min2.estado_inicial}
    inverso: Dict[str, str] = {min2.estado_inicial: min1.estado_inicial}

    # Verificar que el estado inicial comparta condición de aceptación
    if (min1.estado_inicial in min1.estados_aceptacion) != (min2.estado_inicial in min2.estados_aceptacion):
        return False, "Discrepancia en la condición de aceptación del estado inicial en los mínimos.", None

    cola = deque([(min1.estado_inicial, min2.estado_inicial)])
    tabla1 = min1.obtener_tabla_transiciones()
    tabla2 = min2.obtener_tabla_transiciones()
    alfabeto = sorted(list(min1.alfabeto))

    while cola:
        u1, u2 = cola.popleft()
        for a in alfabeto:
            d1_set = tabla1.get(u1, {}).get(a, set())
            d2_set = tabla2.get(u2, {}).get(a, set())

            v1 = next(iter(d1_set)) if d1_set else None
            v2 = next(iter(d2_set)) if d2_set else None

            if (v1 is None) != (v2 is None):
                return False, f"Transición para símbolo '{a}' presente en uno pero ausente en el otro ({u1} vs {u2}).", None

            if v1 is not None and v2 is not None:
                if v1 in mapeo:
                    if mapeo[v1] != v2:
                        return False, f"Conflicto de isomorfismo: {v1} fue mapeado a {mapeo[v1]}, pero ahora requiere {v2}.", None
                else:
                    if v2 in inverso:
                        return False, f"Conflicto de inyectividad: {v2} ya estaba asignado a {inverso[v2]}.", None

                    # Deben tener la misma naturaleza de aceptación
                    if (v1 in min1.estados_aceptacion) != (v2 in min2.estados_aceptacion):
                        return False, f"Estados correspondientes {v1} y {v2} difieren en aceptación.", None

                    mapeo[v1] = v2
                    inverso[v2] = v1
                    cola.append((v1, v2))

    if len(mapeo) != len(min1.estados):
        return False, "No todos los estados del autómata mínimo pudieron ser emparejados isomorficamente.", None

    msg = f"Los autómatas mínimos son idénticos salvo renombre de estados (isomorfismo verificado de {len(mapeo)} estados). Reconocen exactamente el mismo lenguaje formal."
    return True, msg, mapeo


def son_equivalentes(afd1: Automata, afd2: Automata, limite_longitud: int = 6) -> Tuple[bool, str]:
    """
    Decide si dos AFD son equivalentes combinando el isomorfismo de sus AFD mínimos
    y validación de palabras frontera.
    """
    equiv, msg, _ = verificar_equivalencia_isomorfica(afd1, afd2)
    if not equiv:
        # Búsqueda de contraejemplo mínimo para retroalimentación
        alfabeto = sorted(list(set(afd1.alfabeto).intersection(set(afd2.alfabeto))))
        for long in range(limite_longitud + 1):
            for combo in itertools.product(alfabeto, repeat=long):
                palabra = "".join(combo)
                res1, _ = afd1.simular_cadena(palabra)
                res2, _ = afd2.simular_cadena(palabra)
                if res1 != res2:
                    return False, f"{msg} Contraejemplo mínimo encontrado: la cadena '{palabra}' es aceptada por uno y rechazada por el otro."
        return False, msg

    return True, msg
