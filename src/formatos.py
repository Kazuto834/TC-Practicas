"""
Módulo de Serialización e Importación/Exportación Multiformato de Autómatas.

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Lectura y escritura bidireccional en formatos .jff (JFLAP 7.1),
                .json estructurado y .xml canónico según especificaciones del Anexo 3.
"""

from __future__ import annotations
import json
import math
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Optional
from automata import Automata, Transicion, Estado


class FormatosAutomata:
    """Provee métodos estáticos de serialización y deserialización para autómatas."""

    # =========================================================================
    # FORMATO .JFF (JFLAP 7.1)
    # =========================================================================
    @staticmethod
    def cargar_jff(origen: str) -> Automata:
        """
        Importa un autómata desde un archivo .jff o desde una cadena XML nativa de JFLAP.
        """
        if os.path.exists(origen):
            tree = ET.parse(origen)
            root = tree.getroot()
        else:
            root = ET.fromstring(origen)

        automaton_elem = root.find("automaton")
        if automaton_elem is None:
            # En algunas versiones de JFLAP la raíz es directamente <automaton>
            automaton_elem = root if root.tag == "automaton" else None
            if automaton_elem is None:
                raise ValueError("El archivo JFF no contiene el elemento raíz <automaton>.")

        auto = Automata()
        id_a_nombre: Dict[str, str] = {}
        nombre_a_id: Dict[str, str] = {}

        # 1. Leer estados
        for state_elem in automaton_elem.findall("state"):
            state_id = state_elem.attrib.get("id", "")
            state_name = state_elem.attrib.get("name", f"q{state_id}")
            
            id_a_nombre[state_id] = state_name
            nombre_a_id[state_name] = state_id

            x_elem = state_elem.find("x")
            y_elem = state_elem.find("y")
            pos_x = float(x_elem.text) if x_elem is not None and x_elem.text else 100.0
            pos_y = float(y_elem.text) if y_elem is not None and y_elem.text else 100.0

            es_inicial = state_elem.find("initial") is not None
            es_final = state_elem.find("final") is not None

            auto.agregar_estado(
                nombre=state_name,
                es_inicial=es_inicial,
                es_final=es_final,
                pos_x=pos_x,
                pos_y=pos_y
            )

        # 2. Leer transiciones
        for trans_elem in automaton_elem.findall("transition"):
            from_elem = trans_elem.find("from")
            to_elem = trans_elem.find("to")
            read_elem = trans_elem.find("read")

            if from_elem is None or to_elem is None:
                continue

            from_id = from_elem.text.strip() if from_elem.text else ""
            to_id = to_elem.text.strip() if to_elem.text else ""

            origen_nombre = id_a_nombre.get(from_id, f"q{from_id}")
            destino_nombre = id_a_nombre.get(to_id, f"q{to_id}")

            # En JFLAP, <read/> o <read></read> representa la transición lambda (cadena vacía '')
            simbolo = ""
            if read_elem is not None and read_elem.text:
                simbolo = read_elem.text.strip()
                if simbolo.lower() in ("lambda", "epsilon", "λ", "ε"):
                    simbolo = ""

            auto.agregar_transicion(origen_nombre, simbolo, destino_nombre)

        auto._actualizar_tipo()
        return auto

    @staticmethod
    def guardar_jff(automata: Automata, ruta_salida: str) -> None:
        """
        Exporta el autómata a un archivo .jff con formato nativo de JFLAP 7.1.
        Genera coordenadas espaciales automáticas circulares si no están definidas.
        """
        root = ET.Element("structure")
        type_elem = ET.SubElement(root, "type")
        type_elem.text = "fa"
        automaton_elem = ET.SubElement(root, "automaton")

        # Asignar identificadores numéricos ordenados para JFLAP
        estados_ordenados = sorted(list(automata.estados))
        nombre_a_id: Dict[str, str] = {nombre: str(i) for i, nombre in enumerate(estados_ordenados)}

        n = len(estados_ordenados)
        radio = 150.0
        centro_x, centro_y = 250.0, 200.0

        for i, nombre in enumerate(estados_ordenados):
            state_id = nombre_a_id[nombre]
            meta = automata.metadatos_estados.get(nombre)

            if meta and (meta.pos_x != 100.0 or meta.pos_y != 100.0):
                x_val, y_val = meta.pos_x, meta.pos_y
            else:
                angulo = (2 * math.pi * i) / max(n, 1)
                x_val = centro_x + radio * math.cos(angulo)
                y_val = centro_y + radio * math.sin(angulo)

            state_elem = ET.SubElement(automaton_elem, "state", id=state_id, name=nombre)
            ET.SubElement(state_elem, "x").text = f"{x_val:.1f}"
            ET.SubElement(state_elem, "y").text = f"{y_val:.1f}"

            if nombre == automata.estado_inicial:
                ET.SubElement(state_elem, "initial")
            if nombre in automata.estados_aceptacion:
                ET.SubElement(state_elem, "final")

        for trans in automata.transiciones:
            trans_elem = ET.SubElement(automaton_elem, "transition")
            ET.SubElement(trans_elem, "from").text = nombre_a_id.get(trans.origen, "0")
            ET.SubElement(trans_elem, "to").text = nombre_a_id.get(trans.destino, "0")
            read_elem = ET.SubElement(trans_elem, "read")
            if trans.simbolo:
                read_elem.text = trans.simbolo
            # Si es lambda se deja <read/> vacío por especificación de JFLAP

        xml_str = ET.tostring(root, encoding="utf-8")
        header = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        with open(ruta_salida, "wb") as f:
            f.write(header + xml_str)

    # =========================================================================
    # FORMATO .JSON (ESQUEMA ANEXO 3)
    # =========================================================================
    @staticmethod
    def cargar_json(origen: str) -> Automata:
        """
        Importa un autómata desde un archivo .json o desde una cadena JSON según Anexo 3.
        """
        if os.path.exists(origen):
            with open(origen, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.loads(origen)

        auto = Automata(
            alfabeto=set(data.get("alfabeto", [])),
            estados=set(data.get("estados", [])),
            estado_inicial=data.get("inicial"),
            estados_aceptacion=set(data.get("aceptacion", [])),
            tipo=data.get("tipo", "AFD")
        )

        for trans_data in data.get("transiciones", []):
            desde = trans_data.get("desde", "")
            lee = trans_data.get("lee", "")
            hacia_lista = trans_data.get("hacia", [])

            if isinstance(hacia_lista, str):
                hacia_lista = [hacia_lista]

            for destino in hacia_lista:
                auto.agregar_transicion(desde, lee, destino)

        auto._actualizar_tipo()
        return auto

    @staticmethod
    def guardar_json(automata: Automata, ruta_salida: str) -> None:
        """
        Exporta el autómata a formato .json estructurado conforme a la especificación oficial.
        """
        # Agrupar transiciones con mismo origen y símbolo
        agrupadas: Dict[tuple[str, str], List[str]] = {}
        for t in automata.transiciones:
            clave = (t.origen, t.simbolo)
            if clave not in agrupadas:
                agrupadas[clave] = []
            if t.destino not in agrupadas[clave]:
                agrupadas[clave].append(t.destino)

        transiciones_json = []
        for (desde, lee), destinos in sorted(agrupadas.items()):
            transiciones_json.append({
                "desde": desde,
                "lee": lee,
                "hacia": sorted(destinos)
            })

        data = {
            "tipo": automata.tipo,
            "alfabeto": sorted(list(automata.alfabeto)),
            "estados": sorted(list(automata.estados)),
            "inicial": automata.estado_inicial,
            "aceptacion": sorted(list(automata.estados_aceptacion)),
            "transiciones": transiciones_json
        }

        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # =========================================================================
    # FORMATO .XML (ESQUEMA CANÓNICO ANEXO 3)
    # =========================================================================
    @staticmethod
    def cargar_xml(origen: str) -> Automata:
        """
        Importa un autómata desde un archivo .xml o cadena XML canónica según Anexo 3.
        """
        if os.path.exists(origen):
            tree = ET.parse(origen)
            root = tree.getroot()
        else:
            root = ET.fromstring(origen)

        auto = Automata(tipo=root.attrib.get("tipo", "AFD"))

        # Alfabeto
        alfabeto_elem = root.find("alfabeto")
        if alfabeto_elem is not None:
            for simb in alfabeto_elem.findall("simbolo"):
                if simb.text:
                    auto.agregar_simbolo(simb.text.strip())

        # Estados
        estados_elem = root.find("estados")
        if estados_elem is not None:
            for est in estados_elem.findall("estado"):
                nombre = est.attrib.get("nombre", "")
                es_ini = est.attrib.get("inicial", "false").lower() in ("true", "1")
                es_fin = est.attrib.get("aceptacion", "false").lower() in ("true", "1")
                auto.agregar_estado(nombre, es_inicial=es_ini, es_final=es_fin)

        # Transiciones
        trans_elem = root.find("transiciones")
        if trans_elem is not None:
            for t in trans_elem.findall("transicion"):
                desde = t.attrib.get("desde", "")
                lee = t.attrib.get("lee", "")
                hacia = t.attrib.get("hacia", "")
                auto.agregar_transicion(desde, lee, hacia)

        auto._actualizar_tipo()
        return auto

    @staticmethod
    def guardar_xml(automata: Automata, ruta_salida: str) -> None:
        """
        Exporta el autómata a formato .xml canónico según Anexo 3.
        """
        root = ET.Element("automata", tipo=automata.tipo)

        # Alfabeto
        alfabeto_elem = ET.SubElement(root, "alfabeto")
        for simb in sorted(list(automata.alfabeto)):
            s_elem = ET.SubElement(alfabeto_elem, "simbolo")
            s_elem.text = simb

        # Estados
        estados_elem = ET.SubElement(root, "estados")
        for est in sorted(list(automata.estados)):
            attrs = {"nombre": est}
            if est == automata.estado_inicial:
                attrs["inicial"] = "true"
            if est in automata.estados_aceptacion:
                attrs["aceptacion"] = "true"
            ET.SubElement(estados_elem, "estado", **attrs)

        # Transiciones
        trans_elem = ET.SubElement(root, "transiciones")
        for t in automata.transiciones:
            ET.SubElement(
                trans_elem,
                "transicion",
                desde=t.origen,
                lee=t.simbolo,
                hacia=t.destino
            )

        xml_str = ET.tostring(root, encoding="utf-8")
        header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        with open(ruta_salida, "wb") as f:
            f.write(header + xml_str)
