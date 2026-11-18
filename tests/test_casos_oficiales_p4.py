import pytest
import sys
import os

# Asegurar que src está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from er_a_automata import er_a_afnd_lambda, er_a_afd_minimo
from formatos import FormatosAutomata
from automata_a_er import automata_a_expresion_regular
from equivalencia_afd import son_equivalentes


# =====================================================================
# EJERCICIO 2: Casos de Expresión Regular a Autómata (Teorema de Kleene I)
# =====================================================================

CASOS_EJERCICIO_2 = [
    ("241", "0(0+1)*0", ["00", "010"], ["", "1", "01"]),
    ("242", "(0+1)*01(0+1)*", ["01", "1010"], ["", "0", "11"]),
    ("243", "(0+1)*11", ["11", "011"], ["", "1", "10"]),
    ("244", "1*(01*01*)*", ["", "11", "00", "10101"], ["0", "10", "101"]),
    ("245", "0*10*10*", ["11", "01010"], ["", "1", "00"]),
    ("246", "(0+1)(0+1)(0+1)*", ["00", "010"], ["", "0", "1"]),
    ("247", "λ+0+1+(0+1)(0+1)", ["", "0", "1", "00", "11"], ["000", "0101"]),
    ("248", "(a+b)*ab(a+b)*", ["ab", "aab", "baba"], ["", "a", "b", "baa"]),
    ("249", "a*ba*ba*", ["bb", "abba"], ["", "a", "b", "aba", "aabaa"]),
    ("250", "(00+11)*", ["", "00", "11", "001100"], ["0", "1", "01", "001"]),
    ("251", "(0+10)*", ["", "0", "10", "010"], ["1", "01", "11"]),
    ("252", "10+(0+11)0*1", ["10", "01", "1101"], ["", "0", "11"]),
    ("253", "(a+b)*(aa+bb)(a+b)*", ["aa", "bb", "aabba"], ["", "a", "b", "aba"]),
    ("272a", "a+b*", ["a", "", "b", "bb"], ["ab", "ba"]),
    ("272b", "(ab)*", ["", "ab", "abab"], ["a", "b", "aba"]),
    ("272c", "a*b*", ["", "a", "b", "aabb", "aa", "bb"], ["ababa", "ba"]),
    ("273", "(0+1)*001(0+1)*", ["001", "10010"], ["", "01", "00"]),
    ("278", "(a+b)*b", ["b", "ab", "aab"], ["", "a", "ba"]),
]


@pytest.mark.parametrize("id_caso, expresion, validas, invalidas", CASOS_EJERCICIO_2)
def test_er_a_automata_oficiales(id_caso, expresion, validas, invalidas):
    """
    Verifica que cada expresión regular compile correctamente a AFND-lambda
    y AFD mínimo, cumpliendo con las simulaciones de cadenas.
    """
    # 1. Compilación a AFND-lambda
    afnd = er_a_afnd_lambda(expresion)
    assert afnd is not None
    assert len(afnd.estados) > 0
    assert afnd.estado_inicial is not None
    assert len(afnd.estados_aceptacion) > 0

    # 2. Compilación a AFD Mínimo
    afd = er_a_afd_minimo(expresion)
    assert afd is not None
    assert len(afd.estados) > 0
    assert afd.estado_inicial is not None
    assert len(afd.estados_aceptacion) > 0

    # Verificar que el AFD resultante es verdaderamente determinista
    es_det, motivo = afd.es_determinista()
    assert es_det is True, f"El AFD para {id_caso} ({expresion}) no es determinista: {motivo}"

    # 3. Simulación de cadenas válidas
    for cadena in validas:
        res, _ = afd.simular_cadena(cadena)
        assert res is True, f"Cadena válida '{cadena}' rechazada por AFD ({id_caso}: {expresion})"

    # 4. Simulación de cadenas inválidas
    for cadena in invalidas:
        res, _ = afd.simular_cadena(cadena)
        assert res is False, f"Cadena inválida '{cadena}' aceptada indebidamente por AFD ({id_caso}: {expresion})"


# =====================================================================
# EJERCICIO 3: Casos de Autómata a Expresión Regular (GNFA / Kleene II)
# =====================================================================

AUTOMATAS_PRACTICA_3 = [
    ("131", "../automatas/practica3/afd-a-er/131.jff"),
    ("137", "../automatas/practica3/afd-a-er/137.jff"),
    ("139", "../automatas/practica3/afd-a-er/139.jff"),
    ("254", "../automatas/practica3/afd-a-er/254.jff"),
    ("255", "../automatas/practica3/afd-a-er/255.jff"),
]


@pytest.mark.parametrize("id_caso, ruta_rel", AUTOMATAS_PRACTICA_3)
def test_automata_a_er_oficiales(id_caso, ruta_rel):
    """
    Carga los autómatas de Práctica 3, verifica que sean deterministas,
    los convierte a ER mediante GNFA, verifica que la ER no sea vacía,
    recompila la ER y comprueba equivalencia con el autómata original.
    """
    ruta_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), ruta_rel))
    assert os.path.exists(ruta_abs), f"No se encuentra el archivo {ruta_abs}"

    # 1. Cargar autómata
    auto_original = FormatosAutomata.cargar_jff(ruta_abs)
    assert auto_original is not None

    # 2. Verificar que sea determinista
    es_det, motivo = auto_original.es_determinista()
    assert es_det is True, f"El autómata {id_caso} no es determinista: {motivo}"

    # 3. Convertir a Expresión Regular
    resultado = automata_a_expresion_regular(auto_original)
    if isinstance(resultado, tuple):
        er_resultante = resultado[0]
    else:
        er_resultante = resultado

    assert er_resultante is not None
    assert isinstance(er_resultante, str)
    assert len(er_resultante.strip()) > 0, f"La ER para {id_caso} está vacía"

    # 4. Recompilar ER a AFD Mínimo
    auto_recompilado = er_a_afd_minimo(er_resultante)
    assert auto_recompilado is not None

    # 5. Comprobar equivalencia
    eq, _ = son_equivalentes(auto_original, auto_recompilado)
    assert eq is True, f"El autómata original {id_caso} y el recompilado desde ER '{er_resultante}' no son equivalentes"


# Casos sintéticos adicionales para 256, 257, 258, 276 y 277
CASOS_SINTETICOS_ER = [
    ("256", "0*1*"),
    ("257", "(0+1)*00(0+1)*"),
    ("258", "0(0+1)* + (0+1)*1"),
    ("277", "(0*1*)*"),
]


@pytest.mark.parametrize("id_caso, expresion", CASOS_SINTETICOS_ER)
def test_casos_sinteticos_er_a_afd(id_caso, expresion):
    """
    Valida la conversión y re-equivalencia para casos sintéticos adicionales
    pedidos en la Práctica 4 (256, 257, 258, 277).
    """
    afd = er_a_afd_minimo(expresion)
    assert afd is not None
    es_det, _ = afd.es_determinista()
    assert es_det is True

    # Convertir el AFD resultante de vuelta a ER y verificar ciclo completo
    resultado = automata_a_expresion_regular(afd)
    er_vuelta = resultado[0] if isinstance(resultado, tuple) else resultado
    assert len(er_vuelta.strip()) > 0

    afd_vuelta = er_a_afd_minimo(er_vuelta)
    eq, _ = son_equivalentes(afd, afd_vuelta)
    assert eq is True


def test_caso_sintetico_276():
    """Caso especial 276: ((0+1)(0+1))*"""
    afd = er_a_afd_minimo("((0+1)(0+1))*")
    assert afd.simular_cadena("")[0] is True
    assert afd.simular_cadena("01")[0] is True
    assert afd.simular_cadena("0101")[0] is True
    assert afd.simular_cadena("0")[0] is False
    assert afd.simular_cadena("010")[0] is False
