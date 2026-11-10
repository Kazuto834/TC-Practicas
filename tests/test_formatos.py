"""
Pruebas Unitarias para Serialización Multiformato de Autómatas.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
"""

import os
import tempfile
import pytest
from automata import Automata
from formatos import FormatosAutomata


@pytest.fixture
def automata_ejemplo_anexo3():
    """Autómata AFND-lambda del Anexo 3 de las instrucciones de Práctica 2."""
    auto = Automata()
    auto.agregar_estado("q0", es_inicial=True, es_final=False, pos_x=80.0, pos_y=120.0)
    auto.agregar_estado("q1", es_inicial=False, es_final=True, pos_x=240.0, pos_y=120.0)
    auto.agregar_transicion("q0", "a", "q1")
    auto.agregar_transicion("q0", "b", "q0")
    auto.agregar_transicion("q0", "", "q1")
    return auto


def test_roundtrip_jff(automata_ejemplo_anexo3):
    """Comprueba que guardar y recargar en .jff preserva exactamente la quíntupla."""
    with tempfile.NamedTemporaryFile(suffix=".jff", delete=False) as f:
        temp_path = f.name

    try:
        FormatosAutomata.guardar_jff(automata_ejemplo_anexo3, temp_path)
        auto_recuperado = FormatosAutomata.cargar_jff(temp_path)

        assert auto_recuperado.estados == automata_ejemplo_anexo3.estados
        assert auto_recuperado.estado_inicial == automata_ejemplo_anexo3.estado_inicial
        assert auto_recuperado.estados_aceptacion == automata_ejemplo_anexo3.estados_aceptacion
        assert auto_recuperado.alfabeto == automata_ejemplo_anexo3.alfabeto
        assert len(auto_recuperado.transiciones) == len(automata_ejemplo_anexo3.transiciones)
        assert auto_recuperado.tipo == "AFND-lambda"

        # Simulación debe dar los mismos resultados
        assert auto_recuperado.simular_cadena("b")[0] == automata_ejemplo_anexo3.simular_cadena("b")[0]
        assert auto_recuperado.simular_cadena("ba")[0] == automata_ejemplo_anexo3.simular_cadena("ba")[0]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_roundtrip_json(automata_ejemplo_anexo3):
    """Comprueba que guardar y recargar en .json preserva la quíntupla."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        FormatosAutomata.guardar_json(automata_ejemplo_anexo3, temp_path)
        auto_recuperado = FormatosAutomata.cargar_json(temp_path)

        assert auto_recuperado.estados == automata_ejemplo_anexo3.estados
        assert auto_recuperado.estado_inicial == automata_ejemplo_anexo3.estado_inicial
        assert auto_recuperado.estados_aceptacion == automata_ejemplo_anexo3.estados_aceptacion
        assert auto_recuperado.alfabeto == automata_ejemplo_anexo3.alfabeto
        assert len(auto_recuperado.transiciones) == len(automata_ejemplo_anexo3.transiciones)
        assert auto_recuperado.tipo == "AFND-lambda"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_roundtrip_xml(automata_ejemplo_anexo3):
    """Comprueba que guardar y recargar en .xml canónico preserva la quíntupla."""
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        temp_path = f.name

    try:
        FormatosAutomata.guardar_xml(automata_ejemplo_anexo3, temp_path)
        auto_recuperado = FormatosAutomata.cargar_xml(temp_path)

        assert auto_recuperado.estados == automata_ejemplo_anexo3.estados
        assert auto_recuperado.estado_inicial == automata_ejemplo_anexo3.estado_inicial
        assert auto_recuperado.estados_aceptacion == automata_ejemplo_anexo3.estados_aceptacion
        assert auto_recuperado.alfabeto == automata_ejemplo_anexo3.alfabeto
        assert len(auto_recuperado.transiciones) == len(automata_ejemplo_anexo3.transiciones)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
