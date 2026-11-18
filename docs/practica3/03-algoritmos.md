# DOCUMENTACIÓN FORMAL DE ALGORITMOS (PRÁCTICA 3)

**Unidad de Aprendizaje:** Teoría de la Computación  
**Institución:** Instituto Politécnico Nacional — Escuela Superior de Cómputo (ESCOM)  
**Programa Académico:** Ingeniería en Sistemas Computacionales  
**Norma de Citación:** APA 7.ª Edición  
**Propósito:** Especificación teórica, pseudocódigo, correspondencia modular, ejemplos resueltos por software y estimación de complejidad de los algoritmos implementados en el Ejercicio 2.

---

## 1. Algoritmo 1: Cálculo de Cerradura $\lambda$ y Simulación Directa de AFN-$\lambda$

### 1.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un Autómata Finito No Determinista con transiciones vacías $M = (Q, \Sigma, \delta, q_0, F)$, determinar para cualquier conjunto $S \subseteq Q$ todos los estados alcanzables transitivamente sin consumir símbolos ($\lambda$-clausura), y simular la aceptación de una cadena $w \in \Sigma^*$ paso a paso sin requerir su conversión previa a un AFD.
* **Respaldo Teórico:**
  * **Hopcroft, Motwani, & Ullman (2007), Sección 2.5.5:** Formalización de la cerradura-épsilon ($\epsilon\text{-closure}$) como clausura reflexiva y transitiva sobre relaciones de transición nula.
  * **Thompson (1968), DOI: [10.1145/363347.363387](https://doi.org/10.1145/363347.363387):** Algoritmo clásico de simulación en línea mediante seguimiento de conjuntos de estados activos en tiempo $O(n \cdot |w|)$.
  * **Bille, Gørtz, & Sach (2020), DOI: [10.1016/j.tcs.2019.09.006](https://doi.org/10.1016/j.tcs.2019.09.006):** Modelos eficientes de memoria y evaluación de caminos concurrentes en autómatas finitos.
* **Axiomas Matemáticos:**
  $$\lambda\text{-cl}(S) = S \cup \{ p \in Q \mid \exists q \in S, \text{ camino } q \xrightarrow{\lambda^*} p \}$$
  $$\text{Activos}_0 = \lambda\text{-cl}(\{q_0\}), \quad \text{Activos}_i = \lambda\text{-cl}\left(\bigcup_{q \in \text{Activos}_{i-1}} \delta(q, w_i)\right)$$
  $$w \in L(M) \iff \text{Activos}_{|w|} \cap F \neq \emptyset$$

### 1.2 Pseudocódigo y Correspondencia Modular
```text
Función Calcular_Cerradura_Lambda(M, estado):
    clausura ← { estado }
    cola ← Cola([estado])
    Mientras cola no esté vacía:
        actual ← cola.desencolar()
        Para cada destino en M.transiciones_lambda(actual):
            Si destino ∉ clausura:
                clausura.agregar(destino)
                cola.encolar(destino)
    Retornar clausura

Función Simular_AFN_Lambda_Directo(M, cadena):
    activos ← Calcular_Cerradura_Lambda(M, M.q0)
    Para cada símbolo char en cadena:
        directos ← Unión(delta(q, char) para q en activos)
        activos ← Cerradura_Lambda_Conjunto(M, directos)
        Si activos está vacío:
            Retornar (Falso, traza_bloqueo)
    Retornar ((activos ∩ M.F ≠ ∅), traza)
```
* **Correspondencia Modular:**
  * Archivo `src/cerradura_lambda.py`: función `calcular_cerradura_lambda(auto, estado=None)`.
  * Archivo `src/simulacion_directa.py`: función `simular_afn_lambda_directo(auto, cadena)`.

### 1.3 Ejemplo Resuelto por el Software
* **Autómata Evaluado:** Ejercicio 199 de la Lista 3 (`automatas/practica3/casos-de-prueba/199.jff`), donde $Q = \{q0, q1, q2, q3, q4\}$, $q0$ inicial, $F = \{q4\}$ y $\Sigma = \{0, 1\}$.
* **Transiciones $\lambda$ registradas:** $q0 \xrightarrow{\lambda} q1$, $q1 \xrightarrow{\lambda} q2$, $q2 \xrightarrow{\lambda} q4$.
* **Paso a paso de $\lambda$-clausura calculado:**
  * $\lambda\text{-cl}(q0) = \{q0, q1, q2, q4\}$.
  * $\lambda\text{-cl}(q1) = \{q1, q2, q4\}$.
  * $\lambda\text{-cl}(q2) = \{q2, q4\}$.
  * $\lambda\text{-cl}(q3) = \{q3\}$.
  * $\lambda\text{-cl}(q4) = \{q4\}$.
* **Simulación directa de la cadena `w = "01"`:**
  * **Paso 0:** Antes de $\lambda$-cl: $\{q0\}$; Después de $\lambda$-cl: $\{q0, q1, q2, q4\}$ (Estado de aceptación activo porque $q4 \in F$).
  * **Paso 1 (lee '0'):** Transiciones directas tomadas desde $\{q0, q1, q2, q4\}$ con '0' $\to$ Destinos directos: $\{q0, q3\}$.  
    Aplicación de $\lambda$-clausura: $\lambda\text{-cl}(\{q0, q3\}) = \{q0, q1, q2, q3, q4\}$ (Activo final).
  * **Paso 2 (lee '1'):** Transiciones directas desde $\{q0, q1, q2, q3, q4\}$ con '1' $\to$ Destinos directos: $\{q1, q4\}$.  
    Aplicación de $\lambda$-clausura: $\lambda\text{-cl}(\{q1, q4\}) = \{q1, q2, q4\}$.
  * **Resultado final:** Aceptada (ya que $\{q1, q2, q4\} \cap \{q4\} = \{q4\} \neq \emptyset$).

### 1.4 Estimación de Complejidad
* **Número de Estados:** $|Q| = n$.
* **Tamaño del Alfabeto:** $|\Sigma| = k$, longitud de cadena $m = |w|$.
* **Número de Transiciones $\lambda$:** $|E_\lambda| \le n^2$.
* **Cálculo de $\lambda$-clausura:** Recorrido BFS sobre transiciones vacías: $O(n + |E_\lambda|)$. Para los $n$ estados: $O(n^2 + n|E_\lambda|)$.
* **Simulación por paso:** Para cada símbolo, unión de transiciones $O(n)$ más clausura $O(n + |E_\lambda|)$.
* **Complejidad Temporal Total:** $O(m \cdot (n + |E_\lambda|))$.

---

## 2. Algoritmo 2: Eliminación de Transiciones Lambda

### 2.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFN-$\lambda$ $M = (Q, \Sigma, \delta, q_0, F)$, construir un AFN equivalente $M' = (Q, \Sigma, \delta', q_0, F')$ que no contenga ninguna transición vacía ($\lambda$), identificando con rigor las transiciones añadidas y los estados promovidos a aceptación.
* **Respaldo Teórico:**
  * **Hopcroft, Motwani, & Ullman (2007), Sección 2.5.5:** Demostración constructiva de eliminación de transiciones vacías sin alterar la clase regular del lenguaje.
  * **Linz (2016), Teorema 2.2:** Teorema de equivalencia formal entre autómata con movimientos nulos y autómata estándar sin transiciones nulas.
  * **Ilie & Yu (2003), DOI: [10.1016/S0304-3975(02)00843-7](https://doi.org/10.1016/S0304-3975(02)00843-7):** Reducción estructural y preservación exacta de lenguajes regulares en AFN.
* **Axiomas Matemáticos:**
  $$\delta'(q, a) = \lambda\text{-cl}\left(\delta(\lambda\text{-cl}(q), a)\right), \quad \forall q \in Q, \; \forall a \in \Sigma$$
  $$F' = \{ q \in Q \mid \lambda\text{-cl}(q) \cap F \neq \emptyset \}$$
  $$q_0' = q_0$$

### 2.2 Pseudocódigo y Correspondencia Modular
```text
Función Eliminar_Transiciones_Lambda(M):
    F_nuevo ← ConjuntoVacío()
    Para cada q en M.Q:
        Si Cerradura_Lambda(M, q) ∩ M.F ≠ ∅:
            F_nuevo.agregar(q)
            Registrar_Promoción_Aceptación(q)

    delta_nuevo ← Diccionario()
    Para cada q en M.Q:
        C_q ← Cerradura_Lambda(M, q)
        Para cada a en M.Sigma:
            destinos_directos ← Mover(C_q, a)
            destinos_finales ← Cerradura_Lambda_Conjunto(M, destinos_directos)
            Para cada d en destinos_finales:
                delta_nuevo.agregar(q, a, d)
                Si (q, a, d) no existía en M:
                    Registrar_Transición_Añadida(q, a, d)

    Retornar M'(Q=M.Q, Sigma=M.Sigma, delta=delta_nuevo, q0=M.q0, F=F_nuevo)
```
* **Correspondencia Modular:**
  * Archivo `src/eliminacion_lambda.py`: funciones `eliminar_transiciones_lambda(auto)` y `transformar_afn_sin_lambda_detallado(auto)`.

### 2.3 Ejemplo Resuelto por el Software
* **Autómata Evaluado:** Ejercicio 199 (`automatas/practica3/casos-de-prueba/199.jff`).
* **Estados Originales:** $Q = \{q0, q1, q2, q3, q4\}$, $F = \{q4\}$.
* **Estados Promovidos a Aceptación:**
  * $q0$ pasa a ser de aceptación porque $\lambda\text{-cl}(q0) \cap F = \{q4\} \neq \emptyset$.
  * $q1$ pasa a ser de aceptación porque $\lambda\text{-cl}(q1) \cap F = \{q4\} \neq \emptyset$.
  * $q2$ pasa a ser de aceptación porque $\lambda\text{-cl}(q2) \cap F = \{q4\} \neq \emptyset$.
  * Conjunto resultante $F' = \{q0, q1, q2, q4\}$.
* **Transiciones Añadidas Identificadas por el Software:**
  * Desde $q0$ con '0': se añaden transiciones a $q1, q2, q4$.
  * Desde $q1$ con '1': se añaden transiciones a $q2, q4$.
  * Autómata resultante: 0 transiciones $\lambda$, conservando exactamente las mismas palabras aceptadas (`""`, `"0"`, `"1"`, `"01"`, etc.).

### 2.4 Estimación de Complejidad
* **Número de Estados:** $n = |Q|$.
* **Tamaño del Alfabeto:** $k = |\Sigma|$.
* **Pasos para $F'$:** $n$ evaluaciones de intersección de clausuras: $O(n \cdot (n + |E_\lambda|))$.
* **Pasos para $\delta'$:** Para cada uno de los $n$ estados y cada uno de los $k$ símbolos, se realiza un cálculo de transiciones directas y una clausura: $O(n \cdot k \cdot (n + |E_\lambda|))$.
* **Complejidad Temporal:** $O(k \cdot n^2 + k \cdot n \cdot |E_\lambda|)$. En el peor caso con grafos densos de transiciones nulas: $O(k \cdot n^3)$.

---

## 3. Algoritmo 3: Construcción de Subconjuntos (AFN $\to$ AFD)

### 3.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFN o AFN-$\lambda$ $M_N = (Q_N, \Sigma, \delta_N, q_0, F_N)$, sintetizar un AFD equivalente $M_D = (Q_D, \Sigma, \delta_D, S_0, F_D)$ explorando exclusivamente los subconjuntos alcanzables desde el estado inicial, mostrando la tabla de transiciones conforme se genera y justificando qué subconjuntos son de aceptación.
* **Respaldo Teórico:**
  * **Rabin & Scott (1959), Teorema 1, DOI: [10.1147/rd.32.0114](https://doi.org/10.1147/rd.32.0114):** Demostración seminal del teorema de equivalencia entre autómatas deterministas y no deterministas (Premio Turing ACM 1976).
  * **Hopcroft, Motwani, & Ullman (2007), Sección 2.3.5:** Formalización del algoritmo sistemático de construcción de subconjuntos (*The Subset Construction*).
  * **Sipser (2013), Teorema 1.39:** Demostración de equivalencia constructiva entre AFN y AFD.
* **Axiomas Matemáticos:**
  $$S_0 = \lambda\text{-cl}(\{q_0\})$$
  $$\delta_D(S, a) = \lambda\text{-cl}\left(\bigcup_{p \in S} \delta_N(p, a)\right), \quad \forall S \subseteq Q_N, \; \forall a \in \Sigma$$
  $$F_D = \{ S \in Q_D \mid S \cap F_N \neq \emptyset \}$$

### 3.2 Pseudocódigo y Correspondencia Modular
```text
Función Construccion_Subconjuntos(M_N):
    S0 ← Cerradura_Lambda({M_N.q0})
    Q_D ← { S0 }
    cola ← Cola([S0])
    tabla_transiciones ← Lista()

    Mientras cola no esté vacía:
        S ← cola.desencolar()
        fila ← { "subconjunto": S }
        Para cada a en M_N.Sigma:
            destinos_directos ← Mover(S, a)
            U ← Cerradura_Lambda(destinos_directos)
            fila[a] ← U
            Si U ∉ Q_D:
                Q_D.agregar(U)
                cola.encolar(U)
                es_final ← (U ∩ M_N.F ≠ ∅)
                Registrar_Justificación_Aceptación(U, es_final)
            delta_D.agregar(S, a, U)
        tabla_transiciones.agregar(fila)

    Retornar AFD(Q_D, Sigma, delta_D, S0, F_D)
```
* **Correspondencia Modular:**
  * Archivo `src/construccion_subconjuntos.py`: funciones `construccion_subconjuntos(auto)` y `construccion_subconjuntos_detallada(auto)`.

### 3.3 Ejemplo Resuelto por el Software
* **Autómata Evaluado:** Ejercicio 192 de la Lista 3 (`automatas/practica3/casos-de-prueba/192.jff`), $Q_N = \{q0, q1, q2\}$, $\Sigma = \{0, 1\}$, $q_0 = q0$, $F_N = \{q2\}$.
* **Generación Paso a Paso de Subconjuntos Alcanzables:**
  * **Inicial:** $S_0 = \{q0\}$. No contiene a $q2 \implies$ no es de aceptación.
  * **Desde $\{q0\}$:**
    * Con '0' transita a $\{q0, q1\}$. Subconjunto nuevo. No contiene a $q2 \implies$ no final.
    * Con '1' transita a $\{q0\}$. Ya conocido.
  * **Desde $\{q0, q1\}$:**
    * Con '0' transita a $\{q0, q1, q2\}$. Subconjunto nuevo. Contiene a $q2 \in F_N \implies$ **Estado de Aceptación**.
    * Con '1' transita a $\{q0, q2\}$. Subconjunto nuevo. Contiene a $q2 \in F_N \implies$ **Estado de Aceptación**.
  * **Desde $\{q0, q1, q2\}$:**
    * Con '0' transita a $\{q0, q1, q2\}$.
    * Con '1' transita a $\{q0, q2\}$.
  * **Desde $\{q0, q2\}$:**
    * Con '0' transita a $\{q0, q1\}$.
    * Con '1' transita a $\{q0\}$.
* **Tabla de Transiciones Generada por el Software:**

| Subconjunto ($S$) | Símbolo `0` | Símbolo `1` | ¿Aceptación? | Justificación Formal |
| :--- | :--- | :--- | :---: | :--- |
| $\{q0\}$ | $\{q0, q1\}$ | $\{q0\}$ | No | $\{q0\} \cap \{q2\} = \emptyset$ |
| $\{q0, q1\}$ | $\{q0, q1, q2\}$ | $\{q0, q2\}$ | No | $\{q0, q1\} \cap \{q2\} = \emptyset$ |
| $\{q0, q1, q2\}$ | $\{q0, q1, q2\}$ | $\{q0, q2\}$ | **Sí** | Contiene al estado final $\{q2\}$ |
| $\{q0, q2\}$ | $\{q0, q1\}$ | $\{q0\}$ | **Sí** | Contiene al estado final $\{q2\}$ |

* **Total de Estados:** Exactamente 4 estados deterministas alcanzables de un espacio potencial de $2^3 = 8$.

### 3.4 Estimación de Complejidad
* **Número de Estados del AFN:** $n = |Q_N|$.
* **Tamaño del Alfabeto:** $k = |\Sigma|$.
* **Peor Caso Teórico:** $O(k \cdot n \cdot 2^n)$ transiciones y operaciones de conjunto.
* **Caso Práctico Alcanzable:** Si $n_{\text{alcanzables}}$ es el número de subconjuntos generados, la complejidad observada es $O(k \cdot n \cdot n_{\text{alcanzables}})$, donde típicamente $n_{\text{alcanzables}} \ll 2^n$.

---

## 4. Algoritmo 4: Eliminación de Inaccesibles y Minimización de AFD por Particiones

### 4.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFD $M = (Q, \Sigma, \delta, q_0, F)$, eliminar primero los estados que no pueden ser alcanzados desde $q_0$ y obtener el autómata mínimo equivalente $M_{\min}$ con el menor número posible de estados mediante refinamiento sucesivo de particiones (algoritmo de Moore / Hopcroft).
* **Respaldo Teórico:**
  * **Hopcroft (1971), DOI: [10.1016/B978-0-12-417750-5.50022-1](https://doi.org/10.1016/B978-0-12-417750-5.50022-1):** Algoritmo óptimo de partición de estados en tiempo $O(k \cdot n \log n)$.
  * **Valmari (2012), DOI: [10.1016/j.ipl.2011.12.004](https://doi.org/10.1016/j.ipl.2011.12.004):** Minimización de autómatas mediante refinamiento sistemático linealizado.
  * **Hopcroft, Motwani, & Ullman (2007), Sección 4.4.3:** Teorema de Myhill-Nerode y procedimiento inductivo de particionamiento $P_0, P_1, \dots, P_m$.
* **Axiomas Matemáticos:**
  * Dos estados $p, q \in Q$ son indistinguibles ($p \equiv q$) si y solo si $\forall w \in \Sigma^*, \; \hat{\delta}(p, w) \in F \iff \hat{\delta}(q, w) \in F$.
  * Partición base: $P_0 = \{ Q \setminus F, F \}$.
  * Refinamiento: $p \equiv_{k+1} q \iff p \equiv_k q \land (\forall a \in \Sigma, \; \delta(p, a) \equiv_k \delta(q, a))$.

### 4.2 Pseudocódigo y Correspondencia Modular
```text
Función Eliminar_Inaccesibles(M):
    alcanzables ← { M.q0 }
    cola ← Cola([M.q0])
    Mientras cola no esté vacía:
        u ← cola.desencolar()
        Para cada a en M.Sigma:
            v ← M.delta(u, a)
            Si v ∉ alcanzables:
                alcanzables.agregar(v)
                cola.encolar(v)
    Retornar Subgrafo(M, alcanzables)

Función Minimizar_AFD(M):
    M_acc ← Eliminar_Inaccesibles(M)
    P ← { M_acc.Q \ M_acc.F, M_acc.F }
    cambio ← Verdadero
    Mientras cambio:
        cambio ← Falso
        P_nueva ← ListaVacía()
        Para cada bloque B en P:
            firmas ← AgruparPorFirmaTransición(B, P, M_acc.Sigma)
            Si len(firmas) > 1:
                cambio ← Verdadero
            P_nueva.extender(firmas.valores())
        P ← P_nueva
    Retornar Construir_AFD_Cociente(M_acc, P)
```
* **Correspondencia Modular:**
  * Archivo `src/eliminacion_inaccesibles.py`: función `eliminar_estados_inaccesibles(auto)`.
  * Archivo `src/minimizacion_afd.py`: funciones `minimizar_afd(auto)` y `minimizar_afd_detallado(auto)`.

### 4.3 Ejemplo Resuelto por el Software
* **Autómata Evaluado:** Ejercicio 152 de la Lista 3 (`automatas/practica3/casos-de-prueba/152.jff`), con $Q = \{A, B, C, D, E, F\}$, $\Sigma = \{0, 1, 2\}$, $q_0 = A$, $F = \{D, E, F\}$.
* **Fase 1 (Inaccesibles):** Todos los 6 estados son alcanzables desde $A$.
* **Fase 2 (Refinamiento de Particiones):**
  * **Ronda 0 ($P_0$):**
    * Grupo 0 (No Finales): $\{A, B, C\}$.
    * Grupo 1 (Finales): $\{D, E, F\}$.
  * **Ronda 1 ($P_1$):**
    * En el grupo no final, las transiciones hacia $P_0$ difieren:
      * $A$: transita con $\{0, 1, 2\}$ a clases $(0, 1, 0)$.
      * $B$: transita a clases $(1, 1, 0)$.
      * $C$: transita a clases $(0, 1, 1)$.
      * Se separan en clases singulares: $\{A\}$, $\{B\}$, $\{C\}$.
    * En el grupo final $\{D, E, F\}$:
      * $D$ y $F$ comparten firma de transición.
      * $E$ tiene firma distinta.
      * Se particiona en $\{D, F\}$ y $\{E\}$.
    * Partición $P_1 = [\{A\}, \{B\}, \{C\}, \{D, F\}, \{E\}]$.
  * **Ronda 2 ($P_2$):**
    * Se evalúan las firmas con respecto a $P_1$. Ningún grupo se divide.
    * $P_2 = P_1$. Estabilidad alcanzada.
* **Resultado del Software:** 5 estados mínimos consolidados: `[A]`, `[B]`, `[C]`, `[D,F]`, `[E]`. Se redujo exactamente 1 estado redundante.

### 4.4 Estimación de Complejidad
* **Número de Estados:** $n = |Q|$.
* **Tamaño del Alfabeto:** $k = |\Sigma|$.
* **Fase Inaccesibles:** Recorrido BFS: $O(n + k \cdot n) = O(k \cdot n)$.
* **Fase Particiones (Algoritmo de Moore implementado):** A lo sumo $n - 1$ rondas de refinamiento. En cada ronda se clasifican $n$ estados para $k$ símbolos: $O(k \cdot n^2)$.
* **Algoritmo de Hopcroft (*Hopcroft's n log n*):** Mediante selección del bloque menor (*smaller half*): $O(k \cdot n \log n)$.

---

## 5. Algoritmo 5: Decisión de Equivalencia entre AFD vía Isomorfismo Mínimo

### 5.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dados dos AFD $M_1$ y $M_2$, decidir formalmente si reconocen exactamente el mismo lenguaje regular ($L(M_1) = L(M_2)$), comprobando si sus respectivos autómatas mínimos coinciden salvo renombramiento biyectivo de los estados.
* **Respaldo Teórico:**
  * **Hopcroft, Motwani, & Ullman (2007), Sección 4.4:** Teorema de Unicidad del AFD mínimo: para cualquier lenguaje regular, existe un único AFD mínimo salvo isomorfismo de estados y transiciones.
  * **Rabin & Scott (1959), DOI: [10.1147/rd.32.0114](https://doi.org/10.1147/rd.32.0114):** Decidibilidad de la equivalencia en autómatas finitos.
* **Axiomas Matemáticos:**
  $$M_1 \equiv M_2 \iff \exists \text{ biyección } f: Q_{\min, 1} \to Q_{\min, 2} \text{ tal que:}$$
  $$1. \; f(q_{0, 1}) = q_{0, 2}$$
  $$2. \; \forall q \in Q_{\min, 1}, \; q \in F_1 \iff f(q) \in F_2$$
  $$3. \; \forall q \in Q_{\min, 1}, \; \forall a \in \Sigma, \; f(\delta_1(q, a)) = \delta_2(f(q), a)$$

### 5.2 Pseudocódigo y Correspondencia Modular
```text
Función Son_Equivalentes(M1, M2):
    Si M1.Sigma ≠ M2.Sigma:
        Retornar (Falso, "Alfabetos diferentes")

    Min1 ← Minimizar_AFD(M1)
    Min2 ← Minimizar_AFD(M2)

    Si len(Min1.Q) ≠ len(Min2.Q):
        Retornar (Falso, "Diferente número de estados mínimos")

    mapeo ← { Min1.q0: Min2.q0 }
    cola ← Cola([(Min1.q0, Min2.q0)])

    Mientras cola no esté vacía:
        (u1, u2) ← cola.desencolar()
        Para cada a en Sigma:
            v1 ← Min1.delta(u1, a)
            v2 ← Min2.delta(u2, a)
            Si v1 ya mapeado y mapeo[v1] ≠ v2:
                Retornar (Falso, "Conflicto de isomorfismo")
            Si v1 no mapeado:
                Si (v1 ∈ Min1.F) ≠ (v2 ∈ Min2.F):
                    Retornar (Falso, "Discrepancia en estados finales")
                mapeo[v1] ← v2
                cola.encolar((v1, v2))

    Retornar (Verdadero, "Autómatas mínimos isomorfos: equivalentes")
```
* **Correspondencia Modular:**
  * Archivo `src/equivalencia_afd.py`: funciones `son_equivalentes(afd1, afd2, limite_longitud=6)` y `decidir_equivalencia_detallada(afd1, afd2)`.

### 5.3 Ejemplo Resuelto por el Software
* **Autómatas Evaluados:**
  * $M_1$: Autómata con estado $A$ (inicial y final), con ciclo $A \xrightarrow{0} A$.
  * $M_2$: Autómata con estados $B$ (inicial y final) y $C$ (final), con transiciones $B \xrightarrow{0} C$ y $C \xrightarrow{0} B$.
* **Minimización ejecutada por el software:**
  * $M_1$ ya es mínimo ($1$ estado).
  * En $M_2$, $B$ y $C$ son indistinguibles $\implies$ se colapsan en el bloque $[B,C]$ ($1$ estado).
* **Comprobación de Isomorfismo:**
  * Mapeo biyectivo hallado: $f([A]) = [B,C]$.
  * Condiciones de aceptación: ambos son iniciales y finales.
  * Transición con '0': $f(\delta_1([A], '0')) = f([A]) = [B,C] = \delta_2([B,C], '0')$.
* **Resultado del Software:** Formalmente equivalentes.

### 5.4 Estimación de Complejidad
* **Estados y Alfabeto:** $n = \max(|Q_1|, |Q_2|)$, $k = |\Sigma|$.
* **Minimización de ambos autómatas:** $2 \cdot O(k \cdot n^2)$.
* **Comprobación BFS de Isomorfismo:** Recorrido simultáneo sobre el autómata mínimo cociente: $O(k \cdot |Q_{\min}|) \le O(k \cdot n)$.
* **Complejidad Temporal Total:** $O(k \cdot n^2)$ (o $O(k \cdot n \log n)$ con minimizador de Hopcroft).

---

## 6. Algoritmo 6: Validación de Cadenas por Lotes y Generación de Informes

### 6.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Cargar un archivo de texto con una palabra por línea ($w \in \Sigma^*$), ejecutar la simulación en el autómata proporcionado y generar un informe estructurado que detalle el resultado de cada palabra junto con estadísticas globales de aceptación.
* **Respaldo Teórico:**
  * **Aho, Lam, Sethi, & Ullman (2006):** Técnicas de análisis léxico y procesamiento en lote de secuencias de tokens mediante tablas de transición.
  * **Wang & Smith (2024), DOI: [10.1093/jamiaopen/ooaf128](https://doi.org/10.1093/jamiaopen/ooaf128):** Evaluación empírica de velocidad de respuesta determinista en motores de validación regular aplicados a lotes masivos de texto.
* **Axiomas Matemáticos:**
  $$\text{Tasa de Aceptación} = \frac{\sum_{i=1}^N \mathbf{1}_{L(M)}(w_i)}{N} \times 100\%$$

### 6.2 Pseudocódigo y Correspondencia Modular
```text
Función Procesar_Lote_Cadenas(M, ruta_archivo):
    líneas ← LeerLíneas(ruta_archivo)
    resultados ← ListaVacía()
    aceptadas ← 0, rechazadas ← 0

    Para cada (idx, línea) en Enumerar(líneas):
        w ← línea.eliminar_saltos()
        (es_aceptada, traza) ← M.Simular(w)
        Si es_aceptada:
            aceptadas ← aceptadas + 1
        Sino:
            rechazadas ← rechazadas + 1
        resultados.agregar({ "linea": idx, "cadena": w, "aceptada": es_aceptada })

    informe ← { "total": len(líneas), "aceptadas": aceptadas, "rechazadas": rechazadas, "detalles": resultados }
    Retornar informe

Función Guardar_Informe_Lote(informe, ruta_salida):
    EscribirEncabezado(ruta_salida, informe.estadisticas)
    Para cada item en informe.detalles:
        EscribirFilaTabular(ruta_salida, item.linea, item.cadena, item.resultado)
```
* **Correspondencia Modular:**
  * Archivo `src/validacion_lotes.py`: función `procesar_lote_cadenas(auto, ruta_archivo_lineas)`.
  * Archivo `src/guardar_informe_lote.py`: función `guardar_informe_lote(informe, ruta_salida)`.

### 6.3 Ejemplo Resuelto por el Software
* **Lote de Entrada:** Archivo de 5 líneas con palabras `["", "0", "00", "000", "0000"]`.
* **Autómata Evaluado:** Reconocedor de paridad par de ceros ($(00)^*$).
* **Salida del Informe Generado por `guardar_informe_lote`:**
```text
============================================================
  REPORTE CONSOLIDADO DE VALIDACIÓN MASIVA POR LOTES
  Proyecto: Teoría de la Computación (ESCOM-IPN) - Práctica 3
============================================================
Archivo evaluado:        lote_cadenas.txt
Total de cadenas:        5
Cadenas ACEPTADAS:       3
Cadenas RECHAZADAS:      2
Tasa de aceptación:      60.00 %
------------------------------------------------------------
Línea | Cadena                    | Longitud | Resultado 
------------------------------------------------------------
    1 | λ (vacía)                 |        0 | ACEPTADA  
    2 | '0'                       |        1 | RECHAZADA 
    3 | '00'                      |        2 | ACEPTADA  
    4 | '000'                     |        3 | RECHAZADA 
    5 | '0000'                    |        4 | ACEPTADA  
============================================================
```

### 6.4 Estimación de Complejidad
* **Número de Cadenas en el Lote:** $N$.
* **Longitud Media de las Cadenas:** $\bar{m}$.
* **Complejidad Temporal:**
  * Sobre un AFD: $O(N \cdot \bar{m})$, tiempo lineal estrictamente proporcional al volumen de caracteres leídos.
  * Sobre un AFN-$\lambda$: $O(N \cdot \bar{m} \cdot (n + |E_\lambda|))$.
* **Complejidad Espacial:** $O(N)$ para almacenar el resumen de resultados y la emisión del informe tabular.
