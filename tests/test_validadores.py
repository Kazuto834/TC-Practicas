"""
Test suite para el módulo validadores.py – Práctica 4
Teoría de la Computación, ESCOM-IPN

Valida los tres validadores (Email, Teléfono México, URL):
  - Cadenas válidas e inválidas conocidas
  - Generadores de cadenas válidas e inválidas (≥170 cada uno)
  - Congruencia 100 % entre clasificación y re.fullmatch
  - Integridad del catálogo (3 validadores, campos obligatorios)
"""

import re
import sys
import os

import pytest

# ── hacer visible el paquete src ──────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from validadores import (
    Validador,
    obtener_todos_los_validadores,
    ejecutar_validacion_completa,
)


# ======================================================================
# Helpers
# ======================================================================

def _validador_por_nombre(nombre_fragmento: str) -> Validador:
    """Devuelve el primer validador cuyo nombre contenga *nombre_fragmento*
    (búsqueda case-insensitive)."""
    for v in obtener_todos_los_validadores():
        if nombre_fragmento.lower() in v.nombre.lower():
            return v
    raise ValueError(f"No se encontró un validador con «{nombre_fragmento}»")


# ======================================================================
# Email
# ======================================================================

class TestValidadorEmail:
    """Pruebas para el validador de correo electrónico."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.v = _validador_por_nombre("mail")

    # ── cadenas válidas conocidas ─────────────────────────────────────
    @pytest.mark.parametrize("email", [
        "user@domain.com",
        "user.name@domain.co.mx",
        "user_name@sub.domain.org",
        "user-name@domain.com",
        "user123@domain.com",
        "u@domain.com",
        "user@123.123.123.com",
        "user@domain.co",
        "user.name+tag@domain.com",
        "user@my-domain.com",
        "firstname.lastname@domain.com",
        "email@subdomain.domain.com",
        "1234567890@domain.com",
        "email@domain-one.com",
        "_______@domain.com",
    ])
    def test_emails_validos_basicos(self, email: str):
        """Correos válidos conocidos deben hacer match con er_python."""
        assert re.fullmatch(self.v.er_python, email), (
            f"Se esperaba que «{email}» fuera válido"
        )

    # ── cadenas inválidas conocidas ───────────────────────────────────
    @pytest.mark.parametrize("email", [
        "@domain.com",
        "user@",
        "user@.com",
        "user@domain",
        "user@@domain.com",
        "user @domain.com",
        "user@domain..com",
        ".user@domain.com",
        "user.@domain.com",
        "user@-domain.com",
        "user@domain.c",
        "",
        "plainaddress",
        "user@domain,com",
        "@",
    ])
    def test_emails_invalidos_basicos(self, email: str):
        """Correos inválidos conocidos NO deben hacer match con er_python."""
        assert not re.fullmatch(self.v.er_python, email), (
            f"Se esperaba que «{email}» fuera inválido"
        )

    # ── generador de válidos ──────────────────────────────────────────
    def test_generador_emails_validos(self):
        """generar_validas() debe devolver ≥170 cadenas, todas aceptadas."""
        validas = self.v.generar_validas()
        assert len(validas) >= 170, (
            f"Se esperaban ≥170 cadenas válidas, se obtuvieron {len(validas)}"
        )
        for s in validas:
            assert re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente válida no hace match: «{s}»"
            )

    # ── generador de inválidos ────────────────────────────────────────
    def test_generador_emails_invalidos(self):
        """generar_invalidas() debe devolver ≥170 cadenas, ninguna aceptada."""
        invalidas = self.v.generar_invalidas()
        assert len(invalidas) >= 170, (
            f"Se esperaban ≥170 cadenas inválidas, se obtuvieron {len(invalidas)}"
        )
        for s in invalidas:
            assert not re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente inválida sí hace match: «{s}»"
            )


# ======================================================================
# Teléfono México
# ======================================================================

class TestValidadorTelefono:
    """Pruebas para el validador de números telefónicos de México."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.v = _validador_por_nombre("fono")  # Teléfono

    # ── cadenas válidas conocidas ─────────────────────────────────────
    @pytest.mark.parametrize("tel", [
        "5512345678",
        "55 1234 5678",
        "+52 55 1234 5678",
        "52 55 1234 5678",
        "+521 55 1234 5678",
        "55-1234-5678",
        "+52-55-1234-5678",
        "9981234567",
        "33 1234 5678",
        "81 1234 5678",
    ])
    def test_telefonos_validos_basicos(self, tel: str):
        """Números telefónicos válidos conocidos deben hacer match."""
        assert re.fullmatch(self.v.er_python, tel), (
            f"Se esperaba que «{tel}» fuera válido"
        )

    # ── cadenas inválidas conocidas ───────────────────────────────────
    @pytest.mark.parametrize("tel", [
        "123",
        "abcdefghij",
        "123456789012345",
        "",
        "+99 55 1234 5678",
        "55 1234",
        "12345",
        "+52",
        "0000000000",
        "55+1234-5678",
    ])
    def test_telefonos_invalidos_basicos(self, tel: str):
        """Números telefónicos inválidos conocidos NO deben hacer match."""
        assert not re.fullmatch(self.v.er_python, tel), (
            f"Se esperaba que «{tel}» fuera inválido"
        )

    # ── generador de válidos ──────────────────────────────────────────
    def test_generador_telefonos_validos(self):
        """generar_validas() debe devolver ≥170 cadenas, todas aceptadas."""
        validas = self.v.generar_validas()
        assert len(validas) >= 170, (
            f"Se esperaban ≥170 cadenas válidas, se obtuvieron {len(validas)}"
        )
        for s in validas:
            assert re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente válida no hace match: «{s}»"
            )

    # ── generador de inválidos ────────────────────────────────────────
    def test_generador_telefonos_invalidos(self):
        """generar_invalidas() debe devolver ≥170 cadenas, ninguna aceptada."""
        invalidas = self.v.generar_invalidas()
        assert len(invalidas) >= 170, (
            f"Se esperaban ≥170 cadenas inválidas, se obtuvieron {len(invalidas)}"
        )
        for s in invalidas:
            assert not re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente inválida sí hace match: «{s}»"
            )


# ======================================================================
# URL
# ======================================================================

class TestValidadorURL:
    """Pruebas para el validador de URLs."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.v = _validador_por_nombre("url")  # URL

    # ── cadenas válidas conocidas ─────────────────────────────────────
    @pytest.mark.parametrize("url", [
        "http://example.com",
        "https://example.com",
        "https://sub.domain.com/path",
        "http://example.com/path/to/page",
        "https://example.com/path?query=value",
        "https://example.com/path#fragment",
        "https://example.com:8080",
        "http://www.example.com",
        "https://example.co.mx/ruta",
        "https://my-site.org/page",
    ])
    def test_urls_validas_basicas(self, url: str):
        """URLs válidas conocidas deben hacer match."""
        assert re.fullmatch(self.v.er_python, url), (
            f"Se esperaba que «{url}» fuera válida"
        )

    # ── cadenas inválidas conocidas ───────────────────────────────────
    @pytest.mark.parametrize("url", [
        "ftp://example.com",
        "://example.com",
        "http://",
        "https://",
        "http//example.com",
        "example.com",
        "",
        "http:// example.com",
        "http://example",
        "just-text",
    ])
    def test_urls_invalidas_basicas(self, url: str):
        """URLs inválidas conocidas NO deben hacer match."""
        assert not re.fullmatch(self.v.er_python, url), (
            f"Se esperaba que «{url}» fuera inválida"
        )

    # ── generador de válidos ──────────────────────────────────────────
    def test_generador_urls_validas(self):
        """generar_validas() debe devolver ≥170 cadenas, todas aceptadas."""
        validas = self.v.generar_validas()
        assert len(validas) >= 170, (
            f"Se esperaban ≥170 cadenas válidas, se obtuvieron {len(validas)}"
        )
        for s in validas:
            assert re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente válida no hace match: «{s}»"
            )

    # ── generador de inválidos ────────────────────────────────────────
    def test_generador_urls_invalidas(self):
        """generar_invalidas() debe devolver ≥170 cadenas, ninguna aceptada."""
        invalidas = self.v.generar_invalidas()
        assert len(invalidas) >= 170, (
            f"Se esperaban ≥170 cadenas inválidas, se obtuvieron {len(invalidas)}"
        )
        for s in invalidas:
            assert not re.fullmatch(self.v.er_python, s), (
                f"Cadena supuestamente inválida sí hace match: «{s}»"
            )


# ======================================================================
# Congruencia completa (prueba clave)
# ======================================================================

class TestCongruenciaCompleta:
    """Verifica congruencia al 100 % entre clasificación y re.fullmatch
    para cada validador, usando al menos 500 cadenas en total."""

    def test_congruencia_500_cadenas_por_validador(self):
        """Para cada validador, la suma de cadenas válidas + inválidas debe
        ser ≥500 y re.fullmatch debe coincidir con la clasificación esperada
        para TODAS las cadenas."""
        for v in obtener_todos_los_validadores():
            validas = v.generar_validas()
            invalidas = v.generar_invalidas()
            total = len(validas) + len(invalidas)

            assert total >= 500, (
                f"[{v.nombre}] Se esperaban ≥500 cadenas en total, "
                f"se obtuvieron {total} ({len(validas)} válidas + "
                f"{len(invalidas)} inválidas)"
            )

            # Verificar válidas
            for s in validas:
                assert re.fullmatch(v.er_python, s), (
                    f"[{v.nombre}] Cadena clasificada como válida NO hace "
                    f"match: «{s}»"
                )

            # Verificar inválidas
            for s in invalidas:
                assert not re.fullmatch(v.er_python, s), (
                    f"[{v.nombre}] Cadena clasificada como inválida SÍ hace "
                    f"match: «{s}»"
                )


# ======================================================================
# Integridad del catálogo
# ======================================================================

class TestIntegridad:
    """Verifica la integridad del catálogo de validadores."""

    def test_tres_validadores_disponibles(self):
        """obtener_todos_los_validadores() debe devolver exactamente 3."""
        validadores = obtener_todos_los_validadores()
        assert len(validadores) == 3, (
            f"Se esperaban 3 validadores, se obtuvieron {len(validadores)}"
        )

    def test_campos_obligatorios(self):
        """Cada validador debe tener nombre, descripcion, er_formal y
        er_python no vacíos."""
        for v in obtener_todos_los_validadores():
            assert v.nombre, f"Validador sin nombre: {v}"
            assert v.descripcion, f"Validador sin descripción: {v}"
            assert v.er_formal, f"[{v.nombre}] er_formal vacío"
            assert v.er_python, f"[{v.nombre}] er_python vacío"
