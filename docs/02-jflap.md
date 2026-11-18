# EJERCICIO 2: AFND Y AFND-$\lambda$ EN JFLAP Y CONVERSIONES

**Práctica 2:** Autómatas Finitos No Deterministas (AFND) y Simulación de AFD con Interfaz Gráfica  
**Autores:**  
* Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com` (Ejercicios Impares)
* Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com` (Ejercicios Pares y Conversiones)  
**Institución:** Escuela Superior de Cómputo (ESCOM-IPN) — 4CM4 / 4CV4

---

## 1. Clasificación y Cobertura (Sección 2.1)

Se clasifican formalmente los ejercicios de la **Lista 2 (94 a 150)** y de la **Lista 3 (151 a 263)** en tres categorías fundamentales: **AFD** (Autómata Finito Determinista), **AFND** (Autómata Finito No Determinista estándar) y **AFND-$\lambda$** (Autómata Finito No Determinista con transiciones vacías).

### 1.1 Cobertura de la Lista 2 (Ejercicios Representativos 94 a 150)

| Ejercicio | Clasificación | Justificación Teórica en una Línea |
| :---: | :---: | :--- |
| **97** | **AFD** | Para cada estado y símbolo $\{0,1,2\}$ existe una única transición determinista que cuenta módulo 3. |
| **99** | **AFD** | Reconocedor secuencial con retrocesos deterministas al prefijo más largo del patrón `001001`. |
| **102** | **AFD** | Detector determinista de subcadena `abbbab` con sumidero de aceptación final. |
| **103** | **AFD** | Reconocedor secuencial determinista de subcadena `aabbba` con bucle absorbente final. |
| **106** | **AFD** | Autómata de 8 estados con transiciones deterministas que reinicia ante el símbolo '2'. |
| **107** | **AFD** | Estructura en dos vías paralelas deterministas para detectar permutación de subcadenas `0101` y `021`. |
| **111** | **AFD** | Conteo determinista de exactamente tres ocurrencias de `01002` con paso a estado sumidero al cuarto. |
| **112** | **AFD** | Control determinista de dos bloques no traslapados de `010` mediante estado de espera intermedio. |
| **113** | **AFD** | Control determinista de dos bloques traslapados de `010` reutilizando el '0' final como inicial del segundo. |
| **118** | **AFD** | Validación determinista de prefijo 'a', secuencia central 'ab' y sufijo 'a' con sumidero de rechazo. |
| **120** | **AFD** | Memorización determinista del primer símbolo leído en 3 pistas disjuntas comparado con el último. |
| **121** | **AFD** | Procesamiento determinista en ciclos estrictos de 3 saltos exigiendo al menos un cero por bloque. |
| **122** | **AFD** | Conteo determinista de rachas de símbolos distintos de cero con cota máxima de 2 antes de sumidero. |
| **123** | **AFD** | Ramificación determinista de 4 vías para memorizar prefijo de longitud 2 y cotejar sufijo idéntico. |
| **124** | **AFD** | Modelo determinista de 8 configuraciones físicas de palancas mecánicas binarias ($2^3=8$). |
| **128** | **AFD** | Autómata determinista de 6 estados que reconoce cadenas de $L$ omitiendo su último carácter. |
| **131** | **AFD** | Dos estados deterministas donde leer '1' conduce a aceptación y '0' a rechazo. |
| **133** | **AFD** | Función de transición completa y determinista de 4 estados sobre $\{a, b\}$. |
| **135** | **AFD** | Reconocedor determinista de $b^m a b^n$ ($m,n > 0$) con verificación de una única 'a'. |
| **137** | **AFD** | Control determinista de prefijo estricto 'ab' con desvío a trampa si falla el inicio. |
| **139** | **AFD** | Contador de paridad de ceros con 2 estados deterministas invariantes ante la lectura de '1'. |
| **141** | **AFD** | Exigencia determinista de que todo '0' sea seguido inmediatamente por '1' sin ceros consecutivos. |
| **143 (a)**| **AFD** | Un único estado que buclea sobre $\{a, b\}$ aceptando el lenguaje universal $\Sigma^*$. |
| **143 (b)**| **AFND** | En $q_1$ existen múltiples opciones de transición para el símbolo 'b' (bucle propio y retorno a $q_0$). |
| **145** | **AFD** | Aritmética modular inversa que reconoce múltiplos binarios de 5 leídos de derecha a izquierda. |
| **147** | **AFD** | 6 estados deterministas que calculan $(2 \cdot \text{estado} + \text{bit}) \pmod 6$ de izquierda a derecha. |
| **148** | **AFD** | Modelo determinista del historial académico de convocatorias de la ESCOM con cota de 2 intentos. |
| **149** | **AFD** | Tabla de transiciones de 3 estados con transiciones deterministas sobre $\{0, 1\}$. |
| **150** | **AFD** | Tabla de transiciones de 4 estados con transiciones deterministas sobre $\{0, 1, a\}$. |

### 1.2 Cobertura de la Lista 3 (Ejercicios Representativos 151 a 263)

| Ejercicio | Clasificación | Justificación Teórica en una Línea |
| :---: | :---: | :--- |
| **151 a 157** | **AFD** | Autómatas deterministas de entrada sujetos al proceso de minimización por partición de estados equivalentes. |
| **158** | **AFND** | Reconocedor lineal sin transiciones para símbolos no esperados, modelando aceptación de únicamente `"01"`. |
| **159** | **AFND** | Bucle no determinista en $q_1$ con '1' que adivina cuándo iniciar la secuencia final `"01"`. |
| **160** | **AFND** | Prefijo determinista inicial `"01"` y bucle final en $q_3$ con $\{0, 1\}$ como sumidero no determinista. |
| **161** | **AFND** | Retorno cíclico no determinista con '0' para aceptar repeticiones del bloque `"010"`. |
| **189** | **AFND** | Bifurcación no determinista desde $q_0$ para adivinar si la subcadena presente es `00101` o `00110`. |
| **190** | **AFND** | Ramificación concurrente en dos ramas paralelas para reconocer simultáneamente `11010` y `10100`. |
| **191 a 195**| **AFND** | Tablas de transiciones con transiciones múltiples $\delta(q, a) \in \mathcal{P}(Q)$ evaluadas por subconjuntos. |
| **196 a 200**| **AFND-$\lambda$**| Autómatas construidos con transiciones nulas $\lambda$ para conectar subexpresiones regulares. |
| **260** | **AFND** | Autómata no determinista con estados $\{A, B, C, D, E\}$ y transiciones múltiples convertido a AFD. |
| **261** | **AFND** | Grafo no determinista con bucles concurrentes en $q_0$ convertido a AFD mediante subconjuntos. |
| **262** | **AFND** | Bifurcación no determinista desde $q_0$ para aceptar la unión de palabras disjuntas $\{ab, ba\}$. |
| **263** | **AFND** | Modelo estándar con bucle en $q_0$ con $\{0, 1\}$ y avance a $q_1 \xrightarrow{1} q_2$ para cadenas que terminan en `01`. |

---

## 2. Diseño, Validación y Trazas Paso a Paso (Sección 2.2)

### Caso 1: AFND del Ejercicio 189 (Subcadenas `00101` o `00110`)
* **Proceso de Diseño:** El autómata mantiene un bucle en $q_0$ con $\{0, 1\}$. Cuando lee `001`, bifurca de manera no determinista: la rama superior busca completar `01` y la inferior `10`, confluyendo ambas en el estado de aceptación $q_6$.
* **Cinco Cadenas Válidas Probadas:**
  1. `00101`: Recorrido directo $q_0 \xrightarrow{0} q_1 \xrightarrow{0} q_2 \xrightarrow{1} q_3 \xrightarrow{0} q_5 \xrightarrow{1} q_6$ (Aceptada).
  2. `00110`: Recorrido directo $q_0 \xrightarrow{0} q_1 \xrightarrow{0} q_2 \xrightarrow{1} q_3 \xrightarrow{1} q_4 \xrightarrow{0} q_6$ (Aceptada).
  3. `1001011`: Prefijo inerte $q_0 \xrightarrow{1} q_0$, seguido del camino exitoso hacia $q_6$, finalizando en bucle $q_6 \xrightarrow{1} q_6$ (Aceptada).
  4. `0001100`: Prefijo extra absorbido en $q_0$, bifurcación exitosa por la rama `00110` (Aceptada).
  5. `111001010`: Múltiples unos iniciales, detección de `00101` y absorción del cero final en $q_6$ (Aceptada).
* **Cinco Cadenas Inválidas Probadas:**
  1. `""`: Se queda en $q_0 \notin F$ (Rechazada).
  2. `001`: Termina en $\{q_0, q_3\} \cap F = \emptyset$ (Rechazada).
  3. `00111`: Ramas mueren antes de alcanzar $q_6$ (Rechazada).
  4. `010101`: Nunca forma el prefijo de doble cero inicial `001` (Rechazada).
  5. `1010101`: No contiene ni `00101` ni `00110` (Rechazada).

---

## 3. Transiciones Lambda y $\lambda$-Clausuras (Sección 2.3)

### 3.1 Necesidad y Ubicación de las Transiciones $\lambda$
Las transiciones nulas permiten modularizar la construcción de autómatas complejos dividiendo el problema en sub-autómatas independientes (construcción inductiva de Thompson):
1. **Unión de Lenguajes ($L_1 \cup L_2$):** Un nuevo estado inicial bifurca con $\lambda$ hacia los estados iniciales de $M_1$ y $M_2$ sin consumir símbolos.
2. **Concatenación ($L_1 \cdot L_2$):** Los estados finales de $M_1$ se conectan con $\lambda$ hacia el inicial de $M_2$.
3. **Cerradura de Kleene ($L^*$):** Se agrega un atajo $\lambda$ del estado inicial al final para aceptar la palabra vacía, y un retorno $\lambda$ del final al inicial del bloque para permitir iteraciones sucesivas.

### 3.2 Cálculo de $\lambda$-Clausuras en el Autómata del Anexo 3
* **Definición Formal:**
  $$\lambda\text{-cl}(q) = \{q\} \cup \{p \in Q \mid \text{existe un camino de } q \text{ a } p \text{ etiquetado únicamente con } \lambda\}$$
* **Valores Calculados:**
  * $\lambda\text{-cl}(q_0) = \{q_0, q_1\}$ (debido a la transición nula directa $q_0 \xrightarrow{\lambda} q_1$).
  * $\lambda\text{-cl}(q_1) = \{q_1\}$ (no posee transiciones $\lambda$ salientes).
* **Impacto en el Reconocimiento:** Al iniciar la simulación, el conjunto de estados activos es inmediatamente $\lambda\text{-cl}(q_0) = \{q_0, q_1\}$. Como $q_1 \in F$, el autómata acepta automáticamente la cadena vacía $\lambda$, y ante cualquier entrada, mantiene activo a $q_1$ en paralelo con $q_0$.

---

## 4. Conversiones y Análisis Comparativo (Sección 2.4)

### 4.1 Tabla Comparativa de 5 Casos de Conversión AFND $\to$ AFD

| Caso / Ejercicio | Lenguaje Reconocido | Estados AFND ($n$) | Estados AFD Resultante ($|Q_D|$) | Cota Máxima $2^n$ | Relación $|Q_D| / 2^n$ |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **AFND 192** | Lenguaje sobre $\{0, 1\}$ | 3 | 6 | $2^3 = 8$ | 75.0 % |
| **AFND 193** | Lenguaje sobre $\{0, 1\}$ | 4 | 8 | $2^4 = 16$ | 50.0 % |
| **AFND 262** | Lenguaje $\{ab, ba\}$ | 5 | 6 | $2^5 = 32$ | 18.7 % |
| **AFND 263** | Cadenas que terminan en `01` | 3 | 3 | $2^3 = 8$ | 37.5 % |
| **Anexo 3** | AFND-$\lambda$ sobre $\{a, b\}$ | 2 | 1 | $2^2 = 4$ | 25.0 % |

### 4.2 Por qué rara vez se alcanza la cota $2^n$
La cota teórica $2^n$ representa el número de todos los subconjuntos posibles del conjunto de partes $\mathcal{P}(Q)$. En la inmensa mayoría de los sistemas prácticos y lenguajes regulares:
1. **Inalcanzabilidad Estructural:** Gran parte de los subconjuntos teóricos nunca pueden activarse simultáneamente partiendo del estado inicial $q_0$ (por ejemplo, estados que pertenecen a fases mutualmente excluyentes de un protocolo o ramas disjuntas).
2. **Equivalencia de Comportamiento:** Muchos subconjuntos alcanzables se fusionan de forma natural durante la minimización al presentar exactamente las mismas funciones de transición hacia el futuro.

### 4.3 Familia de Lenguajes donde la Cota $2^n$ se Alcanza Exactamente
Tomada de la literatura canónica (Hopcroft et al., 2007, Sección 2.3.6; Sipser, 2013, Ejemplo 1.43), consideremos la familia de lenguajes sobre $\Sigma = \{0, 1\}$:
$$L_n = \{w \in \{0, 1\}^* \mid \text{el } n\text{-ésimo símbolo desde el final de } w \text{ es } 1\}$$

* **Tamaño del AFND:** Un AFND solo requiere **$n + 1$ estados**. El estado $q_0$ posee un bucle $q_0 \xrightarrow{0,1} q_0$ que "adivina" de forma no determinista cuándo se lee el símbolo '1' que se encuentra a distancia $n$ del final; tras esa decisión, el autómata avanza rígidamente $n$ pasos secuenciales hacia el estado de aceptación $q_n$.
* **Tamaño del AFD:** Cualquier AFD determinista que reconozca $L_n$ requiere **exactamente $2^n$ estados**.
  * *Demostración Formal (por Distinguibilidad de Myhill-Nerode):* Consideremos dos cadenas binarias distintas $x, y \in \{0, 1\}^n$. Como $x \ne y$, deben diferir en alguna posición $i$ ($1 \le i \le n$). Sea $z = 0^{i-1}$. Al concatenar $z$, el $n$-ésimo símbolo desde el final de $xz$ es el $i$-ésimo símbolo de $x$, mientras que en $yz$ es el $i$-ésimo símbolo de $y$. Dado que uno es '1' y el otro '0', exactamente una de las dos cadenas $xz$ o $yz$ pertenece a $L_n$. Por tanto, todas las $2^n$ cadenas binarias de longitud $n$ son mutuamente distinguibles respecto a $L_n$, obligando a cualquier AFD a disponer de al menos $2^n$ estados distintos para recordarlas.

