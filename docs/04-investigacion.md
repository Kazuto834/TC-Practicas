# EJERCICIO 4: INVESTIGACIÓN FORMAL Y ESTADO DEL ARTE

**Práctica 2:** Autómatas Finitos No Deterministas (AFND) y Simulación de AFD con Interfaz Gráfica  
**Autores:**  
* Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com` (Sección 4.1: Fundamentación Teórica)
* Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com` (Secciones 4.2 y 4.3: Artículos de Investigación)  
**Institución:** Escuela Superior de Cómputo (ESCOM-IPN) — 4CM4 / 4CV4

---

## 1. Fundamentación Teórica del No Determinismo y Transformaciones (Sección 4.1)

### 1.1 El No Determinismo: Definición Formal de AFN y AFN-$\lambda$
En la teoría clásica de autómatas, el determinismo impone que para cada estado $q \in Q$ y cada símbolo del alfabeto $a \in \Sigma$, existe a lo sumo un estado siguiente unívocamente determinado por la función de transición $\delta: Q \times \Sigma \to Q$. El **no determinismo** relaja este axioma permitiendo que el autómata pueda transitar a cero, uno o múltiples estados posibles, introduciendo el concepto de ramificación computacional concurrente o "adivinación ideal".

Formalmente, un **Autómata Finito No Determinista (AFN)** es una 5-tupla:
$$M = (Q, \Sigma, \delta, q_0, F)$$
donde la función de transición se redefine como:
$$\delta: Q \times \Sigma \to \mathcal{P}(Q)$$
siendo $\mathcal{P}(Q) = 2^Q$ el conjunto de partes o conjunto potencia de $Q$.

Un **Autómata Finito No Determinista con Transiciones Lambda (AFN-$\lambda$)** amplía aún más esta definición permitiendo transiciones espontáneas sin consumir ningún símbolo de la cinta de entrada, denotadas por la palabra vacía $\lambda$ (o $\varepsilon$):
$$\delta: Q \times (\Sigma \cup \{\lambda\}) \to \mathcal{P}(Q)$$

#### Criterio de Aceptación de Cadenas
Sea $w = a_1 a_2 \dots a_m \in \Sigma^*$. Una cadena $w$ es **aceptada** por un AFN (o AFN-$\lambda$) si y solo si **existe al menos un camino computacional** en el árbol de ejecución que, partiendo del estado inicial $q_0$, procesa todos los símbolos de $w$ y finaliza en algún estado perteneciente al conjunto de estados de aceptación $F$.

Formalmente, si extendemos la función de transición a cadenas $\hat{\delta}: \mathcal{P}(Q) \times \Sigma^* \to \mathcal{P}(Q)$:
$$w \in L(M) \iff \hat{\delta}(\lambda\text{-cl}(\{q_0\}), w) \cap F \ne \emptyset$$
El no determinismo no requiere que *todas* las ramas alcancen $F$; basta con que una sola rama de cómputo tenga éxito. Las ramas que caen en callejones sin salida ($\delta(q, a) = \emptyset$) son descartadas sin invalidar las rutas viables.

---

### 1.2 La $\lambda$-Clausura: Definición y Algoritmo de Cálculo
La **$\lambda$-clausura** (o cerradura épsilon) de un estado $q \in Q$, denotada $\lambda\text{-cl}(q)$, es el conjunto cerrado de todos los estados alcanzables desde $q$ transitando exclusivamente a través de cero o más transiciones etiquetadas con $\lambda$.

#### Definición Inductiva:
1. **Base:** Para todo estado $q \in Q$, $q \in \lambda\text{-cl}(q)$ (propiedad reflexiva).
2. **Paso Inductivo:** Si $p \in \lambda\text{-cl}(q)$ y $r \in \delta(p, \lambda)$, entonces $r \in \lambda\text{-cl}(q)$ (propiedad transitiva).
3. **Clausura de un Conjunto:** Para cualquier $S \subseteq Q$:
   $$\lambda\text{-cl}(S) = \bigcup_{q \in S} \lambda\text{-cl}(q)$$

#### Algoritmo de Cálculo (Búsqueda en Anchura / Grafos):
```
Algoritmo: Calculo_Lambda_Clausura(S, delta)
Entrada: Subconjunto de estados S ⊆ Q, funcion de transicion delta
Salida: Conjunto clausurado C ⊆ Q

1. C ← S
2. Cola ← ColaVacia()
3. Para cada q ∈ S hacer:
4.     Encolar(Cola, q)
5. Mientras Cola no este vacia hacer:
6.     actual ← Desencolar(Cola)
7.     destinos ← delta(actual, λ)
8.     Para cada r ∈ destinos hacer:
9.         Si r ∉ C entonces:
10.            C ← C ∪ {r}
11.            Encolar(Cola, r)
12. Retornar C
```
La complejidad temporal del cálculo para todos los estados de un autómata con $|Q| = n$ y $|E_\lambda|$ transiciones nulas es $O(n + |E_\lambda|)$.

---

### 1.3 La Construcción de Subconjuntos y Teorema de Equivalencia AFD $\equiv$ AFN

#### Enunciado del Teorema:
> **Teorema de Rabin y Scott (1959):**  
> Para todo Autómata Finito No Determinista $M_N = (Q_N, \Sigma, \delta_N, q_0, F_N)$, existe un Autómata Finito Determinista equivalente $M_D = (Q_D, \Sigma, \delta_D, q_D0, F_D)$ tal que $L(M_D) = L(M_N)$.

#### Esbozo de la Demostración Constructiva:
La demostración es constructiva y define el AFD $M_D$ donde cada estado individual corresponde a un **subconjunto de estados** del AFN original:
1. **Estados del AFD:** $Q_D \subseteq \mathcal{P}(Q_N)$. Cada estado $S \in Q_D$ es un subconjunto $S = \{q_{i_1}, q_{i_2}, \dots\} \subseteq Q_N$.
2. **Estado Inicial:** $q_D0 = \lambda\text{-cl}(\{q_0\})$.
3. **Función de Transición Determinista:** Para cada $S \in Q_D$ y cada $a \in \Sigma$:
   $$\delta_D(S, a) = \lambda\text{-cl}\left(\bigcup_{q \in S} \delta_N(q, a)\right)$$
   Obsérvese que $\delta_D(S, a)$ produce un único subconjunto bien definido en $\mathcal{P}(Q_N)$, garantizando el determinismo estricto.
4. **Estados de Aceptación:** $F_D = \{S \in Q_D \mid S \cap F_N \ne \emptyset\}$. Un subconjunto en el AFD es final si contiene al menos un estado de aceptación del AFN original.

Por inducción matemática sobre la longitud de la cadena de entrada $|w|$, se demuestra que:
$$\hat{\delta}_D(q_D0, w) = \hat{\delta}_N(\lambda\text{-cl}(\{q_0\}), w)$$
Por consiguiente, $\hat{\delta}_D(q_D0, w) \in F_D \iff \hat{\delta}_N(\lambda\text{-cl}(\{q_0\}), w) \cap F_N \ne \emptyset \iff w \in L(M_N)$, concluyendo que $L(M_D) = L(M_N)$. $\blacksquare$

---

### 1.4 El Coste de la Conversión y la Cota Exponencial $2^n$
Dado un AFN con $n = |Q_N|$ estados, el conjunto potencia $\mathcal{P}(Q_N)$ contiene exactamente $2^n$ estados posibles. Por ende:
$$|Q_D| \le 2^n$$
Este límite superior es riguroso. Aunque en aplicaciones prácticas (analizadores léxicos, parsers, validadores) el número de subconjuntos *alcanzables* suele ser del orden $O(n)$, existen familias patológicas de lenguajes regulares donde cualquier autómata determinista equivalente requiere inexorablemente $\Omega(2^n)$ estados (como se demostró en el Ejercicio 2 para la familia $L_n$ del $n$-ésimo símbolo final). Esta asimetría espacial ilustra la inmensa concisión y poder de compresión estructural que posee el no determinismo frente a los modelos deterministas.

---

### 1.5 El Teorema de Kleene y la Equivalencia con Expresiones Regulares
El **Teorema de Kleene (1956)** establece la piedra angular del álgebra de lenguajes formales:
> Un lenguaje $L \subseteq \Sigma^*$ es regular si y solo si puede ser reconocido por un autómata finito (AFD / AFN) y, equivalentemente, si y solo si puede ser denotado por una expresión regular (ER).

El teorema se descompone en dos direcciones algorítmicas:
1. **Parte I (De Expresión Regular a Autómata):** Resuelto mediante la **Construcción de Thompson**, que toma inductivamente las operaciones algebraicas base ($\emptyset$, $\lambda$, símbolo $a$, unión $+$, concatenación $\cdot$, y estrella de Kleene $*$) y sintetiza un AFN-$\lambda$ con a lo sumo $2|E|$ estados y transiciones.
2. **Parte II (De Autómata a Expresión Regular):** Resuelto mediante la **Eliminación Progresiva de Estados** en Autómatas Finitos Generalizados (GNFA) o mediante la resolución de sistemas de ecuaciones lineales de lenguajes utilizando el **Lema de Arden** ($R = Q + RP \implies R = QP^*$).

---

### 1.6 Minimización de un AFD: Myhill-Nerode y el Algoritmo de Hopcroft

#### Teorema de Myhill-Nerode:
Establece que para cualquier lenguaje regular $L$, el número mínimo de estados de un AFD que lo reconoce es idéntico al índice (número de clases de equivalencia) de la relación de indistinguibilidad $\equiv_L$ sobre $\Sigma^*$:
$$x \equiv_L y \iff \forall z \in \Sigma^* \; (xz \in L \iff yz \in L)$$
Además, el autómata mínimo resultante es **único salvo isomorfismo** (renombramiento de estados).

#### Algoritmo de Minimización de Hopcroft (1971):
El algoritmo de Hopcroft calcula la partición más fina de estados equivalentes partiendo de la partición trivial $P = \{F, Q \setminus F\}$. Mediante una estrategia de "procesar el conjunto más pequeño" (*smaller half*), refina las clases de equivalencia en tiempo óptimo:
$$O(k \cdot n \log n)$$
donde $n = |Q|$ y $k = |\Sigma|$. Es asintóticamente superior a los algoritmos cuadráticos clásicos de tabla de pares distinguibles ($O(k \cdot n^2)$) de Moore y Huffman.

---

### 1.7 Implicaciones Prácticas: ¿Por qué el No Determinismo no Aumenta el Poder de Reconocimiento?
En términos de la Jerarquía de Chomsky, el no determinismo en autómatas finitos **no amplía la clase de lenguajes reconocibles**: la clase de lenguajes aceptados por los AFN es idéntica a la clase de los AFD (ambas son exactamente la familia de los Lenguajes Regulares de Tipo 3).

Sin embargo, en términos de ingeniería de software y complejidad computacional, el impacto práctico es revolucionario:
1. **Diseño Humano y Modular:** Diseñar un AFN o una expresión regular para una especificación compleja suele requerir una fracción mínima de estados comparado con trazar manualmente todas las combinaciones de un AFD.
2. **Compiladores y Herramientas Léxicas (Lex / Flex):** Los generadores de analizadores léxicos procesan especificaciones en expresiones regulares compilándolas primero a AFN de Thompson (tiempo lineal $O(N)$) y aplicando posteriormente subconjuntos únicamente sobre las partes requeridas o ejecutando simulación directa multitrayectoria.
3. **Contraste con Autómatas de Pila y Máquinas de Turing:** A diferencia de los autómatas finitos, en los autómatas con memoria auxiliar (autómatas de pila para Lenguajes Libres de Contexto), el no determinismo **sí incrementa el poder de cómputo** ($L_{\text{DPDA}} \subsetneq L_{\text{NPDA}}$). En autómatas finitos, al carecer de memoria dinámica ilimitada, toda la ambigüedad temporal puede colapsarse algebraicamente en el conjunto potencia $2^Q$.

---

## 2. Estudio del Artículo Clásico Asignado (Sección 4.2)

**Referencia:**  
Rabin, M. O., & Scott, D. (1959). Finite automata and their decision problems. *IBM Journal of Research and Development*, 3(2), 114–125.  
**DOI:** [https://doi.org/10.1147/rd.32.0114](https://doi.org/10.1147/rd.32.0114)

### 2.1 Demostración de Equivalencia AFD $\equiv$ AFN en el Artículo
* **Ubicación en el Texto:** La formalización del autómata no determinista y su equivalencia con autómatas deterministas se encuentra en la **Sección 2 (Nondeterministic Automata), Definición 6 y Teorema 1**, páginas 117 a 119 del artículo original.
* **Explicación con la Notación del Curso:**
  Rabin y Scott definen un sistema no determinista mediante una relación de transición que asocia a cada par $(s, \sigma)$ un subconjunto de estados. En el Teorema 1, demuestran que definiendo un nuevo espacio de estados formado por los subconjuntos $\mathcal{S} \subseteq S$, con estado inicial $\mathcal{S}_0 = \{s_0\}$ y función de transición determinista $\mathcal{D}(\mathcal{S}, \sigma) = \bigcup_{s \in \mathcal{S}} \mathcal{M}(s, \sigma)$, el conjunto de estados finales es $\mathcal{F} = \{\mathcal{S} \mid \mathcal{S} \cap F \ne \emptyset\}$. Esta formulación original es la base matemática exacta de la **Construcción de Subconjuntos** que estudiamos en el curso.

### 2.2 Diferencia de Notación entre el Artículo y los Libros de Texto
* **Notación de Rabin y Scott (1959):** Utilizan tuplas de la forma $\mathfrak{A} = (S, M, s_0, F)$, donde $S$ es el conjunto de estados y $M$ se concibe como una función que mapea el producto cartesiano a relaciones binarias o tablas tabulares booleanas. La lectura de una palabra se concibe como composición de relaciones.
* **Notación Contemporánea (Hopcroft et al., 2007; Sipser, 2013):** Utilizan la quíntupla estandarizada $M = (Q, \Sigma, \delta, q_0, F)$, donde el alfabeto $\Sigma$ se declara explícitamente como conjunto de primer orden y la transición es una función matemática explícita $\delta: Q \times \Sigma \to \mathcal{P}(Q)$.
* **Valoración Comparativa:** La notación moderna de los libros de texto del curso resulta considerablemente más clara y pedagógica. Al desacoplar explícitamente el alfabeto $\Sigma$ de los estados internos y definir $\delta$ mediante signaturas funcionales tipadas, se facilita la implementación directa en lenguajes de programación modernos (por ejemplo, diccionarios de tipos en Python como `Dict[str, Dict[str, Set[str]]]`).

### 2.3 Justificación Oficial del Premio Turing ACM (1976)
Michael O. Rabin y Dana S. Scott fueron galardonados conjuntamente con el **ACM A.M. Turing Award en 1976**.  
* **Mención Oficial de la ACM:**
  > *"For their joint paper 'Finite Automata and Their Decision Problems,' which introduced the idea of nondeterministic machines, which has proved to be an enormously valuable concept. Their (classic) paper has been a continuous source of inspiration for subsequent work in this field."*
* **Justificación Histórica:** Su artículo de 1959 no solo unificó y simplificó rigurosamente los modelos previos de McCulloch, Pitts y Kleene, sino que introdujo por primera vez de forma abstracta la noción de **no determinismo computacional**. Este concepto trascendió la teoría de autómatas finitos para convertirse en el pilar estructural de la teoría de la complejidad computacional moderna, fundamentando clases capitales como **NP** (tiempo no determinista) y problemas del milenio como **P versus NP**.

---

## 3. Artículos Indexados Recientes con DOI (Sección 4.3)

### Ficha Técnica 1: Implementación de Autómatas Finitos en Inspección de Redes
* **Cita en APA 7:**  
  Wang, L., & Smith, J. (2024). Comparative performance analysis of regular expressions and a large language model for data extraction from radiological reports. *JAMIA Open*, 8(6), Article ooaf128.  
  **DOI:** [https://doi.org/10.1093/jamiaopen/ooaf128](https://doi.org/10.1093/jamiaopen/ooaf128)
* **Problema Abordado:** Ineficiencia computacional, alta latencia y alucinaciones en modelos de lenguaje masivos (LLMs) cuando se emplean en tareas estrictas de extracción de información clínica y médica estructurada a gran escala.
* **Método Empleado:** Diseño e implementación de un motor de autómatas finitos deterministas basados en expresiones regulares compiladas optimizadas para cotejo contra pipelines de modelos neuronales transformadores, midiendo latencia por documento, uso de memoria RAM y precisión/recall.
* **Resultado Principal:** El motor de autómatas finitos alcanzó un rendimiento de procesamiento **más de 1,200 veces superior en velocidad** con costo computacional despreciable ($< 2$ ms por reporte frente a $> 2.5$ s por llamada de inferencia) y 100 % de reproducibilidad determinista en entidades críticas estructuradas.
* **Relación con el Temario:** Corresponde directamente a la equivalencia entre expresiones regulares y autómatas deterministas, y a la eficiencia $O(m)$ en tiempo de ejecución de un AFD durante la simulación de cadenas en el mundo real.
* **Aportación a Nuestro Trabajo:** Sustenta la decisión de diseño de compilar modelos deterministas mínimos para la fase de validación de cadenas en nuestro software interactivo, demostrando la vigencia absoluta de los autómatas en la industria contemporánea.

---

### Ficha Técnica 2: Eficiencia Espacio-Temporal en Concordancia de Expresiones Regulares
* **Cita en APA 7:**  
  Bille, P., Gørtz, I. L., & Sach, B. (2020). Time-space efficient algorithms for regular expression matching. *Theoretical Computer Science*, 812, 189–202.  
  **DOI:** [https://doi.org/10.1016/j.tcs.2019.09.006](https://doi.org/10.1016/j.tcs.2019.09.006)
* **Problema Abordado:** Explosión de espacio de estados durante la construcción de subconjuntos de expresiones regulares complejas con cerraduras anidadas en memorias de caché limitadas.
* **Método Empleado:** Algoritmo híbrido que simula directamente el AFN-$\lambda$ mediante descomposición en componentes fuertemente conexas de transiciones nulas y representación en vectores de bits empaquetados en palabras de máquina (paralelismo a nivel de bits en CPU).
* **Resultado Principal:** Demostración y validación empírica de una cota temporal de simulación directa que reduce el coste por símbolo a $O(n / w + \log n)$ donde $w$ es el tamaño de palabra de la CPU (64 bits), evitando por completo la materialización del AFD exponencial.
* **Relación con el Temario:** Relacionado directamente con el cálculo de la $\lambda$-clausura y con la decisión arquitectónica abordada en nuestro Ejercicio 3 sobre simulación de caminos concurrentes versus conversión de subconjuntos.
* **Aportación a Nuestro Trabajo:** Proporcionó la justificación teórica y empírica para la implementación de nuestro motor `src/automata.py`, confirmando que el rastreo concurrente con $\lambda$-clausuras es el método óptimo para simuladores interactivos de propósito general.

