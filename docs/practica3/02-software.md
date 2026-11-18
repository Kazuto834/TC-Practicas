# EJERCICIO 2: EXTENSIÓN DEL SOFTWARE INTERACTIVO (ARQUITECTURA MODULAR)

**Unidad de Aprendizaje:** Teoría de la Computación  
**Institución:** Instituto Politécnico Nacional — Escuela Superior de Cómputo (ESCOM)  
**Programa Académico:** Ingeniería en Sistemas Computacionales  
**Norma de Citación:** APA 7.ª Edición  
**Propósito:** Especificación de la arquitectura modular desacoplada del Ejercicio 2, detallando cada archivo `.py` independiente, su funcionalidad, parámetros de entrada, salidas y pruebas automatizadas.

---

## 1. Arquitectura de Módulos (Un Archivo `.py` por Función)

Siguiendo estrictamente el principio de responsabilidad única y modularidad desacoplada, cada algoritmo del Ejercicio 2 fue programado en un archivo Python independiente dentro de `src/`, permitiendo su ejecución sin interfaz gráfica y facilitando su integración en cualquier menú principal o interfaz de usuario:

| Módulo `.py` | Función Principal | Descripción Técnica |
| :--- | :--- | :--- |
| `src/cerradura_lambda.py` | `calcular_cerradura_lambda` | Calcula la $\lambda$-clausura individual o de todos los estados del autómata mediante BFS, generando bitácora de expansión paso a paso. |
| `src/simulacion_directa.py` | `simular_afn_lambda_directo` | Simula un AFN-$\lambda$ directamente en tiempo lineal respecto a la cadena sin determinizarlo, mostrando en cada paso los estados activos antes y después de aplicar la cerradura $\lambda$. |
| `src/eliminacion_lambda.py` | `eliminar_transiciones_lambda`<br/>`transformar_afn_sin_lambda_detallado` | Transforma un AFN-$\lambda$ en un AFN sin transiciones $\lambda$ equivalente, documentando las transiciones añadidas y los estados que pasan a ser de aceptación. |
| `src/construccion_subconjuntos.py` | `construccion_subconjuntos`<br/>`construccion_subconjuntos_detallada` | Convierte un AFN en un AFD determinista equivalente explorando únicamente los subconjuntos alcanzables desde $S_0$, generando la tabla de transiciones fila por fila y justificando la aceptación. |
| `src/eliminacion_inaccesibles.py` | `eliminar_estados_inaccesibles` | Identifica mediante recorrido en anchura (BFS) los estados alcanzables desde $q_0$ y poda los inaccesibles. |
| `src/minimizacion_afd.py` | `minimizar_afd`<br/>`minimizar_afd_detallado` | Minimiza un AFD por refinamiento sucesivo de particiones (Moore/Hopcroft), registrando la partición resultante en cada ronda hasta alcanzar estabilidad. |
| `src/equivalencia_afd.py` | `son_equivalentes`<br/>`decidir_equivalencia_detallada` | Decide si dos AFD son formalmente equivalentes minimizando ambos y comprobando el isomorfismo estructural de sus estados mínimos cocientes. |
| `src/validacion_lotes.py` | `procesar_lote_cadenas`<br/>`validar_lista_cadenas` | Lee archivos de texto con una cadena por línea, ejecuta la simulación masiva y computa estadísticas de aceptación. |
| `src/guardar_informe_lote.py` | `guardar_informe_lote` | Exporta a un archivo de texto un reporte consolidado estructurado y tabular con los resultados del lote. |

### 1.1 Módulos Fachada para Retrocompatibilidad
Para asegurar compatibilidad con código existente y suites de prueba anteriores, se mantuvieron fachadas que reexportan directamente las funciones individuales:
* `src/algoritmos_afn.py`: Reexporta `calcular_cerradura_lambda`, `simular_afn_lambda_directo`, `eliminar_transiciones_lambda` y `construccion_subconjuntos`.
* `src/minimizacion.py`: Reexporta `eliminar_estados_inaccesibles`, `minimizar_afd` y `son_equivalentes`.
* `src/validador_lotes.py`: Reexporta `procesar_lote_cadenas` y `guardar_informe_lote`.

---

## 2. Detalle de Operación por Algoritmo

### 2.1 Cerradura $\lambda$ y Simulación Directa (Sección 2.1)
* **Archivo:** `src/cerradura_lambda.py` y `src/simulacion_directa.py`.
* **Entradas:** Instancia de `Automata` (desde archivo `.jff`) y cadena de texto `w`.
* **Salida de Cerradura:** Diccionario con lista de estados alcanzados y traza paso a paso de cada transición $\lambda$ transitada.
* **Salida de Simulación Directa:** Tupla `(aceptada: bool, traza: List[Dict])`. Cada elemento de la traza expone:
  * `paso`: número secuencial.
  * `simbolo_leido`: carácter procesado.
  * `estados_antes_cerradura`: destinos directos por aristas con el símbolo.
  * `estados_despues_cerradura`: conjunto activo tras expandir por transiciones $\lambda$.
  * `es_aceptacion`: booleano que indica si algún estado activo pertenece a $F$.
* **Casos de Prueba (Lista 3, 196 a 200):**
  * Verificados en `tests/test_algoritmos_p3.py` con `196.jff`, `197.jff`, `198.jff`, `199.jff` y `200.jff`.

### 2.2 Eliminación de Transiciones $\lambda$ (Sección 2.2)
* **Archivo:** `src/eliminacion_lambda.py`.
* **Entradas:** `Automata` con transiciones nulas.
* **Transformación:**
  $$\delta'(q, a) = \lambda\text{-cl}(\delta(\lambda\text{-cl}(q), a))$$
  $$F' = \{ q \in Q \mid \lambda\text{-cl}(q) \cap F \neq \emptyset \}$$
* **Salida:** Instancia de `Automata` sin transiciones $\lambda$ y bitácora con los estados promovidos a aceptación y el conjunto de transiciones añadidas con su justificación teórica.

### 2.3 Construcción de Subconjuntos (Sección 2.3)
* **Archivo:** `src/construccion_subconjuntos.py`.
* **Entradas:** `Automata` no determinista.
* **Mecánica:** Cola FIFO para explorar recursivamente solo los subconjuntos alcanzables:
  * $S_0 = \lambda\text{-cl}(\{q_0\})$.
  * Por cada $S$ y símbolo $a$: $U = \lambda\text{-cl}\left(\bigcup_{p \in S} \delta(p, a)\right)$.
  * Clasificación formal de aceptación: $S$ es final si y solo si $S \cap F_N \neq \emptyset$.
* **Salida:** `Automata` determinista (AFD) y diccionario con la tabla de transiciones generada paso a paso y la justificación de cada subconjunto.
* **Casos de Prueba (Lista 3, 191 a 194 y 260 a 263):**
  * Verificados con los 8 autómatas oficiales en `tests/test_algoritmos_p3.py`.

### 2.4 Minimización de AFD y Equivalencia (Sección 2.4)
* **Archivos:** `src/eliminacion_inaccesibles.py`, `src/minimizacion_afd.py` y `src/equivalencia_afd.py`.
* **Mecánica:**
  1. Poda de estados inaccesibles mediante BFS.
  2. Partición inicial $P_0 = \{ Q \setminus F, F \}$.
  3. Refinamiento en rondas sucesivas $P_1, P_2, \dots, P_k$ clasificando por firmas de transición hacia las clases activas.
  4. Detención al alcanzar estabilidad ($P_k = P_{k-1}$).
  5. Decisión de equivalencia comprobando isomorfismo biyectivo sobre los autómatas mínimos cocientes resultantes.
* **Casos de Prueba (Lista 3, 151 a 157):**
  * Verificados en `tests/test_algoritmos_p3.py` con `151.jff` a `157.jff`.

### 2.5 Validación Masiva por Lotes e Informes (Sección 2.5)
* **Archivos:** `src/validacion_lotes.py` y `src/guardar_informe_lote.py`.
* **Entradas:** Ruta de archivo `.txt` con una cadena por renglón.
* **Salida:** Reporte estadístico y archivo de texto formateado en columnas con cabecera, métricas de aceptación y resultado individual por línea.

---

## 3. Pruebas Automatizadas con Pytest (Sección 2.6)

La suite de pruebas en `tests/test_algoritmos_p3.py` implementa pruebas exhaustivas parametrizadas sobre los **20 casos de prueba oficiales de la Lista 3** ubicados en `automatas/practica3/casos-de-prueba/`:

```bash
python -m pytest tests/test_algoritmos_p3.py -v
```

### Resultados de la Verificación Formal
* **Preservación de Lenguaje:** Para cada uno de los 20 autómatas, se verifica que:
  $$L(M_{\text{original}}) = L(M_{\text{sin\_}\lambda}) = L(M_{\text{subconjuntos}}) = L(M_{\text{mínimo}})$$
  sobre todas las palabras de $\Sigma^*$ hasta longitud 3 (cota justificada por el Lema de Bombeo para detección exhaustiva de discrepancias en ciclos y bifurcaciones).
* **Cota de Estados:** En el 100 % de los casos se satisface:
  $$|Q_{AFD\_min}| \le |Q_{AFD\_sub}|$$
* **Determinismo Estricto:** Se valida formalmente que tanto el autómata de subconjuntos como el mínimo carecen de transiciones nulas y poseen a lo sumo una transición por símbolo en cada estado.
* **Cobertura:** 27 pruebas de la Práctica 3 aprobadas con **100 % de éxito** (y 156 pruebas en la totalidad del repositorio).
