# DISTRIBUCIÓN EQUITATIVA DEL TRABAJO — TEORÍA DE LA COMPUTACIÓN

**Integrantes del Proyecto:**
1. **Integrante 1:** Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com`
2. **Integrante 2:** Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com`

---

## 1. Resumen Ejecutivo de Carga de Trabajo

Para asegurar una división verdaderamente balanceada (50 % – 50 %) de la complejidad técnica, académica y de implementación, las responsabilidades se distribuyen de manera que cada integrante tenga dominio sobre módulos de software independientes, desarrollos formales teóricos equivalentes, baterías de pruebas unitarias específicas y documentación correspondiente.

| Integrante | Módulos de Software Principales | Carga Académica / Ejercicios | Pruebas y Validación | % Carga Estimado |
| :--- | :--- | :--- | :--- | :---: |
| **A7LAS-1** | Motor formal `automata.py`, Algoritmos de eliminación $\lambda$ y minimización `minimizacion.py`, Parser léxico/sintáctico de ER `parser_er.py`. | Clasificación ejercicios impares L2/L3, Investigación formal 4.1 P2, Investigación 3.1 P3, Monografía ER P4, Artículo DOI 1 (Sistemas). | Pruebas de simulación de autómatas, pruebas de minimización de estados y pruebas sintácticas del parser. | **50.0 %** |
| **Kazuto834** | Módulo de serialización I/O `formatos.py`, Algoritmo de subconjuntos `algoritmos_afn.py`, Eliminación de estados ER `automata_a_er.py`, Validadores de patrones `validadores.py`, Integración GUI `app.py`. | Clasificación ejercicios pares L2/L3, Artículo clásico Rabin & Scott (1959), Ejercicio 5 (Pac-Man 6 estados), Artículo DOI 2 (Algoritmos), Fichas de validadores. | Pruebas de ida y vuelta (roundtrip) I/O (.jff, .json, .xml), pruebas de subconjuntos y suite de congruencia con 500 cadenas (`re.fullmatch`). | **50.0 %** |

---

## 2. Matriz Detallada de Distribución por Práctica

### Práctica 2: Autómatas Finitos No Deterministas y Simulación

| Actividad / Módulo | Responsable | Archivos Asignados | Rama de Trabajo | Carga Est. | Estado |
| :--- | :---: | :--- | :--- | :---: | :---: |
| **Núcleo Formal:** Clase `Automata`, `Estado`, `Transicion`, motor de simulación AFD/AFND, cálculo de $\lambda$-clausuras | **A7LAS-1** | `src/automata.py`<br/>`tests/test_automata.py` | `practica-02/A7LAS-1` | 15 % | En Desarrollo |
| **Serialización Multi-formato:** Parser y generador `.jff` (JFLAP), `.json`, `.xml` con validación de quíntupla | **Kazuto834** | `src/formatos.py`<br/>`tests/test_formatos.py` | `practica-02/Kazuto834` | 15 % | En Desarrollo |
| **Ejercicio 2 (Impares):** Clasificación formal y análisis de ejercicios impares de Lista 2 (97–149) y Lista 3 (151–263) | **A7LAS-1** | `docs/02-jflap.md` (Sec. Impares)<br/>`automatas/lista2-afd/`, `automatas/lista3-afnd/` | `practica-02/A7LAS-1` | 10 % | En Desarrollo |
| **Ejercicio 2 (Pares) y Análisis $2^n$:** Clasificación formal de ejercicios pares, tabla comparativa de 5 casos y familia $L_n$ | **Kazuto834** | `docs/02-jflap.md` (Sec. Pares)<br/>`automatas/conversiones/` | `practica-02/Kazuto834` | 10 % | En Desarrollo |
| **Ejercicio 4.1:** Monografía sobre no determinismo, subconjuntos, cota exponencial, Teorema de Kleene y Hopcroft | **A7LAS-1** | `docs/04-investigacion.md` (Cap. 1 a 7) | `practica-02/A7LAS-1` | 10 % | En Desarrollo |
| **Ejercicio 4.2 y 4.3:** Estudio de Rabin & Scott (1959), Premio Turing ACM 1976 y dos artículos con DOI ($\ge 2018$) | **Kazuto834** | `docs/04-investigacion.md` (Cap. 8 y 9) | `practica-02/Kazuto834` | 10 % | En Desarrollo |
| **Ejercicio 5:** Modelado formal de Pac-Man (6 estados, 2 eventos nuevos), archivo `.jff`, 10 pruebas y abstracción | **Kazuto834** | `docs/05-del-articulo-al-automata.md`<br/>`automatas/aplicacion/pacman_extended.jff` | `practica-02/Kazuto834` | 10 % | En Desarrollo |
| **Propuesta de Trabajo (5.3) y CI:** Propuesta de artículo y workflow GitHub Actions (`pruebas.yml`) | **A7LAS-1** / **Kazuto834** | `docs/propuesta.md`<br/>`.github/workflows/pruebas.yml` | Integración | 10 % | En Desarrollo |
| **Interfaz Gráfica Modular:** Integración de componentes visuales en Flet respetando Práctica 1 | **Kazuto834** | `src/gui_simulador.py`<br/>`src/app.py` | `practica-02/Kazuto834` | 10 % | En Desarrollo |

---

### Práctica 3: Algoritmos Formales de Transformación y Minimización

| Actividad / Módulo | Responsable | Archivos Asignados | Rama de Trabajo | Carga Est. | Estado |
| :--- | :---: | :--- | :--- | :---: | :---: |
| **Eliminación $\lambda$ y Minimización:** Algoritmos de eliminación de transiciones $\lambda$, refinamiento de particiones y equivalencia | **A7LAS-1** | `src/minimizacion.py`<br/>`tests/test_minimizacion.py` | `practica-03/A7LAS-1` | 20 % | Planificada |
| **Construcción de Subconjuntos y Lotes:** Conversión AFN a AFD alcanzables, tabla de transiciones y validación por archivo | **Kazuto834** | `src/algoritmos_afn.py`<br/>`src/validador_lotes.py`<br/>`tests/test_algoritmos.py` | `practica-03/Kazuto834` | 20 % | Planificada |
| **Ejercicio 1:** Conversión de 5 AFD a ER con JFLAP y resolución analítica a mano (3 métodos: Estados, $R_{ij}^{(k)}$, Arden) | **A7LAS-1** (3 AFD + Métodos)<br/>**Kazuto834** (2 AFD + Verif.) | `docs/practica3/01-afd-a-er-jflap.md`<br/>`automatas/practica3/afd-a-er/` | `practica-03/integracion` | 30 % | Planificada |
| **Ejercicio 3:** Documentación teórica, pseudocódigos, complejidades asintóticas y correspondencia en código | **A7LAS-1** (Sec. Minimización)<br/>**Kazuto834** (Sec. Subconjuntos) | `docs/practica3/03-algoritmos.md` | `practica-03/integracion` | 20 % | Planificada |
| **Suite de Pruebas de Preservación de Lenguaje:** Verificación exhaustiva hasta longitud $k$ en las 4 variantes de autómatas | **A7LAS-1** / **Kazuto834** | `tests/test_preservacion_lenguaje.py` | `practica-03/integracion` | 10 % | Planificada |

---

### Práctica 4: Teorema de Kleene y Validadores de Aplicación

| Actividad / Módulo | Responsable | Archivos Asignados | Rama de Trabajo | Carga Est. | Estado |
| :--- | :---: | :--- | :--- | :---: | :---: |
| **Parser de Expresiones Regulares y Thompson:** Análisis léxico, sintáctico con errores posicionales y construcción inductiva de Thompson | **A7LAS-1** | `src/parser_er.py`<br/>`src/er_a_automata.py`<br/>`tests/test_parser.py` | `practica-04/A7LAS-1` | 25 % | Planificada |
| **Conversión AFD a Expresión Regular:** Eliminación de estados sobre autómatas finitos generalizados y simplificación algebraica | **Kazuto834** | `src/automata_a_er.py`<br/>`tests/test_automata_a_er.py` | `practica-04/Kazuto834` | 25 % | Planificada |
| **Investigación Teórica de Expresiones Regulares:** Monografía formal, Jerarquía de Chomsky, leyes algebraicas y bombeo de $(a^*)b\backslash 1$ | **A7LAS-1** | `docs/practica4/01-investigacion-er.md` | `practica-04/A7LAS-1` | 20 % | Planificada |
| **Validadores Prácticos y Suite de 500 Cadenas:** Modelos de Email, Teléfono nacional y URL, y comprobación automatizada contra `re.fullmatch` | **Kazuto834** | `src/validadores.py`<br/>`docs/practica4/04-validadores.md`<br/>`tests/test_validadores.py` | `practica-04/Kazuto834` | 20 % | Planificada |
| **Documentación de Algoritmos y Evidencias:** Reportes comparativos de equivalencia con JFLAP de P3 y evidencias | **A7LAS-1** / **Kazuto834** | `docs/practica4/02-er-a-automata.md`<br/>`docs/practica4/03-automata-a-er.md` | `practica-04/integracion` | 10 % | Planificada |

---

## 3. Protocolo de Identidad y Autoría en Git

De acuerdo con las directrices de integridad:
* Cada módulo y archivo fuente contiene un encabezado identificando al autor responsable y su correo institucional.
* Los commits en las ramas correspondientes se asocian a las identidades verificadas de GitHub:
  * Para **A7LAS-1**: `Antonio Navarro Domínguez <tonyex1400@gmail.com>`
  * Para **Kazuto834**: `Mario García Castillo <luilligar834@gmail.com>`
* La integración final se realiza mediante Pull Requests detallados que documentan la contribución técnica individual de cada autor.
