"""
Pruebas Unitarias para el Autómata Extendido de Pac-Man (Ejercicio 5).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
"""

import os
import pytest
from formatos import FormatosAutomata


@pytest.fixture
def automata_pacman():
    ruta = os.path.join(os.path.dirname(__file__), "..", "automatas", "aplicacion", "pacman_extended.jff")
    return FormatosAutomata.cargar_jff(ruta)


def test_estructura_pacman(automata_pacman):
    """Comprueba que el modelo tenga 6 estados y eventos esperados."""
    estados_esperados = {"Scatter", "Chase", "Frightened", "Eaten", "Ambush", "Rage"}
    assert automata_pacman.estados == estados_esperados
    assert automata_pacman.estado_inicial == "Scatter"
    assert automata_pacman.estados_aceptacion == {"Chase", "Ambush", "Rage"}


@pytest.mark.parametrize("cadena,esperado,descripcion", [
    ("t", True, "Scatter -> Chase (letal)"),
    ("tf", True, "Scatter -> Chase -> Ambush (flanqueo letal)"),
    ("p", False, "Scatter -> Frightened (azul/vulnerable)"),
    ("pch", False, "Scatter -> Frightened -> Eaten -> Scatter (reiniciando)"),
    ("pcht", True, "Scatter -> Frightened -> Eaten -> Scatter -> Chase (recupera ataque)"),
    ("r", True, "Scatter -> Rage (modo furia/letal)"),
    ("rt", True, "Scatter -> Rage -> Chase (letal)"),
    ("rp", False, "Scatter -> Rage -> Frightened (pacman toma power pellet)"),
    ("pt", True, "Scatter -> Frightened -> Chase (termina tiempo vulnerable)"),
    ("f", True, "Scatter -> Ambush (flanqueo directo letal)")
])
def test_simulacion_pacman(automata_pacman, cadena, esperado, descripcion):
    """Prueba las 10 cadenas obligatorias del Ejercicio 5."""
    obtenido, traza = automata_pacman.simular_cadena(cadena)
    assert obtenido == esperado, f"Fallo en {cadena}: esperado {esperado}, obtenido {obtenido}. Traza: {traza}"
