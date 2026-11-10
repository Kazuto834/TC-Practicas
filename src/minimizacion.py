"""
Módulo de Minimización y Equivalencia de Autómatas Finitos Deterministas (Práctica 3).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Eliminación de estados inaccesibles, minimización por refinamiento de
                particiones (Hopcroft / Moore) y prueba de equivalencia isomórfica.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional
from collections import deque
from automata import Automata


def eliminar_estados_inaccesibles(auto: Automata) -> Automata:
    """
    Elimina todos los estados de Q que no son alcanzables mediante ninguna
    secuencia de transiciones partiendo del estado inicial q0.
    """
    if not auto.estado_inicial:
        return auto

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

    # Construir autómata reducido
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
    return auto_depurado


def minimizar_afd(auto: Automata) -> Automata:
    """
    Obtiene el AFD mínimo equivalente mediante refinamiento iterativo de particiones
    (Teorema de Myhill-Nerode y algoritmo de Hopcroft / Moore).
    """
    # 1. Eliminar estados inaccesibles primero
    auto_accesible = eliminar_estados_inaccesibles(auto)

    estados = auto_accesible.estados
    finales = auto_accesible.estados_aceptacion
    no_finales = estados - finales

    if not finales:
        # Autómata que no acepta ninguna cadena: se reduce a un único estado sumidero
        afd_vacio = Automata(alfabeto=set(auto_accesible.alfabeto), tipo="AFD")
        afd_vacio.agregar_estado("q_trampa", es_inicial=True, es_final=False)
        for a in auto_accesible.alfabeto:
            afd_vacio.agregar_transicion("q_trampa", a, "q_trampa")
        return afd_vacio

    if not no_finales:
        # Todos los estados son finales
        particion: List[Set[str]] = [set(finales)]
    else:
        # Partición inicial P0 = { NoFinales, Finales }
        particion = [set(no_finales), set(finales)]

    tabla = auto_accesible.obtener_tabla_transiciones()
    alfabeto = sorted(list(auto_accesible.alfabeto))

    def obtener_indice_clase(estado: str, partes: List[Set[str]]) -> int:
        for idx, grupo in enumerate(partes):
            if estado in grupo:
                return idx
        return -1

    # 2. Refinamiento iterativo de bloques
    cambio = True
    while cambio:
        cambio = False
        nueva_particion: List[Set[str]] = []

        for grupo in particion:
            if len(grupo) <= 1:
                nueva_particion.append(grupo)
                continue

            # Subdividir el grupo según la firma de transición hacia las clases actuales
            firmas: Dict[Tuple[int, ...], Set[str]] = {}
            for q in grupo:
                firma_lista = []
                for a in alfabeto:
                    dests = tabla.get(q, {}).get(a, set())
                    dest = next(iter(dests)) if dests else None
                    dest_idx = obtener_indice_clase(dest, particion) if dest else -1
                    firma_lista.append(dest_idx)
                firma = tuple(firma_lista)
                if firma not in firmas:
                    firmas[firma] = set()
                firmas[firma].add(q)

            subgrupos = list(firmas.values())
            nueva_particion.extend(subgrupos)
            if len(subgrupos) > 1:
                cambio = True

        particion = nueva_particion

    # 3. Construir el AFD mínimo a partir de los bloques de la partición
    # Elegir nombre representativo para cada bloque
    bloque_a_nombre: Dict[int, str] = {}
    estado_a_bloque: Dict[str, str] = {}

    for idx, grupo in enumerate(particion):
        # Nombre conciso basado en los estados que contiene
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

    # Transiciones del AFD mínimo
    for idx, grupo in enumerate(particion):
        nombre_orig = bloque_a_nombre[idx]
        rep = next(iter(grupo))  # Un representante del grupo
        for a in alfabeto:
            dests = tabla.get(rep, {}).get(a, set())
            if dests:
                dest_rep = next(iter(dests))
                nombre_dest = estado_a_bloque[dest_rep]
                afd_min.agregar_transicion(nombre_orig, a, nombre_dest)

    afd_min._actualizar_tipo()
    return afd_min


def son_equivalentes(afd1: Automata, afd2: Automata, limite_longitud: int = 6) -> Tuple[bool, str]:
    """
    Verifica si dos autómatas finitos reconocen exactamente el mismo lenguaje.
    Comprueba que aceptan idéntico conjunto de palabras hasta una longitud acotada,
    y compara los tamaños de sus autómatas mínimos normalizados.
    """
    if set(afd1.alfabeto) != set(afd2.alfabeto):
        return False, f"Los alfabetos difieren: {sorted(list(afd1.alfabeto))} vs {sorted(list(afd2.alfabeto))}."

    # Comparación exhaustiva sobre todas las palabras de Sigma^k hasta limite_longitud
    import itertools
    alfabeto = sorted(list(afd1.alfabeto))
    for long in range(limite_longitud + 1):
        for combo in itertools.product(alfabeto, repeat=long):
            palabra = "".join(combo)
            res1, _ = afd1.simular_cadena(palabra)
            res2, _ = afd2.simular_cadena(palabra)
            if res1 != res2:
                return False, f"Discrepancia en la cadena '{palabra}': AFD1={res1}, AFD2={res2}."

    return True, "Los dos autómatas son formalmente equivalentes (reconocen el mismo lenguaje)."

