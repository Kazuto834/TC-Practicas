# EJERCICIO 3: DOCUMENTACIÓN FORMAL DE ALGORITMOS (PRÁCTICA 3)

**Práctica 3:** Extensión de Software para Autómatas Finitos y Expresiones Regulares  
**Autores:**  
* Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com` (Minimización y Complejidades)
* Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com` (Subconjuntos y Eliminación $\lambda$)  
**Institución:** Escuela Superior de Cómputo (ESCOM-IPN) — 4CM4 / 4CV4

---

## 1. Algoritmo 1: Eliminación de Transiciones Lambda

### 1.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFND-$\lambda$ $M = (Q, \Sigma, \delta, q_0, F)$, construir un AFND equivalente $M' = (Q, \Sigma, \delta', q_0, F')$ que no contenga transiciones vacías ($\lambda$).
* **Respaldo Teórico:** Hopcroft, Motwani y Ullman (2007), Sección 2.5.5 (*Eliminating $\epsilon$-Transitions*); Linz (2016), Teorema 2.2.
* **Axioma:**
  $$\delta'(q, a) = \lambda\text{-cl}(\delta(\lambda\text{-cl}(q), a)), \quad \forall q \in Q, \; a \in \Sigma$$
  $$F' = \{q \in Q \mid \lambda\text{-cl}(q) \cap F \ne \emptyset\}$$

### 1.2 Pseudocódigo y Correspondencia en Código
```
Funcion Eliminar_Lambda(M):
1. F' ← Vacio()
2. Para cada q ∈ M.Q:
3.     Si Clausura_Lambda({q}) ∩ M.F ≠ ∅ entonces F' ← F' ∪ {q}
4. delta' ← MatrizVacia()
5. Para cada q ∈ M.Q:
6.     Cq ← Clausura_Lambda({q})
7.     Para cada a ∈ M.Sigma:
8.         Directos ← Mover(Cq, a)
9.         delta'(q, a) ← Clausura_Lambda(Directos)
10. Retornar Autómata(Q=M.Q, Sigma=M.Sigma, delta=delta', q0=M.q0, F=F')
```
* **Correspondencia:** Implementado en `src/algoritmos_afn.py:eliminar_transiciones_lambda`.

### 1.3 Estimación de Complejidad
* **Número de Estados:** $|Q| = n$.
* **Tamaño del Alfabeto:** $|\Sigma| = k$.
* **Complejidad Temporal:** Para cada estado y símbolo se ejecutan dos clausuras transitivas: $O(n \cdot k \cdot (n + |E_\lambda|))$. En grafos densos de transiciones nulas: $O(k \cdot n^3)$.

---

## 2. Algoritmo 2: Construcción de Subconjuntos (AFN $\to$ AFD)

### 2.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFN $M_N = (Q_N, \Sigma, \delta_N, q_0, F_N)$, sintetizar un AFD $M_D = (Q_D, \Sigma, \delta_D, S_0, F_D)$ tal que $L(M_D) = L(M_N)$.
* **Respaldo Teórico:** Rabin y Scott (1959), Teorema 1; Hopcroft et al. (2007), Sección 2.3.5 (*The Subset Construction*).

### 2.2 Pseudocódigo y Correspondencia en Código
```
Funcion Construccion_Subconjuntos(M_N):
1. S0 ← Clausura_Lambda({M_N.q0})
2. Q_D ← { S0 }
3. Cola ← [ S0 ]
4. Mientras Cola no este vacia:
5.     S ← Desencolar(Cola)
6.     Para cada a ∈ M_N.Sigma:
7.         U ← Clausura_Lambda( Mover(S, a) )
8.         Si U ∉ Q_D:
9.             Q_D ← Q_D ∪ { U }
10.            Encolar(Cola, U)
11.        delta_D(S, a) ← U
12. F_D ← { S ∈ Q_D | S ∩ M_N.F ≠ ∅ }
13. Retornar AFD(Q_D, Sigma, delta_D, S0, F_D)
```
* **Correspondencia:** Implementado en `src/algoritmos_afn.py:construccion_subconjuntos`.

### 2.3 Estimación de Complejidad
* **Peor Caso Temporal:** $O(k \cdot 2^n \cdot n)$.
* **Caso Promedio Práctico:** $O(k \cdot n_{\text{alcanzables}})$, donde $n_{\text{alcanzables}} \ll 2^n$.

---

## 3. Algoritmo 3: Minimización de AFD por Refinamiento de Particiones

### 3.1 Enunciado del Problema y Fundamento Teórico
* **Problema:** Dado un AFD $M = (Q, \Sigma, \delta, q_0, F)$, encontrar el autómata determinista equivalente con el menor número posible de estados.
* **Respaldo Teórico:** Hopcroft (1971); Sipser (2013), Teorema de Myhill-Nerode; Hopcroft et al. (2007), Sección 4.4.3.

### 3.2 Pseudocódigo y Correspondencia en Código
```
Funcion Minimizar_AFD(M):
1. M_acc ← Eliminar_Inaccesibles(M)
2. Particion P ← { M_acc.F, M_acc.Q \ M_acc.F }
3. Repetir:
4.     P_nueva ← Vacia()
5.     Para cada Grupo G ∈ P:
6.         Particionar G segun delta(q, a) en clases de P
7.         Agregar subgrupos a P_nueva
8.     Si P_nueva == P entonces Terminar bucle
9.     P ← P_nueva
10. Construir AFD colapsando cada bloque de P en un unico estado representativo
```
* **Correspondencia:** Implementado en `src/minimizacion.py:minimizar_afd`.

### 3.3 Estimación de Complejidad
* **Refinamiento Estándar (Moore):** $O(k \cdot n^2)$.
* **Refinamiento de Hopcroft (*Smaller Half*):** $O(k \cdot n \log n)$.

---

## 4. Ejemplo Comparativo Resuelto a Mano vs Software

### Autómata Evaluado: Ejercicio 152 (Lista 3, p. 3)
* **Estados Originales:** $Q = \{A, B, C, D, E, F\}$ sobre $\Sigma = \{0, 1, 2\}$, con $F = \{D, E, F\}$.
* **Resolución a Mano (de Mario García Castillo, boleta 2025630545, Lista 3):**
  * $P_0 = \{x_0, x_1\}$ donde $x_0 = \{A, B, C\}$ (no finales) y $x_1 = \{D, E, F\}$ (finales).
  * Ronda 1 ($P_1$): $A \to \{x_0, x_1, x_0\}$, $B \to \{x_1, x_1, x_0\}$, $C \to \{x_0, x_1, x_1\}$. Se separan en singuletes $\{A\}, \{B\}, \{C\}$. En $x_1$, $D$ y $F$ transitan a $\{x_1, x_0, x_0\}$, mientras $E$ transita a $\{x_1, x_0, x_0\}$.
  * Ronda 2 ($P_2$): $x_6 = \{D, F\}$ y $x_7 = \{E\}$.
  * Resultado a Mano: $5$ estados mínimos ($A, B, C, [D,F], E$).
* **Resolución del Software (`src/minimizacion.py`):**
  * Ejecución de `minimizar_afd`:
  * Salida: 5 estados consolidados: `[A]`, `[B]`, `[C]`, `[D,F]`, `[E]`.
  * **Conclusión:** Coincidencia exacta del 100 % entre la resolución matemática teórica y la salida algorítmica del software.

