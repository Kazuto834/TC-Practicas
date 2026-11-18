# Práctica 1: "Operaciones Básicas sobre Lenguajes"
## Datos del Equipo
* **Carrera:** Ingeniería en Sistemas Computacionales
* **Unidad de Aprendizaje:** Teoría de la computación
* **Grupo:** 4CM4
* **Integrantes:**
  * Garcia Castillo Mario, 2025630545
  * Navarro Dominguez Antonio, 2025630725

---

## Índice de la Práctica
### Ejercicio 1: Control de versiones con Git y GitHub
* **Evidencias:** Puedes consultar las capturas de pantalla del historial del repositorio y el Pull Request:
  * [Captura de Git Log](evidencias/git/git-log.png)
  * [Captura de Pull Request Fusionado](evidencias/git/pull-request.png)

#### Parte A: Investigación
* **Documento:** [Investigacion-E1](docs/01-investigacion.md)

#### Parte C: Los tres entornos de Python
* **Documento:** [Justificación de entornos](docs/01-entorno.md)

### Ejercicio 2: Investigacion: qué es la Teoría de la Computación
* **Documento:** [Investigacion-E2](docs/02-investigacion.md)


### Ejercicio 3: Estado del arte: cinco artículos
* **Documento:** [Estado-del-arte-E3](docs/03-estado-del-arte.md)

### Ejercicio 4: Autómatas finitos en JFLAP
* **Documento:** [Automatas JFLAP](docs/04-automatas.md)

### Ejercicio 5: Aplicación con interfaz gráfica
* **Documento Explicativo:** [App en Python con Flat](docs/05-aplicacion.md)

### Bibliogarfías:
* Puede consultar todas las fuentes consultadas para la elaboración de la práctica en: [Bibliografías](docs/bibliografia.md)

---

# Práctica 2: "Autómatas Finitos No Deterministas (AFND) y Simulación de AFD con Interfaz Gráfica"

---

## Índice de la Práctica 2
### Ejercicio 1: Entorno de trabajo y flujo de ramas
* **Documento:** [Justificación del Entorno y Flujo de Ramas](docs/01-entorno.md#práctica-2-flujo-de-ramas-e-integración-continua-con-github-actions)
* **Workflow CI:** [.github/workflows/pruebas.yml](.github/workflows/pruebas.yml)
* **Evidencias:** Puedes consultar las capturas de pantalla del historial del repositorio y los Pull Requests:
  * [Captura de Git Log](evidencias/git/git-log.png)
  * [Captura de Pull Request](evidencias/git/pull-request.png)

### Ejercicio 2: AFND y AFND-λ en JFLAP y Conversiones
* **Documento:** [Clasificación, Simulación y Conversiones JFLAP](docs/02-jflap.md)
* **Autómatas:**
  * [Lista 2 (AFD)](automatas/lista2-afd/)
  * [Lista 3 (AFND)](automatas/lista3-afnd/)
  * [Lista 3 (AFND-λ)](automatas/lista3-afnd-lambda/)
  * [Conversiones a AFD](automatas/conversiones/)

### Ejercicio 3: Simulador de autómatas con interfaz gráfica
* **Documento:** [Arquitectura del Simulador y Especificación Técnica](docs/03-simulador.md)
* **Código Fuente del Núcleo y Formatos:**
  * [Motor Formal de Autómatas](src/automata.py)
  * [Serializador Multiformato (.jff, .json, .xml)](src/formatos.py)
  * [Interfaz Gráfica en Flet](src/gui_simulador.py)
  * [Módulo de Integración No Destructiva](src/integracion.py)

### Ejercicio 4: Investigación teórica y estado del arte
* **Documento:** [Monografía Teórica, Rabin & Scott (1959) y Artículos Recientes](docs/04-investigacion.md)

### Ejercicio 5: Del artículo al autómata
* **Documento:** [Modelado Formal de Pac-Man Extendido](docs/05-del-articulo-al-automata.md)
* **Autómata de la Aplicación:** [pacman_extended.jff](automatas/aplicacion/pacman_extended.jff)
* **Propuesta de Investigación (5.3):** [Propuesta de Artículo](docs/propuesta.md)

### Bibliografías:
* Puede consultar todas las fuentes consultadas para la elaboración de la práctica 2 en: [Bibliografías 2](docs/bibliografia2.md) y en [Referencias Bibliográficas Generales](REFERENCIAS_BIBLIOGRAFICAS.md)

---

## Instrucciones para Levantar el Entorno y Ejecutar Pruebas

### 1. Ejecución de la Suite de Pruebas Automatizadas
Para ejecutar todas las pruebas unitarias y de integración:
```bash
pytest
```
*O con reporte detallado:*
```bash
pytest -v
```

### 2. Ejecutar la Aplicación Interactiva
Para iniciar la suite integrada (conmuta entre la calculadora de cadenas de P1 y el simulador de autómatas de P2):
```bash
python src/integracion.py
```
O para ejecutar el simulador de autómatas de forma independiente:
```bash
python src/gui_simulador.py
```

### 3. Convención de Transiciones Lambda (λ)
En todos los formatos serializados (`.jff`, `.json`, `.xml`) y en las entradas interactivas, la transición nula/lambda se representa canónicamente como la **cadena vacía `""`** (o el nodo `<read/>` vacío en `.jff`). El lector del sistema también admite de forma flexible las cadenas `"lambda"`, `"epsilon"`, `"λ"` y `"ε"`.

---

# Práctica 3: "Extensión de Software para Simular Autómatas No Deterministas, AFN con Transiciones Lambda y Minimización de AFD"

* **Fecha Límite de Entrega:** Miércoles 4 de noviembre de 2026.
* **Etiqueta Git de Entrega:** `practica3`

---

## Índice de la Práctica 3

### Ejercicio 1: Conversión de AFD a Expresiones Regulares en JFLAP
* **Documento:** [01-afd-a-er-jflap.md](docs/practica3/01-afd-a-er-jflap.md)
* **Autómatas y Expresiones:** [automatas/practica3/afd-a-er/](automatas/practica3/afd-a-er/)

### Ejercicio 2: Extensión del Software Interactivo (Arquitectura Modular)
* **Documento Técnico:** [02-software.md](docs/practica3/02-software.md)
* **Casos de Prueba Oficiales (.jff de Lista 3):** [automatas/practica3/casos-de-prueba/](automatas/practica3/casos-de-prueba/)
* **Módulos Desarrollados (Un Archivo `.py` por Función):**
  * [`src/cerradura_lambda.py`](src/cerradura_lambda.py): Cálculo de cerradura $\lambda$ individual y global con bitácora paso a paso.
  * [`src/simulacion_directa.py`](src/simulacion_directa.py): Simulación directa de AFN-$\lambda$ detallando estados antes y después de aplicar cerradura $\lambda$.
  * [`src/eliminacion_lambda.py`](src/eliminacion_lambda.py): Transformación formal a AFN sin transiciones $\lambda$, detallando transiciones añadidas y estados promovidos a aceptación.
  * [`src/construccion_subconjuntos.py`](src/construccion_subconjuntos.py): Construcción de subconjuntos alcanzables (AFN $\to$ AFD), tabla de transiciones y justificación de aceptación.
  * [`src/eliminacion_inaccesibles.py`](src/eliminacion_inaccesibles.py): Poda formal de estados no alcanzables mediante búsqueda BFS.
  * [`src/minimizacion_afd.py`](src/minimizacion_afd.py): Minimización de AFD por refinamiento de particiones (Moore/Hopcroft) con particiones por ronda.
  * [`src/equivalencia_afd.py`](src/equivalencia_afd.py): Decisión de equivalencia entre dos AFD mediante isomorfismo de sus autómatas mínimos cocientes.
  * [`src/validacion_lotes.py`](src/validacion_lotes.py): Procesamiento masivo de cadenas desde archivo de texto con métricas estadísticas.
  * [`src/guardar_informe_lote.py`](src/guardar_informe_lote.py): Exportación de informes tabulares consolidados.

### Ejercicio 3: Documentación Formal de los Algoritmos
* **Documento:** [03-algoritmos.md](docs/practica3/03-algoritmos.md)
* **Referencias Bibliográficas Académicas (con DOI y APA 7):** [REFERENCIAS_BIBLIOGRAFICAS.md](REFERENCIAS_BIBLIOGRAFICAS.md)

---

## Instrucciones de Uso de las Funciones Nuevas (Práctica 3)

### 1. Importación Modular Directa en Python
Cada función puede ser importada e invocada independientemente en scripts o menús interactivos:
```python
from formatos import FormatosAutomata
from cerradura_lambda import calcular_cerradura_lambda
from simulacion_directa import simular_afn_lambda_directo
from eliminacion_lambda import transformar_afn_sin_lambda_detallado
from construccion_subconjuntos import construccion_subconjuntos_detallada
from minimizacion_afd import minimizar_afd_detallado
from equivalencia_afd import son_equivalentes
from validacion_lotes import procesar_lote_cadenas
from guardar_informe_lote import guardar_informe_lote

# Cargar autómata desde archivo JFLAP .jff
auto = FormatosAutomata.cargar_jff("automatas/practica3/casos-de-prueba/199.jff")

# 2.1 Cerradura lambda y simulación directa
cerradura = calcular_cerradura_lambda(auto, estado="q0")
aceptada, traza = simular_afn_lambda_directo(auto, "010")

# 2.2 Eliminación de transiciones lambda
afn_sin_l, rep_l = transformar_afn_sin_lambda_detallado(auto)

# 2.3 Construcción de subconjuntos alcanzables
afd, rep_sub = construccion_subconjuntos_detallada(afn_sin_l)

# 2.4 Minimización por particiones y equivalencia
afd_min, rep_min = minimizar_afd_detallado(afd)
son_equiv, msg = son_equivalentes(afd, afd_min)

# 2.5 Validación por lotes e informe
res_lote = procesar_lote_cadenas(afd_min, "cadenas.txt")
guardar_informe_lote(res_lote, "informe_salida.txt")
```

### 2. Ejecución de Pruebas Automatizadas
Para verificar el 100 % de los casos de prueba de la Lista 3 (ejercicios 151 a 157, 191 a 194, 196 a 200 y 260 a 263):
```bash
python -m pytest tests/test_algoritmos_p3.py -v
```
O para ejecutar la suite completa del repositorio:
```bash
python -m pytest tests/ -q
```
