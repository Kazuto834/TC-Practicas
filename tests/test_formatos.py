"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS: SERIALIZACIÓN MULTIFORMATO (.JFF, .JSON, .XML)
===============================================================================
Unidad de Aprendizaje: Teoría de la Computación (ESCOM - IPN)
Autores: Antonio Navarro Domínguez & Mario García Castillo

Descripción:
    Verifica los requisitos del Ejercicio 3.2, 3.4 y 3.5:
      - Exportación e importación de un mismo autómata en los tres formatos
        (.jff de JFLAP, .json estructurado y .xml canónico).
      - Demostración de que la exportación e importación son operaciones inversas.
      - Preservación de la quíntupla formal M = (Q, Sigma, delta, q0, F) en ciclos
        completos de conversión cruzada.
      - Validación de la convención de transiciones lambda (cadena vacía '')
        según el Anexo 3.
===============================================================================
"""

import os
import tempfile
import pytest
from automata import Automata
from formatos import FormatosAutomata


# =============================================================================
# FIXTURE: AUTÓMATAS DE REFERENCIA SEGÚN ANEXO 3
# =============================================================================

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


# =============================================================================
# SECCIÓN 1: OPERACIONES INVERSAS (ROUNDTRIP) EN LOS TRES FORMATOS (3.5)
# =============================================================================

def test_roundtrip_jff(automata_ejemplo_anexo3):
    """
    Comprueba que guardar y recargar en .jff preserva exactamente la quíntupla
    y que la exportación e importación son operaciones inversas (Requisito 3.5).
    """
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

        # Simulación debe arrojar exactamente el mismo resultado
        assert auto_recuperado.simular_cadena("b")[0] == automata_ejemplo_anexo3.simular_cadena("b")[0]
        assert auto_recuperado.simular_cadena("ba")[0] == automata_ejemplo_anexo3.simular_cadena("ba")[0]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_roundtrip_json(automata_ejemplo_anexo3):
    """
    Comprueba que guardar y recargar en .json preserva la quíntupla
    y que ambas operaciones son formalmente inversas (Requisito 3.5).
    """
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
    """
    Comprueba que guardar y recargar en .xml canónico preserva la quíntupla
    y que ambas operaciones son formalmente inversas (Requisito 3.5).
    """
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


# =============================================================================
# SECCIÓN 2: CONVERSIÓN CRUZADA CICLO COMPLETO (JFF -> JSON -> XML -> JFF)
# =============================================================================

def test_conversion_cruzada_formatos(automata_ejemplo_anexo3):
    """
    Comprueba que la conversión en ciclo JFF -> JSON -> XML -> JFF
    preserve invariante la quíntupla y la simulación de cadenas.
    """
    with tempfile.NamedTemporaryFile(suffix=".jff", delete=False) as f_jff1, \
         tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_json, \
         tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f_xml, \
         tempfile.NamedTemporaryFile(suffix=".jff", delete=False) as f_jff2:
        path_jff1 = f_jff1.name
        path_json = f_json.name
        path_xml = f_xml.name
        path_jff2 = f_jff2.name

    try:
        # 1. Exportar a JFF
        FormatosAutomata.guardar_jff(automata_ejemplo_anexo3, path_jff1)
        auto_desde_jff = FormatosAutomata.cargar_jff(path_jff1)

        # 2. Exportar de JFF a JSON
        FormatosAutomata.guardar_json(auto_desde_jff, path_json)
        auto_desde_json = FormatosAutomata.cargar_json(path_json)

        # 3. Exportar de JSON a XML
        FormatosAutomata.guardar_xml(auto_desde_json, path_xml)
        auto_desde_xml = FormatosAutomata.cargar_xml(path_xml)

        # 4. Exportar de XML a JFF
        FormatosAutomata.guardar_jff(auto_desde_xml, path_jff2)
        auto_final = FormatosAutomata.cargar_jff(path_jff2)

        # Validar consistencia en todas las etapas
        for auto_eval in (auto_desde_jff, auto_desde_json, auto_desde_xml, auto_final):
            assert auto_eval.estados == automata_ejemplo_anexo3.estados
            assert auto_eval.estado_inicial == automata_ejemplo_anexo3.estado_inicial
            assert auto_eval.estados_aceptacion == automata_ejemplo_anexo3.estados_aceptacion
            assert auto_eval.alfabeto == automata_ejemplo_anexo3.alfabeto
            assert len(auto_eval.transiciones) == len(automata_ejemplo_anexo3.transiciones)

            for cadena in ("", "b", "a", "ba", "bba", "bbba", "aa"):
                res_orig, _ = automata_ejemplo_anexo3.simular_cadena(cadena)
                res_eval, _ = auto_eval.simular_cadena(cadena)
                assert res_eval == res_orig

    finally:
        for p in (path_jff1, path_json, path_xml, path_jff2):
            if os.path.exists(p):
                os.remove(p)


# =============================================================================
# SECCIÓN 3: VERIFICACIÓN DE CONVENCIONES DEL ANEXO 3 PARA LAMBDA (λ)
# =============================================================================

def test_verificacion_anexo3_elementos_lambda(automata_ejemplo_anexo3):
    """
    Verifica que la serialización de lambda cumpla explícitamente con las
    convenciones del Anexo 3:
      - JFF : elemento <read/> vacío
      - JSON: "lee": ""
      - XML : lee=""
    """
    with tempfile.NamedTemporaryFile(suffix=".jff", delete=False) as f_jff, \
         tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_json, \
         tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f_xml:
        path_jff = f_jff.name
        path_json = f_json.name
        path_xml = f_xml.name

    try:
        FormatosAutomata.guardar_jff(automata_ejemplo_anexo3, path_jff)
        FormatosAutomata.guardar_json(automata_ejemplo_anexo3, path_json)
        FormatosAutomata.guardar_xml(automata_ejemplo_anexo3, path_xml)

        with open(path_jff, "r", encoding="utf-8") as f:
            contenido_jff = f.read()
            assert any(tag in contenido_jff for tag in ("<read/>", "<read />", "<read></read>"))

        with open(path_json, "r", encoding="utf-8") as f:
            contenido_json = f.read()
            assert '"lee": ""' in contenido_json

        with open(path_xml, "r", encoding="utf-8") as f:
            contenido_xml = f.read()
            assert 'lee=""' in contenido_xml
    finally:
        for p in (path_jff, path_json, path_xml):
            if os.path.exists(p):
                os.remove(p)


def test_carga_directa_desde_cadenas():
    """Verifica la carga directa desde cadenas JSON y XML en memoria."""
    json_str = '{"alfabeto": ["0"], "estados": ["q0"], "inicial": "q0", "aceptacion": ["q0"], "transiciones": []}'
    auto_json = FormatosAutomata.cargar_json(json_str)
    assert auto_json.estados == {"q0"}
    assert auto_json.estado_inicial == "q0"

    xml_str = '<automata tipo="AFD"><alfabeto><simbolo>0</simbolo></alfabeto><estados><estado nombre="q0" inicial="true" aceptacion="true"/></estados><transiciones/></automata>'
    auto_xml = FormatosAutomata.cargar_xml(xml_str)
    assert auto_xml.estados == {"q0"}
    assert auto_xml.estado_inicial == "q0"
