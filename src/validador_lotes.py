"""
Módulo de Validación de Cadenas por Lotes desde Archivo (Práctica 3).

Proyecto: Prácticas de Teoría de la Computación (ESCOM-IPN)
Autor: Mario García Castillo (Kazuto834) <luilligar834@gmail.com>
Responsabilidad: Carga de archivos de texto con una cadena por línea,
                validación automatizada masiva y exportación de reportes de ejecución.
"""

from __future__ import annotations
import os
from typing import Dict, List, Any
from automata import Automata


def procesar_lote_cadenas(auto: Automata, ruta_archivo_lineas: str) -> Dict[str, Any]:
    """
    Lee un archivo de texto con una cadena por línea, ejecuta la simulación
    en el autómata proporcionado y genera un balance estadístico detallado.
    """
    if not os.path.exists(ruta_archivo_lineas):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo_lineas}")

    with open(ruta_archivo_lineas, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    resultados: List[Dict[str, Any]] = []
    total_aceptadas = 0
    total_rechazadas = 0

    for idx, linea in enumerate(lineas, start=1):
        cadena = linea.strip()
        aceptada, traza = auto.simular_cadena(cadena)
        if aceptada:
            total_aceptadas += 1
        else:
            total_rechazadas += 1

        resultados.append({
            "linea": idx,
            "cadena": cadena,
            "aceptada": aceptada,
            "longitud": len(cadena),
            "pasos_ejecutados": len(traza)
        })

    return {
        "archivo": os.path.basename(ruta_archivo_lineas),
        "total_cadenas": len(resultados),
        "total_aceptadas": total_aceptadas,
        "total_rechazadas": total_rechazadas,
        "porcentaje_aceptacion": (total_aceptadas / max(len(resultados), 1)) * 100.0,
        "detalles": resultados
    }


def guardar_informe_lote(informe: Dict[str, Any], ruta_salida: str) -> None:
    """Exporta el reporte consolidado de validación por lotes a formato texto plano."""
    lineas = [
        "============================================================",
        "  REPORTE CONSOLIDADO DE VALIDACIÓN MASIVA POR LOTES",
        "============================================================",
        f"Archivo evaluado:        {informe['archivo']}",
        f"Total de cadenas:        {informe['total_cadenas']}",
        f"Cadenas ACEPTADAS:       {informe['total_aceptadas']}",
        f"Cadenas RECHAZADAS:      {informe['total_rechazadas']}",
        f"Tasa de aceptación:      {informe['porcentaje_aceptacion']:.2f} %",
        "------------------------------------------------------------",
        "Línea | Cadena              | Longitud | Resultado",
        "------------------------------------------------------------"
    ]

    for item in informe["detalles"]:
        cad_repr = f"'{item['cadena']}'" if item['cadena'] else "λ (vacía)"
        estado_repr = "ACEPTADA" if item['aceptada'] else "RECHAZADA"
        lineas.append(f"{item['linea']:5d} | {cad_repr:20s} | {item['longitud']:8d} | {estado_repr}")

    lineas.append("============================================================\n")

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

