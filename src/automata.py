"""
===============================================================================
MÓDULO DEL MOTOR FORMAL DE AUTÓMATAS FINITOS (AFD, AFND, AFND-λ)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación
Institución: Escuela Superior de Cómputo (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Implementa el motor matemático formal de autómatas finitos según la quíntupla
    estándar M = (Q, Sigma, delta, q0, F). Provee:
      - Modelado formal de estados, símbolos y transiciones (incluyendo λ / épsilon).
      - Clasificación automática entre AFD, AFND y AFND-lambda.
      - Cálculo de la lambda-clausura reflexiva y transitiva (Sección 2.3).
      - Función de transición extendida y mover entre conjuntos de estados.
      - Motor de simulación paso a paso con registro completo de la traza de ejecución
        y exploración concurrente de bifurcaciones no deterministas (Sección 3.3).
      - Validación de consistencia matemática de la quíntupla.

Navegación del Módulo:
    1. Estructuras de Datos Elementales: Transicion, Estado
    2. Clase Principal: Automata (Inicialización y Mutadores de Quíntupla)
    3. Clasificación Formal y Representación Tabular
    4. Algoritmos de Clausura Lambda y Transición Extendida
    5. Motor de Simulación y Traza de Ejecución Paso a Paso
    6. Verificación de Consistencia Matemática
===============================================================================
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque


# =============================================================================
# SECCIÓN 1: ESTRUCTURAS DE DATOS ELEMENTALES
# =============================================================================

@dataclass
class Transicion:
    """
    Representa una transición formal individual: delta(origen, simbolo) -> destino.
    
    Atributos:
        origen (str): Estado de procedencia q_i.
        simbolo (str): Símbolo de transición. La cadena vacía '' representa lambda/épsilon.
        destino (str): Estado alcanzado q_j.
    """
    origen: str
    simbolo: str
    destino: str

    def es_lambda(self) -> bool:
        """
        Determina si la transición es nula (lambda / épsilon).
        Admite '', 'lambda', 'epsilon', 'λ', 'ε'.
        """
        return self.simbolo == "" or self.simbolo.lower() in ("lambda", "epsilon", "λ", "ε")


@dataclass
class Estado:
    """
    Representa un estado formal de un autómata finito junto con metadatos gráficos.
    
    Atributos:
        nombre (str): Identificador único del estado (ej. 'q0', 'q1').
        es_inicial (bool): Verdadero si q in {q0}.
        es_final (bool): Verdadero si q in F (estado de aceptación).
        pos_x (float): Coordenada horizontal para renderizado en JFLAP.
        pos_y (float): Coordenada vertical para renderizado en JFLAP.
    """
    nombre: str
    es_inicial: bool = False
    es_final: bool = False
    pos_x: float = 100.0
    pos_y: float = 100.0


# =============================================================================
# SECCIÓN 2: CLASE PRINCIPAL AUTOMATA (QUÍNTUPLA FORMAL)
# =============================================================================

class Automata:
    """
    Representación matemática formal de un Autómata Finito M = (Q, Sigma, delta, q0, F).
    Soporta autómatas deterministas (AFD), no deterministas (AFND) y
    con transiciones lambda (AFND-lambda).
    """

    # -------------------------------------------------------------------------
    # 2.1 Inicialización y Gestión de Componentes
    # -------------------------------------------------------------------------
    def __init__(
        self,
        alfabeto: Optional[Set[str]] = None,
        estados: Optional[Set[str]] = None,
        estado_inicial: Optional[str] = None,
        estados_aceptacion: Optional[Set[str]] = None,
        tipo: str = "AFD"
    ) -> None:
        """Inicializa la quíntupla matemática formal."""
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
        """
        Registra un estado q in Q con sus condiciones inicial/final y coordenadas.
        """
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
        """
        Registra un símbolo formal a in Sigma.
        Ignora símbolos lambda/épsilon ya que no forman parte del alfabeto Sigma.
        """
        if simbolo != "" and simbolo.lower() not in ("lambda", "epsilon", "λ", "ε"):
            self.alfabeto.add(simbolo)

    def agregar_transicion(self, origen: str, simbolo: str, destino: str) -> None:
        """
        Registra una transición formal delta(origen, simbolo) -> destino.
        Normaliza etiquetas de transición vacías o equivalentes a lambda como ''.
        """
        simbolo_normalizado = "" if simbolo.lower() in ("lambda", "epsilon", "λ", "ε", "") else simbolo

        self.estados.add(origen)
        self.estados.add(destino)
        if simbolo_normalizado:
            self.alfabeto.add(simbolo_normalizado)

        trans = Transicion(origen=origen, simbolo=simbolo_normalizado, destino=destino)
        if trans not in self.transiciones:
            self.transiciones.append(trans)

        # Recalcular la clasificación del autómata
        self._actualizar_tipo()


    # =========================================================================
    # SECCIÓN 3: CLASIFICACIÓN FORMAL Y REPRESENTACIÓN TABULAR
    # =========================================================================

    def _actualizar_tipo(self) -> None:
        """
        Clasifica automáticamente el autómata analizando las transiciones registradas:
          - AFND-lambda: Si posee al menos una transición nula.
          - AFND: Si no tiene transiciones lambda pero existen bifurcaciones (|delta(q, a)| > 1).
          - AFD: Si para cada par (q, a) existe como máximo una transición y no hay lambdas.
        """
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
        Retorna la representación tabular estándar de la función de transición delta:
        { estado_origen: { simbolo: {estados_destino} } }
        """
        tabla: Dict[str, Dict[str, Set[str]]] = {q: {} for q in self.estados}
        for t in self.transiciones:
            if t.simbolo not in tabla[t.origen]:
                tabla[t.origen][t.simbolo] = set()
            tabla[t.origen][t.simbolo].add(t.destino)
        return tabla

    def es_determinista(self) -> Tuple[bool, str]:
        """
        Verifica formalmente si el autómata cumple estrictamente los axiomas de un AFD:
          1. delta no contiene ninguna transición nula (lambda / épsilon).
          2. Para cada estado q in Q y cada símbolo a in Sigma, existe como máximo
             un estado sucesor delta(q, a).
             
        Retorna:
            (es_determinado: bool, justificacion: str)
        """
        for t in self.transiciones:
            if t.es_lambda():
                return False, f"Contiene transición lambda desde '{t.origen}' hacia '{t.destino}'."

        tabla = self.obtener_tabla_transiciones()
        for est, trans_dict in tabla.items():
            for simb, dests in trans_dict.items():
                if len(dests) > 1:
                    return False, f"El estado '{est}' tiene transiciones múltiples para el símbolo '{simb}': {sorted(list(dests))}."

        return True, "El autómata es determinista (AFD)."


    # =========================================================================
    # SECCIÓN 4: ALGORITMOS DE CLAUSURA LAMBDA Y FUNCIÓN MOVER
    # =========================================================================

    def clausura_lambda(self, conjunto_estados: Set[str]) -> Set[str]:
        """
        Calcula la lambda-clausura (cerradura épsilon) reflexiva y transitiva
        de un conjunto de estados S subseteq Q:
        
        Definición formal:
            lambda-cl(S) = S union { q' in Q | existe camino q ->* q' etiquetado con lambda }
            
        Parámetros:
            conjunto_estados (Set[str]): Conjunto de estados iniciales S.
            
        Retorna:
            Set[str]: Conjunto completo de estados alcanzables mediante transiciones lambda.
        """
        clausura = set(conjunto_estados)
        cola = deque(conjunto_estados)

        # Mapa rápido de adyacencias lambda
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
        Aplica la función de transición extendida sobre un conjunto de estados:
            Delta(S, a) = Union_{q in S} delta(q, a)
            
        Parámetros:
            conjunto_estados (Set[str]): Estados fuente S.
            simbolo (str): Símbolo leído a in Sigma.
            
        Retorna:
            Set[str]: Conjunto de estados destino alcanzados en exactamente un paso.
        """
        destinos: Set[str] = set()
        for t in self.transiciones:
            if t.origen in conjunto_estados and t.simbolo == simbolo:
                destinos.add(t.destino)
        return destinos


    # =========================================================================
    # SECCIÓN 5: MOTOR DE SIMULACIÓN Y TRAZA PASO A PASO
    # =========================================================================

    def simular_cadena(self, cadena: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Simula el procesamiento formal de una cadena de entrada w in Sigma*.
        Soporta simultáneamente AFD, AFND y AFND-lambda siguiendo concurrentemente
        todas las ramas posibles y preservando la traza completa de ejecución
        (Sección 3.3 de la especificación).
        
        Parámetros:
            cadena (str): Cadena de entrada a evaluar ('' para la cadena vacía lambda).
            
        Retorna:
            (aceptada: bool, traza: List[Dict[str, Any]])
            
        Estructura de cada paso en la traza:
            {
                "paso": int,
                "simbolo_leido": Optional[str],
                "estados_previos": List[str],
                "clausura_previa": List[str],
                "transiciones_tomadas": List[Dict[str, str]],
                "estados_posteriores": List[str],
                "clausura_posterior": List[str],
                "es_aceptacion": bool,
                "error": Optional[str]
            }
        """
        traza: List[Dict[str, Any]] = []

        if not self.estado_inicial:
            return False, [{"error": "El autómata no tiene estado inicial definido."}]

        # Paso 0: Estado inicial y cálculo de su lambda-clausura reflexiva/transitiva
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

        # Procesamiento secuencial símbolo por símbolo de la cadena
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
                # Se agotaron todas las ramas posibles (camino sin salida / bloqueo)
                break

        aceptada = any(q in self.estados_aceptacion for q in activos)
        return aceptada, traza


    # =========================================================================
    # SECCIÓN 6: VALIDACIÓN DE CONSISTENCIA FORMAL
    # =========================================================================

    def validar_consistencia(self) -> Tuple[bool, List[str]]:
        """
        Verifica que los cinco componentes de la quíntupla M = (Q, Sigma, delta, q0, F)
        sean matemáticamente válidos y congruentes entre sí.
        
        Retorna:
            (es_consistente: bool, errores: List[str])
        """
        errores: List[str] = []

        if not self.estados:
            errores.append("El conjunto de estados Q está vacío.")

        if not self.estado_inicial:
            errores.append("No se ha definido el estado inicial q0.")
        elif self.estado_inicial not in self.estados:
            errores.append(f"El estado inicial '{self.estado_inicial}' no pertenece al conjunto Q.")

        for f in self.estados_aceptacion:
            if f not in self.estados:
                errores.append(f"El estado de aceptación '{f}' no pertenece al conjunto Q.")

        for t in self.transiciones:
            if t.origen not in self.estados:
                errores.append(f"Transición con origen inválido '{t.origen}'.")
            if t.destino not in self.estados:
                errores.append(f"Transición con destino inválido '{t.destino}'.")
            if t.simbolo != "" and t.simbolo not in self.alfabeto:
                errores.append(f"Transición con símbolo '{t.simbolo}' que no pertenece al alfabeto Sigma.")

        return len(errores) == 0, errores
