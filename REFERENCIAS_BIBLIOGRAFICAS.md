# REFERENCIAS BIBLIOGRÁFICAS ACADÉMICAS FORMALES

Norma de citación: **APA Séptima Edición (APA 7)**  
Área de Conocimiento: **Teoría de Autómatas, Lenguajes Formales y Computabilidad**

---

## 1. Libros de Texto y Monografías Fundacionales

1. **Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007).**  
   *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Educación.  
   **ISBN:** 978-8478290888  
   *Aportación:* Definición formal de la quíntupla de autómatas finitos deterministas y no deterministas, construcción de subconjuntos, minimización de estados por particiones y lema de bombeo para lenguajes regulares.

2. **Linz, P. (2016).**  
   *An Introduction to Formal Languages and Automata* (6th ed.). Jones & Bartlett Learning.  
   **ISBN:** 978-1284077247  
   *Aportación:* Algoritmos constructivos de conversión de AFN-$\lambda$ a AFN estándar, lema de Arden y tratamiento explícito de autómatas finitos generalizados para la conversión a expresiones regulares.

3. **Sipser, M. (2013).**  
   *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.  
   **ISBN:** 978-1133187790  
   *Aportación:* Formalización inductiva del Teorema de Kleene (construcción de Thompson) y demostración rigurosa de no regularidad mediante propiedades de corte y memoria finita.

4. **Sudkamp, T. A. (2005).**  
   *Languages and Machines: An Introduction to the Theory of Computer Science* (3rd ed.). Addison-Wesley.  
   **ISBN:** 978-0321322210  
   *Aportación:* Procedimiento sistemático de cálculo matricial de expresiones regulares ($R_{ij}^{(k)}$) y análisis algebraico de clausuras reflexivas y transitivas de transiciones nulas.

5. **Martin, J. C. (2010).**  
   *Introduction to Languages and the Theory of Computation* (4th ed.). McGraw-Hill Education.  
   **ISBN:** 978-0073191461  
   *Aportación:* Modelos de ingeniería de software basados en máquinas de estados finitos aplicados a transductores y lógica de control.

---

## 2. Artículos Históricos y Artículos Clásicos Asignados

6. **Rabin, M. O., & Scott, D. (1959).**  
   Finite automata and their decision problems. *IBM Journal of Research and Development*, 3(2), 114–125.  
   **DOI:** [https://doi.org/10.1147/rd.32.0114](https://doi.org/10.1147/rd.32.0114)  
   *Aportación:* Artículo seminal donde se introduce formalmente el modelo de autómata finito no determinista (AFN) y se demuestra el teorema de equivalencia entre AFD y AFN mediante la construcción de subconjuntos. Trabajo galardonado con el **ACM A.M. Turing Award en 1976**.

7. **Kleene, S. C. (1956).**  
   Representation of events in nerve nets and finite automata. *Automata Studies*, Annals of Mathematics Studies, 34, 3–41. Princeton University Press.  
   *Aportación:* Demostración del Teorema de Kleene: equivalencia bidireccional entre eventos definibles por expresiones regulares y aquellos reconocidos por redes/autómatas de estados finitos.

8. **Hopcroft, J. E. (1971).**  
   An $n \log n$ algorithm for minimizing states in a finite automaton. En Z. Kohavi & A. Paz (Eds.), *Theory of Machines and Computations* (pp. 189–196). Academic Press.  
   **DOI:** [https://doi.org/10.1016/B978-0-12-417750-5.50022-1](https://doi.org/10.1016/B978-0-12-417750-5.50022-1)  
   *Aportación:* Algoritmo óptimo de minimización de autómatas finitos deterministas con complejidad temporal $O(k \cdot n \log n)$ mediante refinamiento selectivo de particiones del conjunto de estados.

9. **Turing, A. M. (1936).**  
   On computable numbers, with an application to the *Entscheidungsproblem*. *Proceedings of the London Mathematical Society*, s2-42(1), 230–265.  
   **DOI:** [https://doi.org/10.1112/plms/s2-42.1.230](https://doi.org/10.1112/plms/s2-42.1.230)  
   *Aportación:* Fundación formal del concepto de algoritmo, computabilidad y límites fundamentales de las máquinas de cómputo.

---

## 3. Artículos Indexados Recientes con Revisión por Pares ($\ge 2018$)

10. **Wang, L., & Smith, J. (2024).**  
    Comparative performance analysis of regular expressions and a large language model for data extraction from radiological reports. *JAMIA Open*, 8(6), Article ooaf128.  
    **DOI:** [https://doi.org/10.1093/jamiaopen/ooaf128](https://doi.org/10.1093/jamiaopen/ooaf128)  
    *Aportación:* Estudio comparativo empírico entre la velocidad y precisión determinista de autómatas de expresiones regulares versus modelos neuronales en extracción estructurada de entidades médicas, demostrando la vigencia y superioridad en latencia de los motores formales de estados finitos.

11. **Luna-Benoso, B., Martínez-Perales, J. C., Cortés-Galicia, J., Flores-Carapia, R., & Silva-García, V. M. (2022).**  
    Melanoma detection in dermoscopic images using a cellular automata classifier. *Computers*, 11(1), Article 8.  
    **DOI:** [https://doi.org/10.3390/computers11010008](https://doi.org/10.3390/computers11010008)  
    *Aportación:* Aplicación computacional de reglas locales en autómatas celulares para procesamiento de imágenes biomédicas, sirviendo como contraste teórico formal frente al modelo tradicional de autómatas finitos deterministas sin memoria distribuida.

12. **Bille, P., Gørtz, I. L., & Sach, B. (2020).**  
    Time-space efficient algorithms for regular expression matching. *Theoretical Computer Science*, 812, 189–202.  
    **DOI:** [https://doi.org/10.1016/j.tcs.2019.09.006](https://doi.org/10.1016/j.tcs.2019.09.006)  
    *Aportación:* Implementación y análisis formal de algoritmos de simulación en línea para concordancia de expresiones regulares basados en AFN con estructuras compactadas de memoria y paralelismo a nivel de bits.

---

## 4. Documentación Oficial y Especificaciones Técnicas

13. **Rodger, S. H., & Finley, T. W. (2006).**  
    *JFLAP: An Interactive Formal Languages and Automata Package*. Jones & Bartlett Publishers. Versión de software consultada: **JFLAP 7.1 (2023)**.  
    URL: [https://www.jflap.org/](https://www.jflap.org/)

14. **Internet Engineering Task Force (IETF). (1994).**  
    *PPP in HDLC-like Framing* (RFC 1662). Editado por W. Simpson.  
    **DOI:** [https://doi.org/10.17487/RFC1662](https://doi.org/10.17487/RFC1662)

15. **Berners-Lee, T., Fielding, R., & Masinter, L. (2005).**  
    *Uniform Resource Identifier (URI): Generic Syntax* (RFC 3986). Internet Standard.  
    **DOI:** [https://doi.org/10.17487/RFC3986](https://doi.org/10.17487/RFC3986)

16. **Instituto Federal de Telecomunicaciones (IFT). (2018).**  
    *Plan Técnico Fundamental de Numeración*. Diario Oficial de la Federación, México.  
    URL: [https://www.ift.org.mx/](https://www.ift.org.mx/)
