# Práctica 1: "Operaciones Básicas sobre Lenguajes"
## Datos del Equipo
* **Carrera:** Ingeniería en Sistemas Computacionales
* **Unidad de Aprendizaje:** Base de Datos
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
