"""
Módulo de Minimización de Autómatas Finitos Deterministas por Refinamiento de Particiones.

Ejercicio 2.4: Extensión del software interactivo.
Elimina estados inaccesibles y obtiene el AFD mínimo por refinamiento de particiones
(algoritmo de Moore / Hopcroft), mostrando la partición en cada ronda paso a paso.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional, Any
from automata import Automata
from eliminacion_inaccesibles import eliminar_estados_inaccesibles


def minimizar_afd(auto: Automata) -> Automata:
    """
    Obtiene el AFD mínimo equivalente mediante refinamiento iterativo de particiones
    (Hopcroft, 1971; Hopcroft, Motwani, & Ullman, 2007, Secc. 4.4.3).

    Retorna:
        Instancia de Automata determinista mínimo con el atributo `reporte_minimizacion`.
    """
    afd_min, _ = minimizar_afd_detallado(auto)
    return afd_min


def minimizar_afd_detallado(auto: Automata) -> Tuple[Automata, Dict[str, Any]]:
    """
    Versión extendida que retorna el autómata mínimo y una bitácora exhaustiva
    de cada ronda de refinamiento de particiones.
    """
    # 1. Eliminar estados inaccesibles primero
    auto_accesible = eliminar_estados_inaccesibles(auto)

    estados = auto_accesible.estados
    finales = auto_accesible.estados_aceptacion
    no_finales = estados - finales

    # Caso borde: Sin estados de aceptacion (lenguaje vacio)
    if not finales:
        afd_vacio = Automata(alfabeto=set(auto_accesible.alfabeto), tipo="AFD")
        afd_vacio.agregar_estado("q_trampa", es_inicial=True, es_final=False)
        for a in auto_accesible.alfabeto:
            afd_vacio.agregar_transicion("q_trampa", a, "q_trampa")
        reporte_vacio = {
            "rondas": [{"ronda": 0, "particion": [sorted(list(estados))], "descripcion": "Autómata sin estados finales."}],
            "total_estados_original": len(auto.estados),
            "total_estados_accesibles": len(estados),
            "total_estados_minimo": 1
        }
        setattr(afd_vacio, "reporte_minimizacion", reporte_vacio)
        return afd_vacio, reporte_vacio

    # Partición inicial P0 = { NoFinales, Finales } (si alguno no está vacío)
    particion: List[Set[str]] = []
    if no_finales:
        particion.append(set(no_finales))
    if finales:
        particion.append(set(finales))

    tabla = auto_accesible.obtener_tabla_transiciones()
    alfabeto = sorted(list({s for s in auto_accesible.alfabeto if s != ""}))

    def formatear_particion(part: List[Set[str]]) -> List[List[str]]:
        return [sorted(list(g)) for g in part]

    def obtener_indice_clase(est: Optional[str], partes: List[Set[str]]) -> int:
        if est is None:
            return -1
        for idx, grupo in enumerate(partes):
            if est in grupo:
                return idx
        return -1

    rondas_log: List[Dict[str, Any]] = [{
        "ronda": 0,
        "particion": formatear_particion(particion),
        "descripcion": f"Partición inicial P0: {formatear_particion(particion)} (No Finales vs Finales)."
    }]

    # 2. Refinamiento iterativo de clases de equivalencia
    ronda = 0
    cambio = True
    while cambio:
        ronda += 1
        cambio = False
        nueva_particion: List[Set[str]] = []
        divisiones_ronda: List[Dict[str, Any]] = []

        for grupo in particion:
            if len(grupo) <= 1:
                nueva_particion.append(grupo)
                continue

            # Subdividir el grupo según la firma de transición hacia las clases actuales
            firmas: Dict[Tuple[int, ...], Set[str]] = {}
            for q in sorted(list(grupo)):
                firma_lista = []
                for a in alfabeto:
                    dests = tabla.get(q, {}).get(a, set())
                    dest = next(iter(dests)) if dests else None
                    dest_idx = obtener_indice_clase(dest, particion)
                    firma_lista.append(dest_idx)
                firma = tuple(firma_lista)
                if firma not in firmas:
                    firmas[firma] = set()
                firmas[firma].add(q)

            subgrupos = list(firmas.values())
            nueva_particion.extend(subgrupos)

            if len(subgrupos) > 1:
                cambio = True
                divisiones_ronda.append({
                    "grupo_original": sorted(list(grupo)),
                    "subgrupos_generados": [sorted(list(sg)) for sg in subgrupos]
                })

        particion = nueva_particion
        rondas_log.append({
            "ronda": ronda,
            "particion": formatear_particion(particion),
            "hubo_cambio": cambio,
            "divisiones": divisiones_ronda,
            "descripcion": (
                f"Ronda {ronda}: Se obtienen {len(particion)} clases. "
                + (f"Se subdividieron {len(divisiones_ronda)} grupos." if cambio else "Estabilidad alcanzada.")
            )
        })

    # 3. Construir el AFD mínimo a partir de los bloques de la partición final
    bloque_a_nombre: Dict[int, str] = {}
    estado_a_bloque: Dict[str, str] = {}

    for idx, grupo in enumerate(particion):
        nombre_bloque = "[" + ",".join(sorted(list(grupo))) + "]"
        bloque_a_nombre[idx] = nombre_bloque
        for q in grupo:
            estado_a_bloque[q] = nombre_bloque

    inicial_bloque = estado_a_bloque[auto_accesible.estado_inicial]

    afd_min = Automata(
        alfabeto=set(alfabeto),
        estado_inicial=inicial_bloque,
        tipo="AFD"
    )

    for idx, grupo in enumerate(particion):
        nombre_b = bloque_a_nombre[idx]
        es_ini = (nombre_b == inicial_bloque)
        es_fin = any(q in finales for q in grupo)
        afd_min.agregar_estado(nombre_b, es_inicial=es_ini, es_final=es_fin)

    # Añadir transiciones colapsadas
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

    reporte = {
        "estados_originales": len(auto.estados),
        "estados_accesibles": len(auto_accesible.estados),
        "estados_minimos": len(afd_min.estados),
        "estados_reducidos": len(auto.estados) - len(afd_min.estados),
        "rondas": rondas_log,
        "particion_final": formatear_particion(particion),
        "mapeo_estados": estado_a_bloque
    }

    setattr(afd_min, "reporte_minimizacion", reporte)
    return afd_min, reporte

