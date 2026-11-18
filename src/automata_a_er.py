"""
Módulo de Conversión de Autómata Finito a Expresión Regular (Teorema de Kleene - Parte II).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Algoritmo de eliminación progresiva de estados en autómatas finitos
                generalizados (GNFA) con simplificación algebraica sistemática.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple
from automata import Automata


def _simplificar_er(er: str) -> str:
    """Aplica simplificaciones algebraicas básicas a expresiones regulares."""
    er = er.strip()
    if not er:
        return "λ"
    if er == "λ*":
        return "λ"
    if er == "(λ)":
        return "λ"
    return er


def _concatenar_er(r1: str, r2: str) -> str:
    if not r1 or r1 in ("λ", "ε"):
        return r2
    if not r2 or r2 in ("λ", "ε"):
        return r1
    if r1 in ("∅", "Ø") or r2 in ("∅", "Ø"):
        return "∅"

    # Envolver si tiene unión al nivel superior
    p1 = f"({r1})" if "+" in r1 and not (r1.startswith("(") and r1.endswith(")")) else r1
    p2 = f"({r2})" if "+" in r2 and not (r2.startswith("(") and r2.endswith(")")) else r2
    return f"{p1}{p2}"


def _unir_er(r1: str, r2: str) -> str:
    if not r1 or r1 in ("∅", "Ø"):
        return r2
    if not r2 or r2 in ("∅", "Ø"):
        return r1
    if r1 == r2:
        return r1
    return f"{r1} + {r2}"


def _estrella_er(r: str) -> str:
    if not r or r in ("λ", "ε", "∅", "Ø"):
        return "λ"
    if r.endswith("*"):
        return r
    if len(r) == 1:
        return f"{r}*"
    if r.startswith("(") and r.endswith(")"):
        return f"{r}*"
    return f"({r})*"


def automata_a_expresion_regular(auto: Automata) -> Tuple[str, List[Dict[str, str]]]:
    """
    Convierte cualquier Autómata Finito (AFD o AFN) a su Expresión Regular equivalente
    utilizando el método de eliminación progresiva de estados (GNFA - Sipser, 2013).
    
    Retorna:
        (expresion_regular_final: str, historial_pasos: list[dict])
    """
    historial: List[Dict[str, str]] = []

    # Verificar que el autómata posea estado inicial y aceptación
    if not auto.estado_inicial:
        return "∅", [{"paso": "Error", "detalle": "El autómata no posee estado inicial."}]
    if not auto.estados_aceptacion:
        return "∅", [{"paso": "Base", "detalle": "No posee estados de aceptación; lenguaje vacío."}]

    # 1. Crear matriz de transiciones del GNFA: R[origen][destino] = expresion
    estados_originales = sorted(list(auto.estados))
    gnfa_estados = set(estados_originales)

    q_inicio = "q_gnfa_ini"
    q_fin = "q_gnfa_fin"
    gnfa_estados.add(q_inicio)
    gnfa_estados.add(q_fin)

    R: Dict[str, Dict[str, str]] = {q1: {q2: "∅" for q2 in gnfa_estados} for q1 in gnfa_estados}

    # Transiciones originales agrupadas
    for t in auto.transiciones:
        simb = t.simbolo if t.simbolo else "λ"
        actual = R[t.origen][t.destino]
        R[t.origen][t.destino] = simb if actual == "∅" else _unir_er(actual, simb)

    # Conectar nuevo inicio al inicial original con lambda
    R[q_inicio][auto.estado_inicial] = "λ"

    # Conectar estados de aceptación originales al nuevo fin con lambda
    for f in auto.estados_aceptacion:
        R[f][q_fin] = "λ"

    historial.append({
        "paso": "Inicialización GNFA",
        "detalle": f"Añadidos estados normalizados {q_inicio} y {q_fin}."
    })

    # 2. Eliminar progresivamente cada estado original q_rip
    for q_rip in estados_originales:
        gnfa_estados.remove(q_rip)
        r_rip_rip = R[q_rip][q_rip]
        estrella_rip = _estrella_er(r_rip_rip)

        for q_i in gnfa_estados:
            if q_i == q_fin:
                continue
            r_i_rip = R[q_i][q_rip]
            if r_i_rip == "∅":
                continue

            for q_j in gnfa_estados:
                if q_j == q_inicio:
                    continue
                r_rip_j = R[q_rip][q_j]
                if r_rip_j == "∅":
                    continue

                r_directo = R[q_i][q_j]
                # Camino que cruza por q_rip: R[i, rip] · (R[rip, rip])* · R[rip, j]
                r_cruzado = _concatenar_er(_concatenar_er(r_i_rip, estrella_rip), r_rip_j)
                R[q_i][q_j] = _unir_er(r_directo, r_cruzado)

        historial.append({
            "paso": f"Eliminado estado {q_rip}",
            "detalle": f"Transiciones cruzadas recalculadas. Estados restantes: {len(gnfa_estados)}"
        })

    # 3. La expresión final es la única arista restante entre q_inicio y q_fin
    er_final = R[q_inicio][q_fin]
    if er_final == "∅":
        er_final = "λ" if auto.estado_inicial in auto.estados_aceptacion else "∅"

    return _simplificar_er(er_final), historial

