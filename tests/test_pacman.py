"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS: AUTÓMATA EXTENDIDO DE PAC-MAN (EJERCICIO 5)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Verifica el autómata finito determinista extendido que modela el
    comportamiento de los fantasmas de Pac-Man (Gribkoff 2013, Figura 3),
    ampliado con dos estados y dos eventos adicionales (Sección 5.1 y 5.2):
      - 6 estados: Scatter, Chase, Frightened, Eaten, Ambush (+), Rage (+)
      - Estado inicial: Scatter
      - Estados de aceptación: {Chase, Ambush, Rage} (estados letales / de caza)
      - Validación de las 10 cadenas de prueba obligatorias (5 válidas, 5 inválidas).
===============================================================================
"""

import os
import pytest
from formatos import FormatosAutomata


# =============================================================================
# FIXTURE: CARGA DEL AUTÓMATA .JFF MODELADO EN JFLAP
# =============================================================================

@pytest.fixture
def automata_pacman():
    """Carga el modelo formal del Ejercicio 5 desde el archivo JFF oficial."""
    ruta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "automatas",
        "aplicacion",
        "pacman_extended.jff"
    )
    return FormatosAutomata.cargar_jff(ruta)


# =============================================================================
# SECCIÓN 1: VALIDACIÓN ESTRUCTURAL DE LA QUÍNTUPLA
# =============================================================================

def test_estructura_pacman(automata_pacman):
    """Comprueba que el modelo tenga exactamente 6 estados y la quíntupla esperada."""
    estados_esperados = {"Scatter", "Chase", "Frightened", "Eaten", "Ambush", "Rage"}
    assert automata_pacman.estados == estados_esperados
    assert automata_pacman.estado_inicial == "Scatter"
    assert automata_pacman.estados_aceptacion == {"Chase", "Ambush", "Rage"}


# =============================================================================
# SECCIÓN 2: SIMULACIÓN DE LAS 10 CADENAS OBLIGATORIAS (EJERCICIO 5.2)
# =============================================================================

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
    """Evalúa las diez cadenas de prueba documentadas en docs/05-del-articulo-al-automata.md."""
    obtenido, traza = automata_pacman.simular_cadena(cadena)
    assert obtenido == esperado, (
        f"Fallo en '{cadena}': esperado {esperado}, obtenido {obtenido}. "
        f"Descripción: {descripcion}. Traza: {traza}"
    )
