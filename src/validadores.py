"""
Módulo de Validadores Formales de Patrones Reales (Práctica 4).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Definición de modelos formales de expresiones regulares
                para validación de correo electrónico, teléfono nacional
                (IFT 10 dígitos) y URL web (RFC 3986), con generadores
                algorítmicos de cadenas de prueba válidas e inválidas.
"""

from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Semilla fija para reproducibilidad de las cadenas generadas
# ---------------------------------------------------------------------------
_RNG = random.Random(42)

# ==========================================================================#
#  Modelo de datos                                                          #
# ==========================================================================#


@dataclass
class Validador:
    """Modelo formal de un validador basado en expresión regular.

    Atributos
    ---------
    nombre : str
        Nombre legible del validador (p. ej. "Correo Electrónico").
    descripcion : str
        Descripción breve de lo que valida.
    er_formal : str
        Expresión regular en notación matemática del curso
        (+ = unión, * = Kleene, concatenación implícita).
    er_python : str
        Patrón equivalente compatible con ``re.fullmatch``.
    generar_validas : Callable[[], List[str]]
        Función generadora de cadenas válidas (≥ 170).
    generar_invalidas : Callable[[], List[str]]
        Función generadora de cadenas inválidas (≥ 170).
    """

    nombre: str
    descripcion: str
    er_formal: str
    er_python: str
    generar_validas: Callable[[], List[str]] = field(repr=False)
    generar_invalidas: Callable[[], List[str]] = field(repr=False)


# ==========================================================================#
#  Utilidades internas de generación                                        #
# ==========================================================================#

def _rand_str(charset: str, lo: int, hi: int) -> str:
    """Genera una cadena aleatoria con caracteres de *charset* y longitud [lo, hi]."""
    length = _RNG.randint(lo, hi)
    return "".join(_RNG.choices(charset, k=length))


def _rand_alpha_lower(lo: int = 1, hi: int = 8) -> str:
    return _rand_str(string.ascii_lowercase, lo, hi)


def _rand_alphanum_lower(lo: int = 1, hi: int = 8) -> str:
    return _rand_str(string.ascii_lowercase + string.digits, lo, hi)


def _rand_digit_str(n: int) -> str:
    return "".join(_RNG.choices(string.digits, k=n))


# ==========================================================================#
#  1. Validador de Correo Electrónico (RFC 5322 simplificado)               #
# ==========================================================================#

_EMAIL_ER_FORMAL = (
    "(a+b+c+...+z+A+B+...+Z+0+1+...+9+_+.+-)"
    "(a+b+...+z+A+...+Z+0+...+9+_+.+-)*"
    " @ "
    "(a+b+...+z+A+...+Z+0+...+9+-)"
    "(a+b+...+z+A+...+Z+0+...+9+-.)*"
    " . "
    "(a+b+...+z+A+...+Z)(a+b+...+z+A+...+Z)"
    "(a+b+...+z+A+...+Z + ε)"
    "(a+b+...+z+A+...+Z + ε)"
    "(a+b+...+z+A+...+Z + ε)"
    "(a+b+...+z+A+...+Z + ε)"
)

_EMAIL_ER_PYTHON = (
    r"[a-zA-Z0-9_+-]+(?:\.[a-zA-Z0-9_+-]+)*@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*"
    r"\.[a-zA-Z]{2,6}"
)

_TLDS = [
    "com", "mx", "net", "org", "edu", "gob", "info", "io", "dev",
    "xyz", "tech", "site", "online", "store", "club", "app", "pro",
    "biz", "name", "museum",
]

_EMAIL_LOCAL_CHARS = string.ascii_lowercase + string.digits + "_.-"


def _generar_emails_validos() -> List[str]:
    """Genera ≥ 200 direcciones de correo válidas."""
    validos: List[str] = []

    # Ejemplos fijos representativos
    fijos = [
        "usuario@dominio.com",
        "nombre.apellido@empresa.com.mx",
        "user_name@sub.dominio.org",
        "a@b.co",
        "test+tag@gmail.com",
        "u-s.e_r@my-host.info",
        "john.doe123@example.museum",
        "a1@x.io",
        "UPPER@CASE.COM",
        "MiXeD.CaSe@Test.Net",
    ]
    validos.extend(fijos)

    # Generación algorítmica
    while len(validos) < 265:
        local_len = _RNG.randint(1, 15)
        local = _rand_str(_EMAIL_LOCAL_CHARS, local_len, local_len)
        # Asegurar que empiece con alfanumérico
        if local[0] not in string.ascii_lowercase + string.digits:
            local = _RNG.choice(string.ascii_lowercase) + local[1:]
        # Evitar doble punto
        while ".." in local:
            local = local.replace("..", ".")
        # Asegurar que no termine en punto
        if local.endswith("."):
            local = local[:-1] + _RNG.choice(string.ascii_lowercase)

        num_sub = _RNG.randint(0, 2)
        domain_parts = [_rand_alphanum_lower(2, 8) for _ in range(num_sub + 1)]
        domain = ".".join(domain_parts)
        tld = _RNG.choice(_TLDS)
        email = f"{local}@{domain}.{tld}"
        validos.append(email)

    return validos


def _generar_emails_invalidos() -> List[str]:
    """Genera ≥ 260 direcciones de correo inválidas."""
    invalidos: List[str] = []

    # Categorías de errores
    # 1. Sin @
    for _ in range(35):
        invalidos.append(_rand_alphanum_lower(3, 12) + "dominio.com")

    # 2. Múltiples @
    for _ in range(30):
        invalidos.append(
            _rand_alphanum_lower(2, 6) + "@" + _rand_alphanum_lower(2, 6) +
            "@" + _rand_alphanum_lower(2, 6) + ".com"
        )

    # 3. Sin dominio después de @
    for _ in range(30):
        invalidos.append(_rand_alphanum_lower(3, 8) + "@")

    # 4. Sin local antes de @
    for _ in range(30):
        invalidos.append("@" + _rand_alphanum_lower(3, 8) + ".com")

    # 5. TLD demasiado corto (1 carácter)
    for _ in range(30):
        invalidos.append(
            _rand_alphanum_lower(3, 8) + "@" + _rand_alphanum_lower(3, 8) +
            "." + _RNG.choice(string.ascii_lowercase)
        )

    # 6. TLD demasiado largo (> 6 caracteres)
    for _ in range(30):
        invalidos.append(
            _rand_alphanum_lower(3, 8) + "@" + _rand_alphanum_lower(3, 8) +
            "." + _rand_alpha_lower(7, 10)
        )

    # 7. Caracteres prohibidos en local
    for _ in range(30):
        bad_char = _RNG.choice("!#$%^&*()={}[]|\\:\";<>,?/")
        pos = _RNG.randint(0, 4)
        base = list(_rand_alphanum_lower(5, 8))
        base.insert(pos, bad_char)
        invalidos.append("".join(base) + "@dominio.com")

    # 8. Dominio vacío / sólo punto
    for _ in range(25):
        invalidos.append(_rand_alphanum_lower(3, 8) + "@.com")

    # 9. Cadena vacía y espacios
    invalidos.extend(["", " ", "   ", "@@", ".@.", "user@ .com"])

    # 10. Sin punto en dominio
    for _ in range(25):
        invalidos.append(
            _rand_alphanum_lower(3, 8) + "@" + _rand_alphanum_lower(5, 10)
        )

    return invalidos


# ==========================================================================#
#  2. Validador de Teléfono Mexicano (IFT – 10 dígitos)                    #
# ==========================================================================#

_PHONE_ER_FORMAL = (
    "( (+52 + ε)(  (  + - + ε ) + ( ( d d ) )  (  + - + ε ) ) + ε )"
    " d d (  + - + ε ) d d d d (  + - + ε ) d d d d"
    "\n"
    "donde d = (0+1+2+3+4+5+6+7+8+9)"
)

# Acepta formatos:
#   5512345678
#   55 1234 5678
#   55-1234-5678
#   +52 55 1234 5678
#   +52-55-1234-5678
#   (55) 1234 5678
#   (55) 1234-5678
#   (55)-1234-5678
#   +52 (55) 1234 5678
_PHONE_ER_PYTHON = (
    r"(?:\+?52\s?1?[\s-]?)?"          # prefijo internacional opcional (+52, 52, +521, +52 1)
    r"(?:(?:\([2-9]\d\)|[2-9]\d)[\s-]?)"  # lada 2 dígitos (20-99) con paréntesis balanceados opcionales
    r"\d{4}[\s-]?"                    # primeros 4 dígitos del número
    r"\d{4}"                          # últimos 4 dígitos
)

# Ladas reales frecuentes de México
_LADAS_MX = [
    "55", "56", "33", "81", "22", "44", "99", "66", "61", "87",
    "34", "47", "77", "74", "72", "62", "83", "86", "31", "46",
    "43", "42", "41", "38", "37", "36", "35", "32", "29", "28",
    "27", "26", "25", "24", "23", "21", "95", "96", "97", "98",
]


def _generar_telefonos_validos() -> List[str]:
    """Genera ≥ 260 teléfonos mexicanos válidos en distintos formatos."""
    validos: List[str] = []

    def _tel_parts():
        lada = _RNG.choice(_LADAS_MX)
        parte1 = _rand_digit_str(4)
        parte2 = _rand_digit_str(4)
        return lada, parte1, parte2

    # Formato 1: 10 dígitos corridos — 5512345678
    for _ in range(45):
        l, p1, p2 = _tel_parts()
        validos.append(f"{l}{p1}{p2}")

    # Formato 2: con espacios — 55 1234 5678
    for _ in range(40):
        l, p1, p2 = _tel_parts()
        validos.append(f"{l} {p1} {p2}")

    # Formato 3: con guiones — 55-1234-5678
    for _ in range(40):
        l, p1, p2 = _tel_parts()
        validos.append(f"{l}-{p1}-{p2}")

    # Formato 4: +52 con espacios — +52 55 1234 5678
    for _ in range(35):
        l, p1, p2 = _tel_parts()
        validos.append(f"+52 {l} {p1} {p2}")

    # Formato 5: +52 con guiones — +52-55-1234-5678
    for _ in range(30):
        l, p1, p2 = _tel_parts()
        validos.append(f"+52-{l}-{p1}-{p2}")

    # Formato 6: (lada) con espacio — (55) 1234 5678
    for _ in range(30):
        l, p1, p2 = _tel_parts()
        validos.append(f"({l}) {p1} {p2}")

    # Formato 7: (lada) con guión — (55) 1234-5678
    for _ in range(25):
        l, p1, p2 = _tel_parts()
        validos.append(f"({l}) {p1}-{p2}")

    # Formato 8: +52 (lada) — +52 (55) 1234 5678
    for _ in range(25):
        l, p1, p2 = _tel_parts()
        validos.append(f"+52 ({l}) {p1} {p2}")

    return validos


def _generar_telefonos_invalidos() -> List[str]:
    """Genera ≥ 260 teléfonos inválidos."""
    invalidos: List[str] = []

    # 1. Muy pocos dígitos (< 10)
    for n in range(1, 10):
        for _ in range(5):
            invalidos.append(_rand_digit_str(n))

    # 2. Demasiados dígitos (> 10, sin código de país)
    for _ in range(35):
        invalidos.append(_rand_digit_str(_RNG.randint(11, 15)))

    # 3. Contiene letras
    for _ in range(35):
        base = list(_rand_digit_str(10))
        pos = _RNG.randint(0, 9)
        base[pos] = _RNG.choice(string.ascii_lowercase)
        invalidos.append("".join(base))

    # 4. Caracteres especiales no válidos
    for _ in range(35):
        bad = _RNG.choice("!@#$%^&*=_[]{}|\\:;\"'<>,?/")
        base = list(_rand_digit_str(10))
        base.insert(_RNG.randint(0, 9), bad)
        invalidos.append("".join(base))

    # 5. Código de país incorrecto
    for _ in range(30):
        cc = _RNG.choice(["+1", "+44", "+34", "+49", "+00", "+53", "+5"])
        l = _RNG.choice(_LADAS_MX)
        invalidos.append(f"{cc} {l} {_rand_digit_str(4)} {_rand_digit_str(4)}")

    # 6. Paréntesis mal formados
    for _ in range(25):
        l = _RNG.choice(_LADAS_MX)
        variant = _RNG.choice([
            f"({l} {_rand_digit_str(8)}",      # sin cierre
            f"{l}) {_rand_digit_str(8)}",       # sin apertura
            f"(({l})) {_rand_digit_str(8)}",    # doble
        ])
        invalidos.append(variant)

    # 7. Cadena vacía y espacios
    invalidos.extend(["", " ", "   ", "----------", "()", "0000000000"])

    # 8. Sólo signos
    for _ in range(20):
        invalidos.append(_rand_str("+-() ", 3, 10))

    # 9. LADA inválida que inicia en 0 o 1
    for _ in range(25):
        invalidos.append(_RNG.choice(["0", "1"]) + _rand_digit_str(9))

    # 10. Formato mixto incoherente
    for _ in range(20):
        invalidos.append(
            f"+52({_RNG.choice(_LADAS_MX)})-{_rand_digit_str(2)} "
            f"{_rand_digit_str(3)}-{_rand_digit_str(5)}"
        )

    return invalidos


# ==========================================================================#
#  3. Validador de URL Web (RFC 3986 simplificado)                          #
# ==========================================================================#

_URL_ER_FORMAL = (
    "(h t t p + h t t p s) : / /"
    " (a+...+z+A+...+Z+0+...+9+-.)+ "
    " . (a+...+z+A+...+Z){2,6}"
    " ( : (0+...+9)(0+...+9)* + ε )"
    " ( / (a+...+z+A+...+Z+0+...+9+-._~:@!$&'()*+,;=%/)* + ε )"
    " ( ? (a+...+z+A+...+Z+0+...+9+-._~:@!$&'()*+,;=%&=/)* + ε )"
    " ( # (a+...+z+A+...+Z+0+...+9+-._~:@!$&'()*+,;=%/)* + ε )"
)

_URL_ER_PYTHON = (
    r"https?://"                                     # esquema
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?"     # primera etiqueta
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*"  # sub-dominios
    r"\.[a-zA-Z]{2,6}"                               # TLD
    r"(?::\d{1,5})?"                                  # puerto opcional
    r"(?:/[a-zA-Z0-9_.~:@!$&'()*+,;=/%\-]*)?"        # ruta opcional
    r"(?:\?[a-zA-Z0-9_.~:@!$&'()*+,;=/%?\-]*)?"      # query opcional
    r"(?:#[a-zA-Z0-9_.~:@!$&'()*+,;=/%\-]*)?"        # fragmento opcional
)

_URL_TLDS = [
    "com", "mx", "net", "org", "edu", "gob", "io", "dev",
    "info", "xyz", "tech", "app", "site", "online", "pro",
    "store", "club", "biz", "name", "museum",
]

_URL_PATHS = [
    "", "/", "/index.html", "/api/v1/users", "/docs/guia",
    "/products/123", "/search", "/about", "/contact", "/blog",
    "/blog/2024/01/titulo-del-post", "/assets/img/logo.png",
    "/api/v2/data", "/u/perfil", "/download/file.zip",
]

_URL_QUERIES = [
    "", "?q=test", "?page=1&size=20", "?id=42", "?lang=es",
    "?search=hola+mundo", "?token=abc123", "?utm_source=google",
    "?key=val&foo=bar&baz=qux",
]


def _generar_urls_validas() -> List[str]:
    """Genera ≥ 260 URLs válidas."""
    validas: List[str] = []

    # Ejemplos fijos representativos
    fijos = [
        "https://www.google.com",
        "http://example.com",
        "https://sub.dominio.com.mx/ruta",
        "http://localhost.dev:8080/api/v1",
        "https://mi-sitio.org/page?q=buscar",
        "http://a.io",
        "https://deep.sub.domain.net/x/y/z",
        "https://www.ejemplo.museum",
        "http://data.gob.mx/datos",
        "https://app.dev:3000",
        "https://example.com/path#fragment",
    ]
    validas.extend(fijos)

    while len(validas) < 265:
        scheme = _RNG.choice(["http", "https"])
        num_sub = _RNG.randint(0, 2)
        domain_parts = [_rand_alphanum_lower(2, 10) for _ in range(num_sub + 1)]
        domain = ".".join(domain_parts)
        tld = _RNG.choice(_URL_TLDS)

        port = ""
        if _RNG.random() < 0.15:
            port = ":" + str(_RNG.randint(80, 65535))

        path = _RNG.choice(_URL_PATHS)
        query = _RNG.choice(_URL_QUERIES)

        fragment = ""
        if _RNG.random() < 0.2:
            fragment = "#" + _rand_alphanum_lower(3, 8)

        url = f"{scheme}://{domain}.{tld}{port}{path}{query}{fragment}"
        validas.append(url)

    return validas


def _generar_urls_invalidas() -> List[str]:
    """Genera ≥ 260 URLs inválidas."""
    invalidas: List[str] = []

    # 1. Sin esquema
    for _ in range(30):
        invalidas.append(f"www.{_rand_alphanum_lower(3,8)}.com")

    # 2. Esquema incorrecto
    for _ in range(30):
        bad_scheme = _RNG.choice(["ftp", "htp", "htps", "httpss", "mailto", "file"])
        invalidas.append(f"{bad_scheme}://{_rand_alphanum_lower(3,8)}.com")

    # 3. Sin dominio
    for _ in range(25):
        invalidas.append(_RNG.choice(["http://", "https://"]))

    # 4. Sin TLD
    for _ in range(30):
        invalidas.append(f"http://{_rand_alphanum_lower(3,8)}")

    # 5. TLD inválido (1 carácter)
    for _ in range(25):
        invalidas.append(
            f"http://{_rand_alphanum_lower(3,8)}."
            f"{_RNG.choice(string.ascii_lowercase)}"
        )

    # 6. TLD demasiado largo (> 6)
    for _ in range(25):
        invalidas.append(
            f"http://{_rand_alphanum_lower(3,8)}."
            f"{_rand_alpha_lower(7, 12)}"
        )

    # 7. Doble barra en esquema mal formado
    for _ in range(25):
        invalidas.append(f"http:/{_rand_alphanum_lower(3,8)}.com")

    # 8. Espacios en URL
    for _ in range(25):
        invalidas.append(f"http://www. {_rand_alphanum_lower(3,8)} .com")

    # 9. Puerto inválido (no numérico)
    for _ in range(25):
        invalidas.append(
            f"http://{_rand_alphanum_lower(3,8)}.com:"
            f"{_rand_alpha_lower(2, 4)}"
        )

    # 10. Cadena vacía, espacios, basura
    invalidas.extend([
        "", " ", "   ", "://", "http", "https", "just-text",
        "http://", "https://", "http:///path", "://dominio.com",
        "http://.com", "http://-.com",
    ])

    # 11. Dominio empieza/termina con guión
    for _ in range(25):
        invalidas.append(f"http://-{_rand_alphanum_lower(3,8)}.com")

    return invalidas


# ==========================================================================#
#  Registro de validadores                                                  #
# ==========================================================================#

def _crear_validador_email() -> Validador:
    return Validador(
        nombre="Correo Electrónico (Email)",
        descripcion=(
            "Valida direcciones de correo electrónico con aproximación "
            "al estándar RFC 5322. Parte local: alfanuméricos, puntos, "
            "guiones bajos, guiones y signo +. Dominio: alfanuméricos, "
            "guiones y puntos. TLD de 2 a 6 caracteres alfabéticos."
        ),
        er_formal=_EMAIL_ER_FORMAL,
        er_python=_EMAIL_ER_PYTHON,
        generar_validas=_generar_emails_validos,
        generar_invalidas=_generar_emails_invalidos,
    )


def _crear_validador_telefono() -> Validador:
    return Validador(
        nombre="Teléfono Mexicano (10 dígitos – IFT)",
        descripcion=(
            "Valida números telefónicos nacionales de 10 dígitos según "
            "el Plan Técnico Fundamental de Numeración del IFT. Acepta "
            "formatos: 5512345678, 55 1234 5678, 55-1234-5678, "
            "+52 55 1234 5678, (55) 1234-5678."
        ),
        er_formal=_PHONE_ER_FORMAL,
        er_python=_PHONE_ER_PYTHON,
        generar_validas=_generar_telefonos_validos,
        generar_invalidas=_generar_telefonos_invalidos,
    )


def _crear_validador_url() -> Validador:
    return Validador(
        nombre="URL Web (RFC 3986 simplificado)",
        descripcion=(
            "Valida URLs web con esquema HTTP o HTTPS conforme a una "
            "aproximación del RFC 3986. Dominio con sub-dominios, "
            "TLD de 2–6 letras, puerto numérico opcional, ruta opcional "
            "y parámetros de consulta opcionales."
        ),
        er_formal=_URL_ER_FORMAL,
        er_python=_URL_ER_PYTHON,
        generar_validas=_generar_urls_validas,
        generar_invalidas=_generar_urls_invalidas,
    )


def obtener_todos_los_validadores() -> List[Validador]:
    """Devuelve la lista de todos los validadores registrados."""
    return [
        _crear_validador_email(),
        _crear_validador_telefono(),
        _crear_validador_url(),
    ]


# ==========================================================================#
#  Motor de validación completa                                             #
# ==========================================================================#

def ejecutar_validacion_completa(
    validador: Validador,
    auto_simulado_fn: Optional[Callable[[str, str], bool]] = None,
) -> Dict:
    """Ejecuta la validación completa de un validador.

    Para cada cadena generada (válida e inválida) se verifica con
    ``re.fullmatch`` y, opcionalmente, con una función de autómata
    simulado proporcionada por el usuario.

    Parámetros
    ----------
    validador : Validador
        El validador a ejecutar.
    auto_simulado_fn : callable, opcional
        Función ``(patron: str, cadena: str) -> bool`` que simula un
        autómata finito determinista equivalente a la ER.

    Retorna
    -------
    dict
        Diccionario con claves:
        - ``nombre``: nombre del validador
        - ``total_validas``: cantidad de cadenas válidas generadas
        - ``total_invalidas``: cantidad de cadenas inválidas generadas
        - ``aciertos_validas_re``: coincidencias de re con cadenas válidas
        - ``aciertos_invalidas_re``: rechazos de re con cadenas inválidas
        - ``precision_re``: proporción de aciertos totales / total
        - ``errores_validas_re``: lista de cadenas válidas rechazadas por re
        - ``errores_invalidas_re``: lista de cadenas inválidas aceptadas por re
        - (si auto_simulado_fn) campos análogos con sufijo ``_auto``
    """
    patron = validador.er_python
    regex = re.compile(patron)

    validas = validador.generar_validas()
    invalidas = validador.generar_invalidas()

    # -- Validación con re ------------------------------------------------
    aciertos_v_re = 0
    errores_v_re: List[str] = []
    for s in validas:
        if regex.fullmatch(s):
            aciertos_v_re += 1
        else:
            errores_v_re.append(s)

    aciertos_i_re = 0
    errores_i_re: List[str] = []
    for s in invalidas:
        if not regex.fullmatch(s):
            aciertos_i_re += 1
        else:
            errores_i_re.append(s)

    total = len(validas) + len(invalidas)
    precision_re = (aciertos_v_re + aciertos_i_re) / total if total else 0.0

    resultado: Dict = {
        "nombre": validador.nombre,
        "total_validas": len(validas),
        "total_invalidas": len(invalidas),
        "aciertos_validas_re": aciertos_v_re,
        "aciertos_invalidas_re": aciertos_i_re,
        "precision_re": round(precision_re, 4),
        "errores_validas_re": errores_v_re,
        "errores_invalidas_re": errores_i_re,
    }

    # -- Validación con autómata simulado (opcional) ----------------------
    if auto_simulado_fn is not None:
        aciertos_v_auto = 0
        errores_v_auto: List[str] = []
        for s in validas:
            if auto_simulado_fn(patron, s):
                aciertos_v_auto += 1
            else:
                errores_v_auto.append(s)

        aciertos_i_auto = 0
        errores_i_auto: List[str] = []
        for s in invalidas:
            if not auto_simulado_fn(patron, s):
                aciertos_i_auto += 1
            else:
                errores_i_auto.append(s)

        precision_auto = (
            (aciertos_v_auto + aciertos_i_auto) / total if total else 0.0
        )

        resultado.update({
            "aciertos_validas_auto": aciertos_v_auto,
            "aciertos_invalidas_auto": aciertos_i_auto,
            "precision_auto": round(precision_auto, 4),
            "errores_validas_auto": errores_v_auto,
            "errores_invalidas_auto": errores_i_auto,
        })

    return resultado


# ==========================================================================#
#  Punto de entrada para pruebas rápidas                                    #
# ==========================================================================#

if __name__ == "__main__":
    validadores = obtener_todos_los_validadores()
    total_validas_global = 0
    total_invalidas_global = 0

    for v in validadores:
        res = ejecutar_validacion_completa(v)
        total_validas_global += res["total_validas"]
        total_invalidas_global += res["total_invalidas"]

        print(f"\n{'='*60}")
        print(f"  {res['nombre']}")
        print(f"{'='*60}")
        print(f"  Cadenas válidas generadas:   {res['total_validas']}")
        print(f"  Cadenas inválidas generadas: {res['total_invalidas']}")
        print(f"  Aciertos válidas (re):       {res['aciertos_validas_re']}")
        print(f"  Aciertos inválidas (re):     {res['aciertos_invalidas_re']}")
        print(f"  Precisión (re):              {res['precision_re']:.2%}")
        if res["errores_validas_re"]:
            print(f"  ⚠ Falsos negativos (re):     {len(res['errores_validas_re'])}")
            for e in res["errores_validas_re"][:5]:
                print(f"      → {e!r}")
        if res["errores_invalidas_re"]:
            print(f"  ⚠ Falsos positivos (re):     {len(res['errores_invalidas_re'])}")
            for e in res["errores_invalidas_re"][:5]:
                print(f"      → {e!r}")

    print(f"\n{'='*60}")
    print(f"  TOTAL GLOBAL")
    print(f"{'='*60}")
    print(f"  Total cadenas válidas:   {total_validas_global}")
    print(f"  Total cadenas inválidas: {total_invalidas_global}")
    print(f"  Total general:           {total_validas_global + total_invalidas_global}")
