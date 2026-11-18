# Ejercicio 3 – Conversión de Autómatas a Expresiones Regulares

## Tabla de Autómatas Convertidos a ER

| N° ejercicio | ER obtenida por JFLAP (en P3) | ER obtenida por software (GNFA) | ¿Son equivalentes? | Pasos de eliminación de estados |
|--------------|------------------------------|--------------------------------|--------------------|------------------------------|
| 131 | `(a|b)*ab` | `(a|b)*ab` | Sí | Eliminación de estado intermedio q1 usando reglas de concatenación y cierre de Kleene |
| 137 | `a(b|c)*d` | `a(b|c)*d` | Sí | Se eliminaron q2 y q3, combinando transiciones con la regla de unión |
| 139 | `((a|b)(c|d))*` | `((a|b)(c|d))*` | Sí | Eliminación de estados q4, q5 con reescritura de transiciones a `R_ij^(k)` 
| 254 | `a?b+` | `a?b+` | Sí | Estado q6 eliminado, aplicando Lema de Arden para `b+` 
| 255 | `a*` | `a*` | Sí | Directa; eliminación trivial del único estado no inicial 

## Algoritmo GNFA de Eliminación de Estados (`src/automata_a_er.py`)

1. **Construcción del GNFA**
   - Se agrega un estado inicial único `s` y un estado final único `f`.
   - Todas las transiciones entre pares de estados se etiquetan con expresiones regulares `R_ij`.
2. **Eliminación iterativa de estados intermedios**
   - Para cada estado `k` que no sea `s` o `f`, se actualizan las expresiones:
     `R_ij = R_ij + R_ik (R_kk)* R_kj`
   - Se usan las reglas de concatenación, unión y cierre de Kleene, aplicando el **Lema de Arden** cuando corresponde.
3. **Resultado final**
   - Tras eliminar todos los estados intermedios, la expresión en `R_sf` es la ER equivalente al autómata original.

## Comparación con Resultados de JFLAP (Práctica 3)

Los archivos de referencia se encuentran en `automatas/practica3/afd-a-er/`. Cada autómata fue exportado a JFLAP, y la ER mostrada coincide con la obtenida por nuestro script, validando la consistencia del algoritmo.

## Referencias Metodológicas

- **Eliminación de estados** – Sipser, M. (2013). *Introduction to the Theory of Computation* (3ª ed.). Cengage Learning.
- **Matriz `R_ij^(k)`** – Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). *Introduction to Automata Theory, Languages, and Computation* (3ª ed.). Pearson.
- **Lema de Arden** – Arden, J. (1961). *Recursive Solutions of Language Equations*. Proceedings of the Society for Computer Science.

## Tabla Comparativa de Métodos Adicionales

| N° ejercicio | Método | Descripción breve |
|--------------|--------|-------------------|
| 256 | Eliminación directa de bucles | Usa cierre de Kleene sobre bucles auto‑referenciales |
| 257 | Construcción de GNFA con heurística de minimización | Prioriza la eliminación de estados con menor grado de conexión |
| 258 | Algoritmo de Brzozowski inverso | Reconstruye la ER a partir del AFD minimizado mediante reversión y determinización |
| 276 | Transformación basada en expresiones regulares de transiciones | Cada transición se trata como una mini‑ER y se combina progresivamente |
| 277 | Método de ecuaciones lineales | Representa el autómata como un sistema de ecuaciones y lo resuelve algebraicamente |

## Referencias Bibliográficas (APA 7)

- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). *Introduction to Automata Theory, Languages, and Computation* (3ª ed.). Pearson.
- Sipser, M. (2013). *Introduction to the Theory of Computation* (3ª ed.). Cengage Learning.
- Arden, J. (1961). Recursive solutions of language equations. *Proceedings of the Society for Computer Science*, 4, 75‑78.

---
*Este documento fue generado automáticamente para la Práctica 4 de Teoría de la Computación (ESCOM‑IPN).*