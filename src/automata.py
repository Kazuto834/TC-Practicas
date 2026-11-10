"""
Módulo del Motor Formal de Autómatas Finitos.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Antonio Navarro Domínguez (A7LAS-1) <tonyex1400@gmail.com>
Responsabilidad: Definición de la quíntupla M = (Q, Sigma, delta, q0, F),
                motor de simulación para AFD, AFND y AFND-lambda,
                cálculo de lambda-clausuras y trazas paso a paso.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque


@dataclass
class Transicion:
    """Representa una transición individual delta(origen, simbolo) -> destino."""
    origen: str
    simbolo: str  # Cadena vacía '' representa la transición nula/lambda/épsilon
    destino: str

    def es_lambda(self) -> bool:
        """Indica si la transición es nula (lambda / épsilon)."""
        return self.simbolo == "" or self.simbolo.lower() in ("lambda", "epsilon", "λ", "ε")


@dataclass
class Estado:
    """Representa un estado formal de un autómata con metadatos gráficos."""
    nombre: str
    es_inicial: bool = False
    es_final: bool = False
    pos_x: float = 100.0
    pos_y: float = 100.0


class Automata:
    """
    Representa un Autómata Finito formal M = (Q, Sigma, delta, q0, F).
    Soporta autómatas deterministas (AFD), no deterministas (AFND) y
    con transiciones lambda (AFND-lambda).
    """

    def __init__(
        self,
        alfabeto: Optional[Set[str]] = None,
        estados: Optional[Set[str]] = None,
        estado_inicial: Optional[str] = None,
        estados_aceptacion: Optional[Set[str]] = None,
        tipo: str = "AFD"
    ):
        self.alfabeto: Set[str] = set(alfabeto) if alfabeto else set()
        self.estados: Set[str] = set(estados) if estados else set()
        self.estado_inicial: Optional[str] = estado_inicial
        self.estados_aceptacion: Set[str] = set(estados_aceptacion) if estados_aceptacion else set()
        self.transiciones: List[Transicion] = []
        self.tipo: str = tipo  # 'AFD', 'AFND', 'AFND-lambda'
        self.metadatos_estados: Dict[str, Estado] = {}

    def agregar_estado(
        self,
        nombre: str,
        es_inicial: bool = False,
        es_final: bool = False,
        pos_x: float = 100.0,
        pos_y: float = 100.0
    ) -> None:
        """Registra un nuevo estado en el autómata con metadatos de renderizado."""
        self.estados.add(nombre)
        if es_inicial:
            self.estado_inicial = nombre
        if es_final:
            self.estados_aceptacion.add(nombre)
        self.metadatos_estados[nombre] = Estado(
            nombre=nombre,
            es_inicial=es_inicial,
            es_final=es_final,
            pos_x=pos_x,
            pos_y=pos_y
        )

    def agregar_simbolo(self, simbolo: str) -> None:
        """Agrega un símbolo al alfabeto formal del autómata."""
        if simbolo != "" and simbolo.lower() not in ("lambda", "epsilon", "λ", "ε"):
            self.alfabeto.add(simbolo)

    def agregar_transicion(self, origen: str, simbolo: str, destino: str) -> None:
        """
        Agrega una transición formal delta(origen, simbolo) -> destino.
        Normaliza símbolos lambda a la cadena vacía ''.
        """
        simbolo_normalizado = "" if simbolo.lower() in ("lambda", "epsilon", "λ", "ε", "") else simbolo
        
        self.estados.add(origen)
        self.estados.add(destino)
        if simbolo_normalizado:
            self.alfabeto.add(simbolo_normalizado)

        trans = Transicion(origen=origen, simbolo=simbolo_normalizado, destino=destino)
        if trans not in self.transiciones:
            self.transiciones.append(trans)
        
        # Ajuste dinámico del tipo de autómata
        self._actualizar_tipo()

    def _actualizar_tipo(self) -> None:
        """Evalúa las transiciones registradas para clasificar el autómata."""
        tiene_lambda = any(t.es_lambda() for t in self.transiciones)
        if tiene_lambda:
            self.tipo = "AFND-lambda"
            return

        tabla = self.obtener_tabla_transiciones()
        es_nd = False
        for est, trans_dict in tabla.items():
            for simb, dests in trans_dict.items():
                if len(dests) > 1:
                    es_nd = True
                    break
            if es_nd:
                break
        
        self.tipo = "AFND" if es_nd else "AFD"

    def obtener_tabla_transiciones(self) -> Dict[str, Dict[str, Set[str]]]:
        """
        Retorna la representación tabular canónica de delta:
        { estado_origen: { simbolo: {estados_destino} } }
        """
        tabla: Dict[str, Dict[str, Set[str]]] = {q: {} for q in self.estados}
        for t in self.transiciones:
            if t.simbolo not in tabla[t.origen]:
                tabla[t.origen][t.simbolo] = set()
            tabla[t.origen][t.simbolo].add(t.destino)
        return tabla

    def clausura_lambda(self, conjunto_estados: Set[str]) -> Set[str]:
        """
        Calcula la lambda-clausura (cerradura épsilon) reflexiva y transitiva
        de un conjunto de estados:
        lambda-cl(S) = S U { q' | existe camino de q en S hacia q' con etiquetas lambda }
        """
        clausura = set(conjunto_estados)
        cola = deque(conjunto_estados)

        trans_lambda: Dict[str, Set[str]] = {q: set() for q in self.estados}
        for t in self.transiciones:
            if t.es_lambda():
                if t.origen not in trans_lambda:
                    trans_lambda[t.origen] = set()
                trans_lambda[t.origen].add(t.destino)

        while cola:
            actual = cola.popleft()
            destinos = trans_lambda.get(actual, set())
            for d in destinos:
                if d not in clausura:
                    clausura.add(d)
                    cola.append(d)

        return clausura

    def mover(self, conjunto_estados: Set[str], simbolo: str) -> Set[str]:
        """
        Calcula la función de transición extendida de un conjunto:
        Delta(S, a) = Union_{q in S} delta(q, a)
        """
        destinos: Set[str] = set()
        for t in self.transiciones:
            if t.origen in conjunto_estados and t.simbolo == simbolo:
                destinos.add(t.destino)
        return destinos

    def es_determinista(self) -> Tuple[bool, str]:
        """
        Verifica formalmente si el autómata cumple con los axiomas de un AFD:
        1. No contiene transiciones lambda.
        2. Para cada estado q in Q y cada simbolo a in Sigma, existe como maximo
           una transicion delta(q, a).
        """
        for t in self.transiciones:
            if t.es_lambda():
                return False, f"Contiene transición lambda desde el estado '{t.origen}' hacia '{t.destino}'."

        tabla = self.obtener_tabla_transiciones()
        for est, trans_dict in tabla.items():
            for simb, dests in trans_dict.items():
                if len(dests) > 1:
                    return False, f"El estado '{est}' tiene transiciones múltiples no deterministas para el símbolo '{simb}': {sorted(list(dests))}."

        return True, "El autómata es determinista (AFD)."

    def simular_cadena(self, cadena: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Simula el procesamiento completo de una cadena de entrada.
        Soporta AFD, AFND y AFND-lambda siguiendo todos los caminos posibles concurrentemente.
        
        Retorna:
            (aceptada: bool, traza: List[Dict[str, Any]])
        
        Cada registro de la traza contiene:
            paso: int,
            simbolo_leido: Optional[str],
            estados_previos: List[str],
            clausura_previa: List[str],
            transiciones_tomadas: List[Dict[str, str]],
            estados_posteriores: List[str],
            clausura_posterior: List[str],
            es_aceptacion: bool
        """
        traza: List[Dict[str, Any]] = []

        if not self.estado_inicial:
            return False, [{"error": "El autómata no tiene estado inicial definido."}]

        # Estado inicial y su lambda-clausura
        activos_iniciales = {self.estado_inicial}
        activos = self.clausura_lambda(activos_iniciales)

        traza.append({
            "paso": 0,
            "simbolo_leido": None,
            "estados_previos": sorted(list(activos_iniciales)),
            "clausura_previa": sorted(list(activos)),
            "transiciones_tomadas": [],
            "estados_posteriores": sorted(list(activos)),
            "clausura_posterior": sorted(list(activos)),
            "es_aceptacion": any(q in self.estados_aceptacion for q in activos)
        })

        # Procesamiento secuencial de la cadena
        for i, char in enumerate(cadena, start=1):
            if char not in self.alfabeto:
                traza.append({
                    "paso": i,
                    "simbolo_leido": char,
                    "error": f"Símbolo '{char}' no pertenece al alfabeto {sorted(list(self.alfabeto))}.",
                    "estados_previos": sorted(list(activos)),
                    "estados_posteriores": [],
                    "es_aceptacion": False
                })
                return False, traza

            destinos_directos: Set[str] = set()
            trans_usadas: List[Dict[str, str]] = []

            for t in self.transiciones:
                if t.origen in activos and t.simbolo == char:
                    destinos_directos.add(t.destino)
                    trans_usadas.append({"desde": t.origen, "lee": t.simbolo, "hacia": t.destino})

            clausura_nueva = self.clausura_lambda(destinos_directos)

            es_final_paso = any(q in self.estados_aceptacion for q in clausura_nueva)

            traza.append({
                "paso": i,
                "simbolo_leido": char,
                "estados_previos": sorted(list(activos)),
                "clausura_previa": sorted(list(activos)),
                "transiciones_tomadas": trans_usadas,
                "estados_posteriores": sorted(list(destinos_directos)),
                "clausura_posterior": sorted(list(clausura_nueva)),
                "es_aceptacion": es_final_paso
            })

            activos = clausura_nueva
            if not activos:
                # Se agotaron los caminos válidos (bloqueo / sumidero)
                break

        aceptada = any(q in self.estados_aceptacion for q in activos)
        return aceptada, traza

    def validar_consistencia(self) -> Tuple[bool, List[str]]:
        """Valida que la quíntupla formal sea matemáticamente consistente."""
        errores: List[str] = []
        if not self.estados:
            errores.append("El conjunto de estados Q está vacío.")
        if not self.estado_inicial:
            errores.append("No se ha definido el estado inicial q0.")
        elif self.estado_inicial not in self.estados:
            errores.append(f"El estado inicial '{self.estado_inicial}' no pertenece al conjunto de estados Q.")

        for f in self.estados_aceptacion:
            if f not in self.estados:
                errores.append(f"El estado de aceptación '{f}' no pertenece al conjunto de estados Q.")

        for t in self.transiciones:
            if t.origen not in self.estados:
                errores.append(f"Transición con origen inválido '{t.origen}'.")
            if t.destino not in self.estados:
                errores.append(f"Transición con destino inválido '{t.destino}'.")
            if t.simbolo != "" and t.simbolo not in self.alfabeto:
                errores.append(f"Transición con símbolo '{t.simbolo}' que no pertenece a Sigma.")

        return len(errores) == 0, errores

