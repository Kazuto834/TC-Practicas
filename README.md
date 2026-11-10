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


---

# Práctica 3: "Uso de JFLAP para Convertir AFD a Expresiones Regulares y Extensión de Software para Simular Autómatas No Deterministas, AFN con Transiciones Lambda y Minimización de AFD"

## Datos de Entrega
* **Unidad de Aprendizaje:** Teoría de la Computación
* **Carrera:** Ingeniería en Sistemas Computacionales (ESCOM-IPN)
* **Grupo:** 4CM4 / 4CV4
* **Integrantes del Equipo:**
  * Garcia Castillo Mario (Boleta: `2025630545`) — `luilligar834@gmail.com`
  * Navarro Dominguez Antonio (Boleta: `2025630725`) — `tonyex1400@gmail.com`
* **Fecha Límite de Entrega:** Miércoles 4 de noviembre de 2026
* **Etiqueta Git de Entrega:** `practica3`

---

## Índice de Documentos de la Práctica 3

### Ejercicio 1: Conversión de AFD a Expresiones Regulares
* **Documento Técnico:** [01-afd-a-er-jflap.md](docs/practica3/01-afd-a-er-jflap.md)
* **Contenido:**
  * Conversión de 5 AFD seleccionados de las Listas 2 y 3 (Ejercicios 131, 137, 139, 254 y 255) mediante JFLAP (opción *Convert FA to RE*).
  * Análisis previo de ciclos y ramas.
  * Verificación de equivalencia con *Convert to NFA* y *Compare Equivalence* junto con tabla de cadenas de prueba.
  * Simplificación algebraica formal mediante leyes de expresiones regulares.
  * Comparación analítica de 3 métodos para los Ejercicios 254 y 255: Eliminación de estados (GNFA), matriz recursiva {ij}^{(k)}$ y Lema de Arden.
* **Modelos y Expresiones:** [automatas/practica3/afd-a-er/](automatas/practica3/afd-a-er/)

### Ejercicio 2: Extensión del Software Interactivo
* **Documento Técnico:** [02-software.md](docs/practica3/02-software.md)
* **Contenido:**
  * Simulación directa de AFND-$\lambda$ sin conversión determinista previa.
  * Cálculo y visualización de la $\lambda569Xclausura para estados individuales y globales.
  * Algoritmo de eliminación de transiciones $\lambda$ con bitácora de transiciones agregadas y estados de aceptación resultantes.
  * Algoritmo de construcción de subconjuntos alcanzables fila por fila.
  * Minimización de AFD por refinamiento de particiones (Hopcroft/Moore) y prueba de equivalencia isomórfica.
  * Validador masivo de cadenas por lotes desde archivos `.txt` con generación de informes formateados.
  * Suite de pruebas automatizadas con pytest (153 pruebas aprobadas al 100%).
* **Casos de Prueba JFLAP:** [automatas/practica3/casos-de-prueba/](automatas/practica3/casos-de-prueba/)
* **Evidencias de Ejecución:** [evidencias/practica3/](evidencias/practica3/)

### Ejercicio 3: Documentación Formal de Algoritmos
* **Documento Técnico:** [03-algoritmos.md](docs/practica3/03-algoritmos.md)
* **Contenido:**
  * Enunciado formal y fundamento matemático con citas a la bibliografía oficial (Hopcroft et al. 2007, Sipser 2013, Linz 2016, Sudkamp 2005).
  * Pseudocódigo y correspondencia exacta con las funciones en `src/`.
  * Ejemplos resueltos a mano vs salida del software (Ejercicios 152, 192, 196).
  * Estimación rigurosa de complejidad temporal y espacial en función de  = |Q|$ y  = |\Sigma|$.

---

## Instrucciones de Uso de las Nuevas Funcionalidades (Práctica 3)

### 1. Interfaz Gráfica de Práctica 3 (Tkinter Desktop)
Para ejecutar la aplicación con todas las funciones paso a paso del Ejercicio 2:
```bash
python3 src/gui_practica3_tk.py
```
**Pestañas disponibles:**
1. **Importar y Clausura $\lambda$:** Permite cargar archivos `.jff`, visualizar la 5-tupla y calcular la $\lambda569Xclausura individual o total.
2. **Simulación Directa (AFN-$\lambda$):** Ejecuta la simulación concurrentemente mostrando los conjuntos activos antes y después de aplicar $\lambda569Xclausura en cada paso.
3. **Eliminación de Transiciones $\lambda$:** Convierte el autómata paso a paso, destacando aristas añadidas y nuevos estados finales; permite exportar el resultado a `.jff`.
4. **Construcción de Subconjuntos:** Genera la tabla de transiciones del AFD explorando únicamente subconjuntos alcanzables.
5. **Minimización y Equivalencia:** Muestra las particiones , P_1, P_2\dots$ ronda por ronda, y permite comparar la equivalencia de dos autómatas decidiendo si sus AFD mínimos son isomorfos.
6. **Validación Masiva por Lotes:** Procesa archivos `.txt` con una cadena por línea y exporta reportes tabulares consolidados.

### 2. Ejecución de la Suite de Pruebas de Práctica 3
Para ejecutar exclusivamente las pruebas formales de Práctica 3:
```bash
pytest -v tests/test_algoritmos_p3.py
```
O para ejecutar la suite completa del repositorio (153 pruebas):
```bash
pytest
```
