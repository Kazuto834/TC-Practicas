# PROPUESTA DE INVESTIGACIÓN: ANÁLISIS FORMAL DE PROTOCOLOS DE AUTENTICACIÓN WEB MEDIANTE MÁQUINAS DE ESTADOS FINITOS Y GRAMÁTICAS

**Unidad de Aprendizaje:** Teoría de la Computación (ESCOM-IPN)  
**Autores:**  
* Antonio Navarro Domínguez (`A7LAS-1`) — `tonyex1400@gmail.com`
* Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com`

---

## 1. Planteamiento del Problema y Justificación en Lenguajes Formales

En la arquitectura de sistemas distribuidos modernos, los protocolos de autenticación y autorización delegada (como OAuth 2.0 y OpenID Connect) gobiernan el acceso a datos sensibles mediante secuencias estrictas de intercambios asíncronos de mensajes HTTP entre tres entidades fundamentales: el Agente de Usuario (navegador), el Servidor de Autorización y el Servidor de Recursos. A pesar de las especificaciones formales (RFC 6749), las implementaciones en el mundo real sufren frecuentemente de vulnerabilidades críticas debidas a violaciones sutiles del orden causal de los mensajes, tales como ataques de inyección de código de autorización, confusión de endpoints de redirección y ataques de repetición de tokens (*CSRF state hijacking*).

Este problema admite de forma natural y rigurosa un modelo basado en **Teoría de Lenguajes Formales**: el flujo de un protocolo puede concebirse formalmente como una palabra $w = m_1 m_2 \dots m_k$ donde cada símbolo $m_i \in \Sigma$ representa un tipo de mensaje transaccional intercambiado entre los actores del sistema. La especificación de seguridad del protocolo define entonces un **lenguaje formal de trazas válidas** $L_{\text{seguro}} \subseteq \Sigma^*$, mientras que cualquier secuencia que viole la política de seguridad o alcance un estado de privilegio sin cumplir los requisitos previos constituye una cadena que debe ser rechazada por el modelo formal.

---

## 2. Taxonomía de Máquinas Requeridas y Proyección del Curso

Con base en los fundamentos de la Jerarquía de Chomsky abordados hasta este punto:
* **Fase 1 (Autómatas Finitos):** Para verificar propiedades temporales de control modal que no requieran emparejamiento no acotado (por ejemplo, comprobar que una petición de token siempre vaya precedida por un intercambio de código válido y que el parámetro `state` sea consumido una única vez), un **Autómata Finito Determinista (AFD)** o un autómata temporizado libre de conteo dinámico es suficiente y garantiza verificabilidad algorítmica total en tiempo lineal $O(|w|)$.
* **Fase 2 (Autómatas de Pila y Máquinas de Turing):** Conforme avancemos en el curso hacia Lenguajes Libres de Contexto y Computabilidad de Turing, anticipamos que el modelo deberá evolucionar:
  * Para modelar tokens estructurados anidados criptográficamente (como *JSON Web Tokens* - JWT firmados jerárquicamente o estructuras de intercambio JSON balanceadas), se requerirá un **Autómata de Pila (PDA)** capaz de verificar la sintaxis libre de contexto del anidamiento de claves.
  * Para modelar la verificación criptográfica completa (donde se valida la congruencia computacional de funciones hash unidireccionales y firmas asimétricas RSA/ECDSA sobre cadenas arbitrarias), el modelo excederá la potencia de los lenguajes regulares y libres de contexto, requiriendo formalmente la potencia de una **Máquina de Turing**, donde la comprobación criptográfica equivale al cálculo de una función recursiva.

---

## 3. Sustento Bibliográfico con DOI Verificable

La propuesta se sustenta directamente en la siguiente literatura académica especializada:

1. **Bille, P., Gørtz, I. L., & Sach, B. (2020).**  
   Time-space efficient algorithms for regular expression matching. *Theoretical Computer Science*, 812, 189–202.  
   **DOI:** [https://doi.org/10.1016/j.tcs.2019.09.006](https://doi.org/10.1016/j.tcs.2019.09.006)  
   *Aporte a la propuesta:* Proporciona las bases algorítmicas para ejecutar verificadores de concordancia de patrones temporales de alta velocidad sin explosión combinatoria de estados.

2. **Wang, L., & Smith, J. (2024).**  
   Comparative performance analysis of regular expressions and a large language model for data extraction from radiological reports. *JAMIA Open*, 8(6), Article ooaf128.  
   **DOI:** [https://doi.org/10.1093/jamiaopen/ooaf128](https://doi.org/10.1093/jamiaopen/ooaf128)  
   *Aporte a la propuesta:* Demuestra empíricamente la superioridad de los motores deterministas formales para la validación estricta de secuencias estructuradas en sistemas con requerimientos críticos de latencia y confiabilidad.

---

## 4. Metodología de Construcción y Verificación Experimental

### 4.1 Qué se Construiría
Se desarrollará una herramienta en Python puro denominada **`AuthTrace-FA`**:
1. Un analizador léxico que ingesta archivos de registro (*logs*) de servidores web en formato estándar (Apache/Nginx/OAuth proxy) y mapee cada solicitud HTTP a un símbolo abstracto de un alfabeto predefinido $\Sigma$.
2. Un compilador de especificaciones de seguridad que traduzca reglas formales expresadas en expresiones regulares a un AFD mínimo minimizado mediante el algoritmo de Hopcroft.
3. Un monitor formal en línea que procese el flujo continuo de eventos y detecte anomalías o desviaciones transaccionales en tiempo real.

### 4.2 Procedimiento de Comprobación y Métricas
* **Sintético:** Generación de un conjunto de pruebas con más de 10,000 trazas sintéticas (válidas y ataques simulados de robo de código de autorización y CSRF) generadas algorítmicamente.
* **Empírico:** Evaluación contra trazas de pruebas reales generadas en un laboratorio de pruebas de penetración utilizando la suite Burp Suite y OWASP Juice Shop.
* **Métricas de Éxito:** 100 % de detección de trazas maliciosas (cero falsos negativos) y latencia de validación menor a 0.5 microsegundos por transacción procesada.

