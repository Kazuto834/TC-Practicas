"""
Módulo de Validadores Basados en Expresiones Regulares (Ejercicio 4 - Práctica 4).
ESCOM-IPN — Teoría de la Computación.

Incluye 4 validadores formales:
  1. Dirección de correo electrónico (subconjunto práctico RFC 5322)
  2. Número telefónico nacional de México (10 dígitos, IFT)
  3. Fecha en formato DD/MM/AAAA (ISO 8601 / calendario gregoriano 1900-2099)
  4. URL HTTP/HTTPS (subconjunto práctico RFC 3986)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import random

from automata import Automata
from er_a_automata import er_a_pipeline_completo


# Clases de símbolos (abreviaturas declaradas según la notación del curso)
MACROS_VALIDADORES: Dict[str, str] = {
    "D": "0+1+2+3+4+5+6+7+8+9",                                    # Dígitos [0-9]
    "N": "1+2+3+4+5+6+7+8+9",                                      # Dígitos no cero [1-9]
    "L": "a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p+q+r+s+t+u+v+w+x+y+z",    # Letras minúsculas [a-z]
    "U": "A+B+C+D+E+F+G+H+I+J+K+L+M+N+O+P+Q+R+S+T+U+V+W+X+Y+Z",    # Letras mayúsculas [A-Z]
    "A": "L+U+D",                                                  # Alfanumérico
    "E": "A+_+\\.+\\-",                                            # Caracteres permitidos en usuario de correo
    "H": "L+D+\\-",                                                # Caracteres permitidos en etiqueta de dominio
    "P": "A+\\.+\\-+_+/",                                          # Caracteres permitidos en ruta URL
}


@dataclass
class DefinicionValidador:
    clave: str
    nombre: str
    er_curso: str
    regex_python: str
    estandar_consultado: str
    justificacion_alcance: str


VALIDADORES_DISPONIBLES: Dict[str, DefinicionValidador] = {
    "correo": DefinicionValidador(
        clave="correo",
        nombre="Dirección de Correo Electrónico",
        er_curso="AE*@(L+D)(H)*((\\.(L+D)(H)*)+)",
        regex_python=r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*@[a-z0-9][a-z0-9-]*(\.[a-z0-9][a-z0-9-]*)+$",
        estandar_consultado="RFC 5322 (Internet Message Format) y RFC 1035 (Nombres de Dominio).",
        justificacion_alcance=(
            "Aproximación regular al RFC 5322: exige que la parte local inicie con un carácter alfanumérico (A) "
            "seguido de cero o más alfanuméricos, guiones bajos, puntos o guiones (E*), seguido de '@' y al menos "
            "dos etiquetas de dominio separadas por punto (ej. usuario@escom.ipn.mx). Quedan fuera casos válidos "
            "del estándar completo como direcciones con parte local entrecomillada (\"juan perez\"@dominio.com), "
            "direcciones IP literales entre corchetes ([192.168.1.1]), comentarios entre paréntesis o dominios "
            "internacionalizados (IDN con caracteres Unicode/Punycode). También admite algunos inválidos como "
            "puntos consecutivos ('a..b@x.com') o etiquetas de dominio de más de 63 caracteres, pues limitar longitudes "
            "exactas y evitar repeticiones contextuales dispararía el tamaño de estados del AFD."
        ),
    ),
    "telefono": DefinicionValidador(
        clave="telefono",
        nombre="Número Telefónico Nacional (México - 10 dígitos)",
        er_curso="(+52+λ)(NDDDDDDDDD+((NDD)DDDDDDD)+((NDD)\\-DDD\\-DDDD))",
        regex_python=r"^(\+52)?([1-9][0-9]{9}|\([1-9][0-9]{2}\)[0-9]{7}|[1-9][0-9]{2}-[0-9]{3}-[0-9]{4})$",
        estandar_consultado="Plan Técnico Fundamental de Numeración Nacional — Instituto Federal de Telecomunicaciones (IFT, México).",
        justificacion_alcance=(
            "Valida números telefónicos nacionales mexicanos a 10 dígitos con prefijo internacional opcional '+52' "
            "y primer dígito no cero (N ∈ {1..9}, dado que en México ningún NIR inicia con 0), admitiendo tres "
            "formatos usuales: continuo (5512345678), con lada entre paréntesis ((551)2345678) o separado por "
            "guiones (551-234-5678). Quedan fuera números cortos de emergencia o servicios (911, 074), extensiones "
            "internas (ext. 102), separadores por espacios en blanco ('55 1234 5678') y la validación semántica "
            "de si el Número Identificador de Región (NIR) de 2 o 3 dígitos está asignado geográficamente por el IFT."
        ),
    ),
    "fecha": DefinicionValidador(
        clave="fecha",
        nombre="Fecha en Formato DD/MM/AAAA",
        er_curso="((0N+(1+2)D+30)/(01+03+05+07+08+10+12)+31/(01+03+05+07+08+10+12)+(0N+(1+2)D+30)/(04+06+09+11)+(0N+1D+2(0+1+2+3+4+5+6+7+8))/02)/(19+20)DD",
        regex_python=r"^(((0[1-9]|[12][0-9]|30)/(01|03|05|07|08|10|12))|(31/(01|03|05|07|08|10|12))|((0[1-9]|[12][0-9]|30)/(04|06|09|11))|((0[1-9]|1[0-9]|2[0-8])/02))/(19|20)[0-9]{2}$",
        estandar_consultado="ISO 8601 (Data elements and interchange formats — Representation of dates and times) y calendario gregoriano.",
        justificacion_alcance=(
            "Valida fechas estrictas con separador '/' en el rango de años 1900 a 2099, discriminando la duración "
            "real de cada mes: 31 días para enero, marzo, mayo, julio, agosto, octubre y diciembre; 30 días para "
            "abril, junio, septiembre y noviembre; y 28 días para febrero (rechazando combinaciones imposibles como "
            "31/02/2026 o 31/04/2026). Queda fuera el 29 de febrero de años bisiestos (29/02/2024), fechas con guiones "
            "o formato ISO invertido (AAAA-MM-DD), meses o días sin cero inicial ('5/3/2026') y años anteriores a 1900 "
            "o posteriores a 2099."
        ),
    ),
    "url": DefinicionValidador(
        clave="url",
        nombre="URL Web (HTTP / HTTPS)",
        er_curso="http(s+λ)://(www\\.+λ)(L+D)(H)*((\\.(L+D)(H)*)+)(:DDDD+λ)(/P*+λ)",
        regex_python=r"^https?://(www\.)?[a-z0-9][a-z0-9-]*(\.[a-z0-9][a-z0-9-]*)+(:[0-9]{4})?(/[a-zA-Z0-9._/-]*)?$",
        estandar_consultado="RFC 3986 (Uniform Resource Identifier - URI: Generic Syntax) y WHATWG URL Standard.",
        justificacion_alcance=(
            "Valida URLs web con esquema 'http://' o 'https://', subdominio 'www.' opcional, nombre de host "
            "multi-etiqueta (ej. escom.ipn.mx), puerto opcional de 4 dígitos (:8080) y ruta jerárquica opcional "
            "(/practicas/tc4). Quedan fuera otros esquemas válidos del RFC 3986 (ftp://, file://, mailto:), "
            "direcciones IPv4/IPv6 literales, puertos de 1 a 3 o 5 dígitos (:80, :65535), cadenas de consulta "
            "con parámetros (?id=1&lang=es), fragmentos (#seccion) y caracteres codificados en porcentaje (%20)."
        ),
    ),
}


_CACHE_AUTOMATAS_VALIDADORES: Dict[str, Dict[str, Any]] = {}


def obtener_pipeline_validador(clave: str) -> Dict[str, Any]:
    """Construye y cachea el pipeline completo ER -> AFD -> AFD mínimo para un validador."""
    if clave not in VALIDADORES_DISPONIBLES:
        raise KeyError(f"Validador desconocido: '{clave}'.")
    if clave not in _CACHE_AUTOMATAS_VALIDADORES:
        definicion = VALIDADORES_DISPONIBLES[clave]
        pipeline = er_a_pipeline_completo(definicion.er_curso, macros=MACROS_VALIDADORES)
        _CACHE_AUTOMATAS_VALIDADORES[clave] = {
            "definicion": definicion,
            "pipeline": pipeline,
            "afd_antes": pipeline["afd"],
            "afd_minimo": pipeline["afd_minimo"],
            "estados_antes": pipeline["estados_afd_antes_min"],
            "estados_despues": pipeline["estados_afd_despues_min"],
        }
    return _CACHE_AUTOMATAS_VALIDADORES[clave]


def validar_cadena_con_validador(clave: str, texto: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """Evalúa una cadena utilizando el AFD mínimo generado desde la ER del curso."""
    info = obtener_pipeline_validador(clave)
    afd_min: Automata = info["afd_minimo"]
    return afd_min.simular_cadena(texto)


def generar_dataset_congruencia(clave: str, total: int = 600, seed: int = 2026) -> List[str]:
    """
    Genera un conjunto reproducible de `total` cadenas (50% válidas, 50% inválidas y casos frontera)
    para verificar la congruencia exacta entre el autómata del Ejercicio 2 y `re.fullmatch`.
    """
    rng = random.Random(seed)
    mitad = total // 2
    validas: List[str] = []
    invalidas: List[str] = []

    if clave == "correo":
        letras = "abcdefghijklmnopqrstuvwxyz"
        mayus = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digitos = "0123456789"
        extras = "_.-"
        tlds = ["com", "mx", "edu", "org", "ipn.mx", "escom.ipn.mx", "gob.mx", "net"]

        validas.extend([
            "a@b.c",
            "A@b.co",
            "antonio.navarro_2026@escom.ipn.mx",
            "mario-garcia834@alumno.ipn.mx",
            "123user@sub-dom1.sub2.org",
            "u_.-1@a-b.c-d",
        ])
        while len(validas) < mitad:
            ini = rng.choice(letras + mayus + digitos)
            cola = "".join(rng.choices(letras + mayus + digitos + extras, k=rng.randint(0, 12)))
            dom1 = rng.choice(letras + digitos) + "".join(rng.choices(letras + digitos + "-", k=rng.randint(0, 8)))
            tld = rng.choice(tlds)
            validas.append(f"{ini}{cola}@{dom1}.{tld}")

        invalidas.extend([
            "",
            "@dominio.com",
            ".usuario@dominio.com",
            "_usuario@dominio.com",
            "-usuario@dominio.com",
            "usuario@",
            "usuario@dominio",
            "usuario@dominio.",
            "usuario@.dominio.com",
            "usuario@-dominio.com",
            "usuario@Dominio.com",
            "usuario@dom_inio.com",
            "usu ario@dominio.com",
            "usuario@@dominio.com",
            "usuario@dom..com",
        ])
        while len(invalidas) < mitad:
            tipo_err = rng.randint(0, 5)
            if tipo_err == 0:
                invalidas.append(rng.choice("._-") + "user@escom.mx")
            elif tipo_err == 1:
                invalidas.append("user" + str(rng.randint(1, 999)) + "@sintld")
            elif tipo_err == 2:
                invalidas.append("user@" + rng.choice(mayus) + "dominio.com")
            elif tipo_err == 3:
                invalidas.append("user@dom_" + str(rng.randint(1, 99)) + ".com")
            elif tipo_err == 4:
                invalidas.append("user" + str(rng.randint(1, 99)) + "dominio.com")
            else:
                invalidas.append("user@dom." + str(rng.randint(1, 99)) + ".")

    elif clave == "telefono":
        validas.extend([
            "5512345678",
            "+525512345678",
            "(551)2345678",
            "+52(551)2345678",
            "551-234-5678",
            "+52551-234-5678",
            "9999999999",
            "1000000000",
        ])
        while len(validas) < mitad:
            pref = rng.choice(["", "+52"])
            n1 = str(rng.randint(1, 9))
            d2 = f"{rng.randint(0, 99):02d}"
            d3 = f"{rng.randint(0, 999):03d}"
            d4 = f"{rng.randint(0, 9999):04d}"
            fmt = rng.randint(0, 2)
            if fmt == 0:
                validas.append(f"{pref}{n1}{d2}{d3}{d4}")
            elif fmt == 1:
                validas.append(f"{pref}({n1}{d2}){d3}{d4}")
            else:
                validas.append(f"{pref}{n1}{d2}-{d3}-{d4}")

        invalidas.extend([
            "",
            "0512345678",
            "+520512345678",
            "(051)2345678",
            "051-234-5678",
            "551234567",
            "55123456789",
            "+52551234567",
            "525512345678",
            "(55)12345678",
            "55-1234-5678",
            "551 234 5678",
            "551-2345678",
            "(551)-234-5678",
            "551234567a",
        ])
        while len(invalidas) < mitad:
            tipo_err = rng.randint(0, 4)
            if tipo_err == 0:
                invalidas.append("0" + "".join(str(rng.randint(0, 9)) for _ in range(9)))
            elif tipo_err == 1:
                invalidas.append("".join(str(rng.randint(1, 9)) for _ in range(rng.choice([7, 8, 9, 11, 12]))))
            elif tipo_err == 2:
                invalidas.append(f"+51{rng.randint(1, 9)}{rng.randint(0, 999999999):09d}")
            elif tipo_err == 3:
                invalidas.append(f"{rng.randint(1, 9)}{rng.randint(0, 9)}-{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}")
            else:
                invalidas.append(f"({rng.randint(100, 999)}){rng.randint(100, 999)}-{rng.randint(1000, 9999)}")

    elif clave == "fecha":
        dias_por_mes = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
        }
        validas.extend([
            "01/01/1900",
            "31/12/2099",
            "28/02/2026",
            "30/04/2026",
            "31/07/2026",
            "15/01/2005",
            "06/11/2026",
        ])
        while len(validas) < mitad:
            mes = rng.randint(1, 12)
            dia = rng.randint(1, dias_por_mes[mes])
            anio = rng.randint(1900, 2099)
            validas.append(f"{dia:02d}/{mes:02d}/{anio:04d}")

        invalidas.extend([
            "",
            "00/01/2026",
            "01/00/2026",
            "32/01/2026",
            "29/02/2024",
            "30/02/2026",
            "31/02/2026",
            "31/04/2026",
            "31/06/2026",
            "31/09/2026",
            "31/11/2026",
            "15/13/2026",
            "15/01/1899",
            "15/01/2100",
            "15-01-2026",
            "2026/01/15",
            "5/1/2026",
        ])
        while len(invalidas) < mitad:
            tipo_err = rng.randint(0, 4)
            if tipo_err == 0:
                mes_30 = rng.choice([4, 6, 9, 11])
                invalidas.append(f"31/{mes_30:02d}/{rng.randint(1900, 2099)}")
            elif tipo_err == 1:
                dia_feb = rng.choice([29, 30, 31])
                invalidas.append(f"{dia_feb:02d}/02/{rng.randint(1900, 2099)}")
            elif tipo_err == 2:
                anio_malo = rng.choice([rng.randint(1000, 1899), rng.randint(2100, 2999)])
                invalidas.append(f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{anio_malo}")
            elif tipo_err == 3:
                invalidas.append(f"{rng.randint(1, 28):02d}-{rng.randint(1, 12):02d}-{rng.randint(1900, 2099)}")
            else:
                invalidas.append(f"{rng.randint(32, 99):02d}/{rng.randint(13, 99):02d}/{rng.randint(1900, 2099)}")

    elif clave == "url":
        letras = "abcdefghijklmnopqrstuvwxyz"
        digitos = "0123456789"
        ruta_chars = letras + digitos + "._-/"
        validas.extend([
            "http://a.b",
            "https://escom.ipn.mx",
            "https://www.escom.ipn.mx/practica4",
            "http://localhost1.local:8080/api/v1_0/test-ok.html",
            "https://sub-1.dom2.org/",
        ])
        while len(validas) < mitad:
            esq = rng.choice(["http://", "https://"])
            www = rng.choice(["", "www."])
            d1 = rng.choice(letras + digitos) + "".join(rng.choices(letras + digitos + "-", k=rng.randint(0, 7)))
            d2 = rng.choice(letras + digitos) + "".join(rng.choices(letras + digitos + "-", k=rng.randint(1, 5)))
            puerto = f":{rng.randint(1000, 9999)}" if rng.random() < 0.35 else ""
            ruta = "/" + "".join(rng.choices(ruta_chars, k=rng.randint(0, 12))) if rng.random() < 0.6 else ""
            validas.append(f"{esq}{www}{d1}.{d2}{puerto}{ruta}")

        invalidas.extend([
            "",
            "ftp://escom.ipn.mx",
            "escom.ipn.mx",
            "http://",
            "https://localhost",
            "http://.escom.mx",
            "http://-escom.mx",
            "http://Escom.ipn.mx",
            "http://escom.ipn.mx:80",
            "http://escom.ipn.mx:12345",
            "http://escom.ipn.mx?q=1",
            "http://escom.ipn.mx#top",
            "https://escom.ipn.mx/ruta con espacio",
            "http:/escom.ipn.mx",
        ])
        while len(invalidas) < mitad:
            tipo_err = rng.randint(0, 4)
            if tipo_err == 0:
                invalidas.append("ftp://dom" + str(rng.randint(1, 99)) + ".com")
            elif tipo_err == 1:
                invalidas.append("https://dom" + str(rng.randint(1, 99)))
            elif tipo_err == 2:
                invalidas.append("http://dom" + str(rng.randint(1, 99)) + ".mx:" + str(rng.randint(10, 999)))
            elif tipo_err == 3:
                invalidas.append("https://dom" + str(rng.randint(1, 99)) + ".com?id=" + str(rng.randint(1, 50)))
            else:
                invalidas.append("https://Dom" + str(rng.randint(1, 99)) + ".com")

    return validas[:mitad] + invalidas[:mitad]
