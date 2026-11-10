# REPORTE DE CONTROL DE CALIDAD Y PRUEBAS (QA)

**Proyecto:** Prácticas de Teoría de la Computación  
**Responsable QA:** Equipo de Control de Calidad  
**Entorno de Ejecución:** Python 3.12.10 (Local) / Matrix Python 3.11, 3.12, 3.13 (GitHub Actions)  
**Herramienta de Pruebas:** Pytest 8.3.4 / 9.2.0  
**Fecha de Verificación:** 2026-11-09

---

## 1. Tabla de Matriz de Pruebas Ejecutadas

| ID | Suite / Módulo | Descripción de la Prueba | Resultado Esperado | Resultado Obtenido | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **QA-P1-01** | `test_lenguajes.py` | `test_cadena_vacia`: Comprobación de prefijos, sufijos y subcadenas sobre cadena nula `""`. | Retornar lista conteniendo únicamente `[""]`. | `prefijos("") == [""]`, `sufijos("") == [""]`, `subcadenas("") == [""]`. | **APROBADO** |
| **QA-P1-02** | `test_lenguajes.py` | `test_cadena_longitud_uno`: Operaciones sobre cadena unaria `"a"`. | Retornar `{"", "a"}` en las tres operaciones. | Conjuntos equivalentes a `{"" , "a"}` comprobados. | **APROBADO** |
| **QA-P1-03** | `test_lenguajes.py` | `test_diferencia_kleene_y_positiva_longitud_cero`: Diferencia en $\Sigma^*$ y $\Sigma^+$ para $n=0$. | Kleene retorna `[""]`; positiva retorna `[]`. | `res_kleene == [""]`, `res_positiva == []`, `res_kleene != res_positiva`. | **APROBADO** |
| **QA-P1-04** | `test_lenguajes.py` | `test_alfabeto_un_simbolo`: Generación de cerraduras hasta longitud 6 sobre `{"a"}`. | Generación exacta de potencias $a^0$ a $a^6$. | Coincidencia exacta con conjunto generado. | **APROBADO** |
| **QA-P2-01** | `test_formatos.py` | `test_roundtrip_jff`: Inversión I/O `.jff` de JFLAP 7.1 sin alteración de quíntupla. | `cargar_jff(guardar_jff(A)) == A`. | Estados, transiciones y simulación idénticos. | **APROBADO** |
| **QA-P2-02** | `test_formatos.py` | `test_roundtrip_json`: Inversión I/O en formato JSON estructurado según Anexo 3. | Preservar quíntupla formal en serialización JSON. | Estados, alfabeto y transiciones íntegros. | **APROBADO** |
| **QA-P2-03** | `test_formatos.py` | `test_roundtrip_xml`: Inversión I/O en XML canónico según Anexo 3. | Idéntica quíntupla importada vs exportada. | XML estructurado validado y recuperado. | **APROBADO** |
| **QA-P2-04** | `test_automata.py` | `test_afd_paridad_ceros`: Aceptación y rechazo determinista en AFD (Ej. 139). | Cadenas pares aceptadas; impares rechazadas. | 5 cadenas válidas y 5 inválidas verificadas. | **APROBADO** |
| **QA-P2-05** | `test_automata.py` | `test_afnd_termina_en_01`: Simulación concurrente en AFND sin determinizar. | Caminos no deterministas explorados simultáneamente. | Cadenas con terminación `01` aceptadas. | **APROBADO** |
| **QA-P2-06** | `test_automata.py` | `test_afnd_lambda_clausura`: Aceptación en AFND-$\lambda$ dependiente de $\lambda$-clausura. | $\lambda\text{-cl}(q_0) = \{q_0, q_1\}$, acepta $\lambda$ y `'b'`. | Aceptación inmediata verificada con éxito. | **APROBADO** |
| **QA-P2-07** | `test_automata.py` | `test_traza_paso_a_paso`: Registro formal de transiciones tomadas. | Lista cronológica con metadatos de bifurcación. | Transición `A -> x -> B` registrada exactamente. | **APROBADO** |
| **QA-P2-08** | `test_pacman.py`   | `test_estructura_pacman`: Formalización de 6 estados y 2 nuevos eventos. | Estados y aceptación configurados. | Estados $Q$ y $F$ comprobados con precisión. | **APROBADO** |
| **QA-P2-09** | `test_pacman.py`   | `test_simulacion_pacman`: Batería de 10 cadenas sobre el modelo de Pac-Man. | Resultados de letalidad coincidentes. | 10 de 10 cadenas con estado de salida exacto. | **APROBADO** |
| **QA-P3-01** | `test_algoritmos_p3.py`| Cálculo de $\lambda$-clausura formal (Práctica 3). | $\lambda\text{-cl}(q)$ cerrado reflexivo-transitivo. | Pendiente de desarrollo P3. | **PENDIENTE** |
| **QA-P3-02** | `test_algoritmos_p3.py`| Eliminación de transiciones $\lambda$ (Práctica 3). | AFN equivalente sin transiciones vacías. | Pendiente de desarrollo P3. | **PENDIENTE** |
| **QA-P3-03** | `test_algoritmos_p3.py`| Construcción de subconjuntos AFN $\to$ AFD (Práctica 3). | Subconjuntos alcanzables y tabla determinista. | Pendiente de desarrollo P3. | **PENDIENTE** |
| **QA-P3-04** | `test_minimizacion.py` | Minimización de Hopcroft y equivalencia isomórfica (Práctica 3). | Partición irreducible y comparación de autómatas. | Pendiente de desarrollo P3. | **PENDIENTE** |
| **QA-P4-01** | `test_parser_er.py`   | Parser sintáctico de expresiones regulares con errores posicionales (P4). | Diagnóstico posicional en sintaxis no válida. | Pendiente de desarrollo P4. | **PENDIENTE** |
| **QA-P4-02** | `test_kleene.py`      | Thompson Inductivo y eliminación de estados (Práctica 4). | Teorema de Kleene bidireccional verificado. | Pendiente de desarrollo P4. | **PENDIENTE** |
| **QA-P4-03** | `test_validadores.py` | Validación de Email, Teléfono (IFT) y URL vs `re.fullmatch` (P4). | 100 % de congruencia sobre $\ge 500$ cadenas. | Pendiente de desarrollo P4. | **PENDIENTE** |

---

## 2. Métricas Actuales de Ejecución
* **Total de Pruebas Automatizadas Ejecutadas:** 22
* **Aprobadas:** 22 (100 %)
* **Fallidas:** 0 (0 %)
* **Tiempo de Ejecución:** 0.29 segundos
