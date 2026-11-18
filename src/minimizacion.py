"""
Módulo Fachada para Minimización y Equivalencia de AFD (Práctica 3).

Reexporta de forma modular las funciones de eliminación de estados inaccesibles,
minimización por refinamiento de particiones y decisión de equivalencia.
"""

from __future__ import annotations
from eliminacion_inaccesibles import eliminar_estados_inaccesibles, eliminar_estados_inaccesibles_detallado
from minimizacion_afd import minimizar_afd, minimizar_afd_detallado
from equivalencia_afd import son_equivalentes, decidir_equivalencia_detallada

__all__ = [
    "eliminar_estados_inaccesibles",
    "eliminar_estados_inaccesibles_detallado",
    "minimizar_afd",
    "minimizar_afd_detallado",
    "son_equivalentes",
    "decidir_equivalencia_detallada"
]

