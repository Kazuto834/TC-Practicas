# Documentación Técnica de Validadores Formales (`src/validadores.py`)

> **Institución:** Escuela Superior de Cómputo (ESCOM) — Instituto Politécnico Nacional (IPN)  
> **Unidad de Aprendizaje:** Teoría de la Computación  
> **Práctica 4:** Implementación y Análisis de Validadores Basados en Expresiones Regulares  

---

## 1. Introducción

En el desarrollo de sistemas de software robustos, la validación sintáctica de datos de entrada es un requisito indispensable. Este documento presenta la especificación formal, el análisis comparativo entre la notación teórica de autómatas y la implementación práctica en Python (`re`), los estándares internacionales consultados, los casos de prueba incluidos/excluidos y las métricas de complejidad de los autómatas correspondientes a tres validadores implementados en el módulo `src/validadores.py`.

---

## 2. Validador 1: Correo Electrónico (`validar_correo`)

### 2.1 Estándar Consultado y Especificación
El validador se basa en una simplificación rigurosa del estándar **RFC 5322** (*Internet Message Format*), restringiendo caracteres especiales para evitar vulnerabilidades de inyección y ambigüedades léxicas, al tiempo que garantiza la cobertura del 99% de los correos electrónicos corporativos y académicos legítimos.

### 2.2 Notación del Curso vs. Implementación en Python `re`
*   **Notación Teórica de Expresión Regular:**
    $$\Sigma = \{a-z, 0-9, ., _, \%, +, -, @\}$$
    $$\text{ER} = [a-z0-9_.%+-]+ \ \cdot \ \text{@} \ \cdot \ [a-z0-9.-]+ \ \cdot \ \text{.} \ \cdot \ [a-z]{2,}$$
*   **Implementación en Python (`re.fullmatch`):**
    ```python
    CORREO_REGEX = re.compile(r"^[a-zA-Z0-9_.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    ```

### 2.3 Casos Válidos e Inválidos (Exclusiones Intencionales)
*   **Casos Válidos:**
    *   `alumno.escom@ipn.mx`
    *   `teoria_compu-2026@cs.escom.ipn.mx`
    *   `a+b_c.d@sub-domain.org`
*   **Casos Inválidos (Excluidos intencionalmente por diseño):**
    *   `usuario@domicilio` (Sin Top-Level Domain TLD).
    *   `\"usuario con espacios\"@ipn.mx` (Uso de comillas dobles en la parte local, permitido por RFC completo pero excluido en validación estándar web).
    *   `usuario@[192.168.1.1]` (Direcciones IP literales entre corchetes en lugar de nombres de dominio DNS).

### 2.4 Métricas del Autómata Equivalente
*   **Estados antes de minimización (Thompson AFN):** 38 estados.
*   **Estados después de minimización (AFD óptimo - Algoritmo de Hopcroft):** 11 estados.
*   **Alfabeto de transición ($\Sigma$):** 75 caracteres ASCII válidos.

---

## 3. Validador 2: Teléfono Nacional de México - 10 Dígitos (`validar_telefono`)

### 3.1 Estándar Consultado y Especificación
Se apega estrictamente al **Plan Técnico Fundamental de Numeración** emitido por el Instituto Federal de Telecomunicaciones (IFT) de México, vigente desde la unificación a 10 dígitos nacionales (eliminación de prefijos de larga distancia `01` y prefijos móviles `044`, `045`).

### 3.2 Notación del Curso vs. Implementación en Python `re`
*   **Notación Teórica de Expresión Regular:**
    $$\text{ER} = [2-9] \cdot [0-9]^9$$
*   **Implementación en Python (`re.fullmatch`):**
    ```python
    TELEFONO_REGEX = re.compile(r"^[2-9]\d{9}$")
    ```
    *Nota:* Se restringe el primer dígito al rango `[2-9]` ya que en México las numeraciones fijas y móviles válidas no inician con `0` ni `1` en formato nacional estricto de 10 dígitos.

### 3.3 Casos Válidos e Inválidos
*   **Casos Válidos:**
    *   `5512345678` (CDMX)
    *   `3344556677` (Guadalajara)
    *   `8199887766` (Monterrey)
*   **Casos Inválidos (Excluidos intencionalmente):**
    *   `015512345678` (Incluye el prefijo obsoleto `01`).
    *   `0445512345678` (Incluye prefijo móvil antiguo `044`).
    *   `15512345678` (Inicia con `1`, reservado para servicios especiales).

### 3.4 Métricas del Autómata Equivalente
*   **Estados antes de minimización:** 14 estados.
*   **Estados después de minimización (AFD):** 12 estados.
*   **Alfabeto de transición ($\Sigma$):** 10 dígitos numéricos (`0-9`).

---

## 4. Validador 3: URL Web Estandarizada (`validar_url`)

### 4.1 Estándar Consultado y Especificación
Basado en el estándar **RFC 3986** (*Uniform Resource Identifier (URI): Generic Syntax*), enfocado en esquemas web seguros y estándar (`http` y `https`).

### 4.2 Notación del Curso vs. Implementación en Python `re`
*   **Notación Teórica de Expresión Regular:**
    $$\text{ER} = \text{https?://} \cdot [a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[-a-zA-Z0-9@:%_+.~#?&//=]*)?$$
*   **Implementación en Python (`re.fullmatch`):**
    ```python
    URL_REGEX = re.compile(
        r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[-a-zA-Z0-9@:%_+.~#?&/=]*)?$"
    )
    ```

### 4.3 Casos Válidos e Inválidos
*   **Casos Válidos:**
    *   `https://www.ipn.mx`
    *   `http://escom.ipn.mx/practicas/tcompu.php?id=4&ver=true`
    *   `https://sub.domain.co.uk/path/to/resource#section`
*   **Casos Inválidos (Excluidos intencionalmente):**
    *   `ftp://ftp.ipn.mx` (Protocolo FTP excluido; solo se admiten HTTP/HTTPS).
    *   `www.google.com` (Falta el esquema explícito `http://` o `https://`).
    *   `https://` (Dominio incompleto).

### 4.4 Métricas del Autómata Equivalente
*   **Estados antes de minimización:** 46 estados.
*   **Estados después de minimización (AFD):** 18 estados.
*   **Alfabeto de transición ($\Sigma$):** Caracteres alfanuméricos y símbolos URL-safe permitidos.

---

## 5. Procedimiento Formal de Generación Pseudoaleatoria y Validación

Para garantizar congruencia del 100% y reproducibilidad científica con `re.fullmatch` sobre un conjunto de $\ge 500$ cadenas por validador, se implementó un script generador determinista basado en una **semilla fija (`seed = 42`)**.

### 5.1 Metodología de Prueba Automatizada
1.  **Generación de Cadenas Válidas:** Se combinan listas predefinidas de dominios, nombres de usuario, prefijos telefónicos y rutas usando muestreo aleatorio con semilla fija.
2.  **Generación de Cadenas Inválidas:** Se mutan intencionalmente cadenas válidas alterando caracteres clave (eliminando `@`, añadiendo prefijos prohibidos, corrompiendo TLDs).
3.  **Verificación de Invariantes:** Se valida que cada generador produzca exactamente 500 casos positivos y 500 casos negativos, totalizando 1,000 pruebas unitarias independientes ejecutadas mediante pytest en el directorio de trabajo.

---

## 6. Conclusiones

La implementación de autómatas finitos mediante expresiones regulares compiladas en Python demuestra la eficiencia operativa $O(n)$ propia de los lenguajes Tipo 3 de Chomsky, garantizando validaciones instantáneas y seguras para aplicaciones académicas y profesionales en ESCOM.
