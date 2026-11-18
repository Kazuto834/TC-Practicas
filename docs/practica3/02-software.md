# EJERCICIO 2: EXTENSIÓN DEL SOFTWARE INTERACTIVO (ALGORITMOS FORMALES)

**Práctica 3:** Extensión de Software para Autómatas Finitos y Expresiones Regulares  
**Autores:**  
* Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com`
* Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com`  
**Institución:** Escuela Superior de Cómputo (ESCOM-IPN) — 4CM4 / 4CV4

---

## 1. Módulos Desarrollados en Python Puro

Siguiendo el principio de arquitectura desacoplada, todos los algoritmos fueron implementados en la carpeta `src/` en Python estándar sin dependencias de Flet ni de bibliotecas de grafos externas:

| Módulo | Responsable | Funcionalidades Principales |
| :--- | :---: | :--- |
| `src/algoritmos_afn.py` | **Kazuto834** | 1. Simulación directa de AFND-$\lambda$ sin conversión previa.<br/>2. Eliminación formal de transiciones $\lambda$.<br/>3. Construcción de subconjuntos (AFN $\to$ AFD alcanzables). |
| `src/minimizacion.py` | **A7LAS-1** | 1. Eliminación de estados inaccesibles mediante BFS.<br/>2. Minimización de AFD por particiones (Hopcroft).<br/>3. Decisión de equivalencia exacta de lenguajes. |
| `src/validador_lotes.py` | **Kazuto834** | 1. Carga masiva de cadenas desde archivo `.txt`.<br/>2. Procesamiento por lotes y estadísticas.<br/>3. Generación de informes tabulares exportables. |

---

## 2. Descripción de Algoritmos y Casos de Prueba

### 2.1 Simulación Directa y $\lambda$-Clausura (Sección 2.1)
* **Función:** `simulacion_directa_paso_a_paso(auto, cadena)` en `algoritmos_afn.py`.
* **Mecánica:** Mantiene el conjunto activo $S_t$ y aplica la $\lambda$-clausura reflexiva y transitiva antes y después de consumir cada símbolo.
* **Casos de Prueba (Lista 3, 196 a 200):**
  * Verificado en `tests/test_algoritmos_p3.py` con el ejercicio 199 (puentes $\lambda$ intermedios). La cadena vacía `""` y secuencias como `0011` y `010` activan caminos paralelos sin determinizar el autómata.

### 2.2 Eliminación de Transiciones $\lambda$ (Sección 2.2)
* **Función:** `eliminar_transiciones_lambda(auto)` en `algoritmos_afn.py`.
* **Axiomas Matemáticos:**
  $$\delta'(q, a) = \lambda\text{-cl}(\delta(\lambda\text{-cl}(q), a))$$
  $$F' = \{q \in Q \mid \lambda\text{-cl}(q) \cap F \ne \emptyset\}$$
* **Resultado:** Produce un AFN estándar sin aristas vacías que acepta exactamente el mismo lenguaje.

### 2.3 Construcción de Subconjuntos Alcanzables (Sección 2.3)
* **Función:** `construccion_subconjuntos(auto)` en `algoritmos_afn.py`.
* **Mecánica:** A partir de $S_0 = \lambda\text{-cl}(\{q_0\})$, explora iterativamente mediante una cola BFS únicamente los subconjuntos alcanzables del conjunto potencia $\mathcal{P}(Q)$.
* **Casos de Prueba (Lista 3, 191 a 194 y 260 a 263):**
  * Implementados y guardados en `automatas/conversiones/` (192, 193, 262, 263).

### 2.4 Minimización de AFD y Equivalencia (Sección 2.4)
* **Funciones:** `eliminar_estados_inaccesibles(auto)`, `minimizar_afd(auto)` y `son_equivalentes(afd1, afd2)`.
* **Casos de Prueba (Lista 3, 151 a 157):**
  * Demostrado con el autómata de paridad y con el Ejercicio 152: colapsa estados redundantes con idéntica firma de transición hacia las clases activas.
  * La función `son_equivalentes` comprueba exhaustivamente la preservación de lenguaje en todas las cadenas de $\Sigma^{\le 6}$.

### 2.5 Validación Masiva por Lotes (Sección 2.5)
* **Función:** `procesar_lote_cadenas(auto, ruta)` y `guardar_informe_lote(informe, salida)`.
* Permite cargar archivos con cientos de cadenas y produce un reporte formateado con estadísticas de aceptación, rechazo y conteo de pasos.

---

## 3. Pruebas Automatizadas (Sección 2.6)

La suite `tests/test_algoritmos_p3.py` ejecuta cinco pruebas críticas:
1. `test_eliminacion_transiciones_lambda`: Aprobada.
2. `test_construccion_subconjuntos_y_determinismo`: Aprobada.
3. `test_minimizacion_hopcroft`: Aprobada.
4. `test_equivalencia_entre_automatas`: Aprobada.
5. `test_validador_por_lotes`: Aprobada.
Totalizando **100 % de éxito** sin regresión de los módulos de Práctica 1 y Práctica 2.

