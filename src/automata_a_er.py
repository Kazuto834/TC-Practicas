"""
Módulo de Conversión de Autómata Finito a Expresión Regular (Teorema de Kleene - Parte II).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Verificación estricta de determinismo (estado y símbolo conflictivo),
                eliminación progresiva de estados en autómatas finitos generalizados (GNFA)
                con instantáneas paso a paso, y comprobación de equivalencia con JFLAP.
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List, Optional, Tuple
from automata import Automata
from equivalencia_afd import decidir_equivalencia_detallada
from er_a_automata import er_a_pipeline_completo


def verificar_determinismo_detallado(auto: Automata) -> Dict[str, Any]:
    """
    Verifica formalmente si el autómata es determinista (AFD).
    En caso contrario, indica exactamente qué estado y qué símbolo lo impiden.
    """
    if not auto.estado_inicial:
        return {
            "es_determinista": False,
            "estado_conflicto": None,
            "simbolo_conflicto": None,
            "motivo": "El autómata no posee un estado inicial definido.",
        }

    # 1. Verificar ausencia de transiciones vacías (lambda)
    for t in auto.transiciones:
        if t.es_lambda():
            return {
                "es_determinista": False,
                "estado_conflicto": t.origen,
                "simbolo_conflicto": "λ",
                "motivo": (
                    f"No es determinista: el estado '{t.origen}' tiene una transición vacía "
                    f"con el símbolo 'λ' hacia '{t.destino}'."
                ),
            }

    # 2. Verificar unicidad de transición por par (estado, símbolo)
    tabla = auto.obtener_tabla_transiciones()
    for est in sorted(tabla.keys()):
        for simb in sorted(tabla[est].keys()):
            dests = sorted(list(tabla[est][simb]))
            if len(dests) > 1:
                return {
                    "es_determinista": False,
                    "estado_conflicto": est,
                    "simbolo_conflicto": simb,
                    "motivo": (
                        f"No es determinista: en el estado '{est}' con el símbolo '{simb}' "
                        f"existen {len(dests)} transiciones hacia {dests}."
                    ),
                }

    return {
        "es_determinista": True,
        "estado_conflicto": None,
        "simbolo_conflicto": None,
        "motivo": "El autómata cumple la definición formal de AFD (determinista).",
    }


def _envolver_si_union(r: str) -> str:
    if "+" not in r:
        return r
    nivel = 0
    for ch in r:
        if ch == "(":
            nivel += 1
        elif ch == ")":
            nivel -= 1
        elif ch == "+" and nivel == 0:
            return f"({r})"
    return r


def _envolver_para_estrella(r: str) -> str:
    if len(r) == 1:
        return r
    if r.startswith("(") and r.endswith(")"):
        nivel = 0
        cierra_al_final = True
        for i, ch in enumerate(r):
            if ch == "(":
                nivel += 1
            elif ch == ")":
                nivel -= 1
            if nivel == 0 and i < len(r) - 1:
                cierra_al_final = False
                break
        if cierra_al_final:
            return r
    return f"({r})"


def _simplificar_er(er: str) -> str:
    """Aplica simplificaciones algebraicas básicas a expresiones regulares."""
    er = er.strip()
    if not er or er in ("λ*", "(λ)", "∅*", "(∅)*"):
        return "λ"
    return er


def _concatenar_er(r1: str, r2: str) -> str:
    r1 = _simplificar_er(r1)
    r2 = _simplificar_er(r2)
    if r1 in ("∅", "Ø") or r2 in ("∅", "Ø"):
        return "∅"
    if r1 in ("λ", "ε"):
        return r2
    if r2 in ("λ", "ε"):
        return r1

    p1 = _envolver_si_union(r1)
    p2 = _envolver_si_union(r2)
    return f"{p1}{p2}"


def _unir_er(r1: str, r2: str) -> str:
    r1 = _simplificar_er(r1)
    r2 = _simplificar_er(r2)
    if r1 in ("∅", "Ø"):
        return r2
    if r2 in ("∅", "Ø"):
        return r1
    if r1 == r2:
        return r1
    return f"{r1}+{r2}"


def _estrella_er(r: str) -> str:
    r = _simplificar_er(r)
    if r in ("λ", "ε", "∅", "Ø"):
        return "λ"
    if r.endswith("*") and _envolver_para_estrella(r[:-1]) == r[:-1]:
        return r
    return f"{_envolver_para_estrella(r)}*"


def _construir_snapshot_gnfa(
    estados_activos: List[str],
    matriz: Dict[str, Dict[str, str]],
    q_inicio: str,
    q_fin: str,
) -> Automata:
    """Construye una instancia visualizable de Automata representando el GNFA actual."""
    gnfa_visual = Automata(estado_inicial=q_inicio, tipo="GNFA")
    for q in estados_activos:
        gnfa_visual.agregar_estado(
            q,
            es_inicial=(q == q_inicio),
            es_final=(q == q_fin),
        )
    for orig in estados_activos:
        for dest in estados_activos:
            etq = matriz.get(orig, {}).get(dest, "∅")
            if etq != "∅":
                gnfa_visual.agregar_transicion(orig, etq, dest)
                gnfa_visual.tipo = "GNFA"
    return gnfa_visual


def automata_a_expresion_regular(
    auto: Automata,
    orden_eliminacion: Optional[List[str]] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Convierte un Autómata Finito a su Expresión Regular equivalente
    utilizando el método de eliminación progresiva de estados (GNFA).

    Retorna:
        (expresion_regular_final: str, historial_pasos: list[dict])
    """
    historial: List[Dict[str, Any]] = []

    if not auto.estado_inicial:
        return "∅", [{
            "paso": "Error",
            "estado_eliminado": None,
            "detalle": "El autómata no posee estado inicial.",
            "estados_restantes": [],
            "aristas_gnfa": [],
            "gnfa_automata": Automata(),
        }]
    if not auto.estados_aceptacion:
        return "∅", [{
            "paso": "Base",
            "estado_eliminado": None,
            "detalle": "No posee estados de aceptación; lenguaje vacío (∅).",
            "estados_restantes": sorted(list(auto.estados)),
            "aristas_gnfa": [],
            "gnfa_automata": auto,
        }]

    estados_originales = sorted(list(auto.estados))
    if orden_eliminacion:
        validos = [q for q in orden_eliminacion if q in auto.estados]
        restantes = [q for q in estados_originales if q not in validos]
        estados_a_eliminar = validos + restantes
    else:
        estados_a_eliminar = estados_originales

    q_inicio = "q_gnfa_ini"
    q_fin = "q_gnfa_fin"
    gnfa_estados = [q_inicio] + estados_originales + [q_fin]

    R: Dict[str, Dict[str, str]] = {q1: {q2: "∅" for q2 in gnfa_estados} for q1 in gnfa_estados}

    for t in auto.transiciones:
        simb = t.simbolo if t.simbolo else "λ"
        actual = R[t.origen][t.destino]
        R[t.origen][t.destino] = simb if actual == "∅" else _unir_er(actual, simb)

    R[q_inicio][auto.estado_inicial] = "λ"
    for f in sorted(list(auto.estados_aceptacion)):
        R[f][q_fin] = "λ"

    def registrar_paso(titulo: str, eliminado: Optional[str], detalle: str) -> None:
        aristas = [
            (u, R[u][v], v)
            for u in gnfa_estados
            for v in gnfa_estados
            if R[u][v] != "∅"
        ]
        historial.append({
            "paso": titulo,
            "estado_eliminado": eliminado,
            "detalle": detalle,
            "estados_restantes": list(gnfa_estados),
            "aristas_gnfa": aristas,
            "gnfa_automata": _construir_snapshot_gnfa(gnfa_estados, copy.deepcopy(R), q_inicio, q_fin),
        })

    registrar_paso(
        "Inicialización GNFA",
        None,
        f"Añadidos estados normalizados {q_inicio} (λ → {auto.estado_inicial}) y {q_fin} (desde {sorted(list(auto.estados_aceptacion))} con λ).",
    )

    for q_rip in estados_a_eliminar:
        gnfa_estados.remove(q_rip)
        r_rip_rip = R[q_rip][q_rip]
        estrella_rip = _estrella_er(r_rip_rip)

        cambios: List[str] = []
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
                r_cruzado = _concatenar_er(_concatenar_er(r_i_rip, estrella_rip), r_rip_j)
                nuevo = _unir_er(r_directo, r_cruzado)
                R[q_i][q_j] = nuevo
                cambios.append(f"R({q_i}, {q_j}) = {nuevo}")

        detalle_cambios = "; ".join(cambios) if cambios else "Sin nuevas rutas a través de este estado."
        registrar_paso(
            f"Eliminado estado {q_rip}",
            q_rip,
            f"Transiciones cruzadas recalculadas (bucle={r_rip_rip}). Actualizaciones: {detalle_cambios}",
        )

    er_final = R[q_inicio][q_fin]
    if er_final == "∅":
        er_final = "λ" if auto.estado_inicial in auto.estados_aceptacion else "∅"

    return _simplificar_er(er_final), historial


def comparar_expresiones_regulares(
    er_propia: str,
    er_jflap: str,
    macros: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Compara si dos expresiones regulares (la obtenida por GNFA y la obtenida con JFLAP)
    son equivalentes convirtiendo ambas a AFD mínimos con el Ejercicio 2 y aplicando
    la prueba de equivalencia de la Práctica 3.
    """
    afd_min_1: Automata = er_a_pipeline_completo(er_propia, macros=macros)["afd_minimo"]
    afd_min_2: Automata = er_a_pipeline_completo(er_jflap, macros=macros)["afd_minimo"]

    equivalentes, mensaje, detalle = decidir_equivalencia_detallada(afd_min_1, afd_min_2)
    return {
        "equivalentes": equivalentes,
        "mensaje": mensaje,
        "detalle": detalle,
        "afd_min_1": afd_min_1,
        "afd_min_2": afd_min_2,
    }