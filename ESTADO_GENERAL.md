# ESTADO GENERAL DEL PROYECTO — TEORÍA DE LA COMPUTACIÓN

**Última Actualización:** 2026-11-09  
**Repositorio GitHub:** [https://github.com/Kazuto834/TC-Practicas](https://github.com/Kazuto834/TC-Practicas)  
**Ramas de Trabajo:** `master`, `Practica2`, `practica-02/A7LAS-1`, `practica-02/Kazuto834`

---

## 1. Resumen Cuantitativo de Avance

| Métrica | Valor Actual | Meta | Porcentaje |
| :--- | :---: | :---: | :---: |
| **Prácticas Totales Identificadas** | 4 | 4 | 100 % |
| **Prácticas Concluidas / Integradas** | 2 (Práctica 1 y Práctica 2) | 4 | 50 % |
| **Prácticas en Planificación / Prerrequisitos Listos** | 2 (Prácticas 3 y 4) | 4 | 50 % |
| **Pruebas Automatizadas Exitosas** | **22 de 22** | $\ge 25$ | **100 %** (0 fallos) |
| **Autómatas Serializados (.jff, .json, .xml)** | **50+ archivos** | $\ge 40$ | **100 %** |
| **Archivos Generales de Control** | 6 de 6 | 6 | **100 %** |

---

## 2. Detalle de Estado por Práctica

### Práctica 1: Operaciones Básicas sobre Lenguajes
* **Estado:** **CONCLUIDA Y FUSIONADA EN MASTER**
* **PR:** Pull Request #1 fusionado el 4 de octubre de 2026.
* **Componentes:** `src/lenguajes.py`, `src/app.py`, `tests/test_lenguajes.py`, documentación `docs/01-entorno.md` a `docs/05-aplicacion.md`.

---

### Práctica 2: Autómatas Finitos No Deterministas (AFND) y Simulación
* **Estado:** **DESARROLLO, PRUEBAS Y DOCUMENTACIÓN COMPLETADOS**
* **Componentes Entregados:**
  1. **Motor Formal:** `src/automata.py` implementado con simulación concurrente, $\lambda$-clausuras y verificación de determinismo (A7LAS-1).
  2. **Serializador Multiformato:** `src/formatos.py` con importación/exportación bidireccional en `.jff`, `.json` y `.xml` conforme al Anexo 3 (Kazuto834).
  3. **Interfaz Gráfica Modular:** `src/gui_simulador.py` con definición interactiva, importación/exportación y simulación paso a paso con traza (Kazuto834).
  4. **Módulo de Integración No Destructiva:** `src/integracion.py` que unifica P1 y P2 en una sola suite interactiva con navegación por pestañas.
  5. **Integración Continua:** `.github/workflows/pruebas.yml` configurado con matriz para Python 3.11, 3.12 y 3.13.
  6. **Autómatas del Repositorio:**
     * `automatas/lista2-afd/`: 26 autómatas en `.jff`, `.json` y `.xml`.
     * `automatas/lista3-afnd/`: 8 autómatas no deterministas en los 3 formatos.
     * `automatas/lista3-afnd-lambda/`: 14 autómatas con transiciones $\lambda$ en los 3 formatos.
     * `automatas/conversiones/`: 5 conversiones AFND $\to$ AFD en los 3 formatos.
     * `automatas/aplicacion/`: Autómata formal de Pac-Man Extendido (6 estados, 2 eventos nuevos) en los 3 formatos.
  7. **Suites de Pruebas Pytest:** 22 pruebas automatizadas pasando al 100 % (`test_automata.py`, `test_formatos.py`, `test_lenguajes.py`, `test_pacman.py`).
  8. **Documentación Académica:**
     * `docs/01-entorno.md` (Flujo de ramas y GitHub Actions).
     * `docs/02-jflap.md` (Clasificación de L2 y L3, justificación de $\lambda$, y análisis comparativo de la cota $2^n$).
     * `docs/03-simulador.md` (Arquitectura desacoplada y justificación de la decisión de diseño para no determinismo).
     * `docs/04-investigacion.md` (Monografía formal, análisis de Rabin & Scott 1959, Premio Turing ACM 1976 y dos artículos con DOI $\ge 2018$).
     * `docs/05-del-articulo-al-automata.md` (Modelado de Pac-Man, 10 pruebas y ensayo de abstracción).
     * `docs/propuesta.md` (Propuesta de investigación de 1 cuartilla con 2 fuentes DOI).
     * `docs/bibliografia2.md` (Referencias en formato APA 7).

---

### Práctica 3: Extensión de Software (Subconjuntos, Minimización y Lotes)
* **Estado:** **PLANIFICADA / PRERREQUISITOS COMPLETOS**
* **Materiales de Entrada:** Análisis de Lista 3 completado; módulos base `automata.py` y `formatos.py` listos para ser extendidos con `algoritmos_afn.py` y `minimizacion.py`.

---

### Práctica 4: Teorema de Kleene y Validadores de Expresiones Regulares
* **Estado:** **PLANIFICADA / PRERREQUISITOS COMPLETOS**
* **Materiales de Entrada:** Análisis de Lista 4 completado; arquitectura modular preparada para recibir `parser_er.py` y `validadores.py`.
