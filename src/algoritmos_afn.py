"""
Módulo Fachada para Algoritmos de Autómatas No Deterministas (Práctica 3).

Reexporta de forma modular las funciones de cálculo de cerradura lambda,
simulación directa, eliminación de transiciones lambda y construcción de subconjuntos.
"""

from __future__ import annotations
from cerradura_lambda import calcular_cerradura_lambda
from simulacion_directa import simular_afn_lambda_directo
from eliminacion_lambda import eliminar_transiciones_lambda, transformar_afn_sin_lambda_detallado
from construccion_subconjuntos import construccion_subconjuntos, construccion_subconjuntos_detallada

__all__ = [
    "calcular_cerradura_lambda",
    "simular_afn_lambda_directo",
    "eliminar_transiciones_lambda",
    "transformar_afn_sin_lambda_detallado",
    "construccion_subconjuntos",
    "construccion_subconjuntos_detallada"
]

