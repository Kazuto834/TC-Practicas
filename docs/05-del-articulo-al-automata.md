# EJERCICIO 5: DEL ARTÍCULO AL AUTÓMATA — MODELADO FORMAL DE PAC-MAN EXTENDIDO

**Práctica 2:** Autómatas Finitos No Deterministas (AFND) y Simulación de AFD con Interfaz Gráfica  
**Autor:** Mario García Castillo (`Kazuto834`) — `luilligar834@gmail.com`  
**Artículo de Referencia:** Gribkoff, E. (2013). *Applications of deterministic finite automata* [Documento de curso, ECS 120]. University of California, Davis. Figura 3: *Pac-Man Ghost Behaviors*.

---

## 1. Contexto y Justificación de la Ampliación

En el trabajo de Gribkoff (2013, Figura 3), el comportamiento de los fantasmas del videojuego *Pac-Man* (Namco, 1980) se modela mediante un autómata finito determinista de cuatro estados:
1. **Scatter (Dispersión):** El fantasma se dirige periódicamente a su esquina asignada en el laberinto.
2. **Chase (Persecución):** El fantasma persigue activamente la posición actual de Pac-Man.
3. **Frightened (Asustado):** Al consumir Pac-Man una píldora de poder (*Power Pellet*), los fantasmas se vuelven azules, vulnerables y se mueven aleatoriamente a menor velocidad.
4. **Eaten / ReturnHome (Comido):** Pac-Man colisiona con el fantasma asustado; los ojos del fantasma regresan a gran velocidad a la casa central (*Ghost House*) para regenerarse.

### Ampliación Propuesta (Dos Nuevos Estados y Dos Nuevos Eventos)
Para modelar con mayor fidelidad la inteligencia artificial reactiva descrita en la arquitectura original del juego desarrollada por Toru Iwatani, se incorporan:
* **Nuevo Estado 1: `Ambush` (Emboscada / Flanqueo Táctico):**
  * Modela la IA diferenciada de *Pinky* (el fantasma rosa). A diferencia de *Blinky* (que persigue linealmente la casilla de Pac-Man en modo `Chase`), en `Ambush` el fantasma no apunta a Pac-Man, sino a una posición proyectada cuatro casillas por delante de la orientación de movimiento de Pac-Man para cerrarle el paso.
* **Nuevo Estado 2: `Rage` (Furia / Modo Berserk):**
  * Modela el comportamiento clásico de *Cruise Elroy* (Blinky acelerado). Se dispara cuando el número de píldoras ordinarias restantes en el nivel cae por debajo de un umbral crítico ($\le 20$). El fantasma incrementa su velocidad y persigue sin retornar a modo de dispersión.
* **Nuevos Eventos en el Alfabeto:**
  * **`f` (Flanqueo detectado):** El algoritmo de navegación detecta que Pac-Man se aproxima a una intersección favorable para emboscada.
  * **`r` (Reserva crítica de píldoras):** Disparo de evento cuando el jugador ha comido la mayoría de píldoras del nivel.

---

## 2. Definición Formal de la Quíntupla

El sistema extendido se formaliza matemáticamente como:
$$M = (Q, \Sigma, \delta, q_0, F)$$

### 2.1 Conjunto Finito de Estados ($Q$)
$$Q = \{\text{Scatter}, \text{Chase}, \text{Frightened}, \text{Eaten}, \text{Ambush}, \text{Rage}\}$$

* **`Scatter` ($q_0$):** Estado inicial. Modo de patrullaje no letal enfocado en las esquinas perimetrales del mapa.
* **`Chase`:** Modo de persecución directa hacia las coordenadas actuales del jugador. Estado letal.
* **`Ambush`:** Modo de intercepción predictiva y corte de trayectoria. Estado letal.
* **`Rage`:** Modo de máxima agresividad y velocidad sostenida. Estado letal.
* **`Frightened`:** Modo de vulnerabilidad temporal con evasión aleatoria; el fantasma puede ser devorado.
* **`Eaten`:** Estado de tránsito de ojos desarmados dirigiéndose a la base central de regeneración.

### 2.2 Alfabeto de Entrada ($\Sigma$)
$$\Sigma = \{t, p, c, h, f, r\}$$
* $t$ (*Timer*): Expiración del temporizador de fase global del nivel.
* $p$ (*Power Pellet*): Pac-Man consume una píldora de poder.
* $c$ (*Collision*): Pac-Man colisiona con el fantasma mientras este se encuentra en estado vulnerable.
* $h$ (*Home reached*): Los ojos del fantasma alcanzan físicamente la casa central.
* $f$ (*Flank trigger*): Cambio de cuadrante de Pac-Man que habilita la ruta de emboscada.
* $r$ (*Rage trigger*): Quedan menos de 20 píldoras en el tablero.

### 2.3 Estado Inicial y Conjunto de Estados de Aceptación
* **Estado Inicial:** $q_0 = \text{Scatter}$
* **Estados de Aceptación ($F$):**
  $$F = \{\text{Chase}, \text{Ambush}, \text{Rage}\}$$
  *Justificación de $F$:* Un estado de aceptación modela formalmente que el fantasma se encuentra en **modo de ataque letal activo**, donde cualquier contacto físico con Pac-Man resulta en la pérdida de una vida para el jugador.

### 2.4 Tabla de Transición de Estados ($\delta$)

| Estado Origen | $t$ (Timer) | $p$ (Power) | $c$ (Colisión) | $h$ (Home) | $f$ (Flanqueo) | $r$ (Rage) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| $\to$ `Scatter` | `Chase` | `Frightened` | — | — | `Ambush` | `Rage` |
| $*$ `Chase` | `Scatter` | `Frightened` | — | — | `Ambush` | `Rage` |
| $*$ `Ambush` | `Chase` | `Frightened` | — | — | — | `Rage` |
| $*$ `Rage` | `Chase` | `Frightened` | — | — | — | — |
| `Frightened` | `Chase` | `Frightened` | `Eaten` | — | — | — |
| `Eaten` | — | — | — | `Scatter` | — | — |

---

## 3. Verificación Experimental: Batería de 10 Cadenas de Prueba

Las siguientes diez cadenas fueron ejecutadas y verificadas tanto en el simulador desarrollado (`src/gui_simulador.py`) como en la suite automatizada `tests/test_pacman.py`:

| N.º | Cadena | Recorrido de Estados | Resultado Esperado | Resultado Obtenido | Estado QA |
| :---: | :---: | :--- | :---: | :---: | :---: |
| 1 | `t` | `Scatter` $\xrightarrow{t}$ `Chase` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 2 | `tf` | `Scatter` $\xrightarrow{t}$ `Chase` $\xrightarrow{f}$ `Ambush` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 3 | `p` | `Scatter` $\xrightarrow{p}$ `Frightened` | RECHAZADA (Vulnerable) | RECHAZADA | **APROBADO** |
| 4 | `pch` | `Scatter` $\xrightarrow{p}$ `Frightened` $\xrightarrow{c}$ `Eaten` $\xrightarrow{h}$ `Scatter` | RECHAZADA (No letal) | RECHAZADA | **APROBADO** |
| 5 | `pcht` | `Scatter` $\xrightarrow{p}$ `Frightened` $\xrightarrow{c}$ `Eaten` $\xrightarrow{h}$ `Scatter` $\xrightarrow{t}$ `Chase` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 6 | `r` | `Scatter` $\xrightarrow{r}$ `Rage` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 7 | `rt` | `Scatter` $\xrightarrow{r}$ `Rage` $\xrightarrow{t}$ `Chase` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 8 | `rp` | `Scatter` $\xrightarrow{r}$ `Rage` $\xrightarrow{p}$ `Frightened` | RECHAZADA (Vulnerable) | RECHAZADA | **APROBADO** |
| 9 | `pt` | `Scatter` $\xrightarrow{p}$ `Frightened` $\xrightarrow{t}$ `Chase` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |
| 10 | `f` | `Scatter` $\xrightarrow{f}$ `Ambush` | ACEPTADA (Letal) | ACEPTADA | **APROBADO** |

---

## 4. Ensayo sobre la Abstracción del Modelo (Media Cuartilla)

El poder analítico de la Teoría de Autómatas reside en su capacidad de aislar la esencia cualitativa de un sistema dinámico complejo prescindiendo del ruido continuo irrelevante. En este ejercicio, el modelo formal de estados finitos captura con precisión matemática la **lógica de control modal y reactiva** del agente: define con exactitud cuándo el fantasma representa una amenaza letal para el jugador ($F = \{\text{Chase}, \text{Ambush}, \text{Rage}\}$), cuándo se encuentra en estado vulnerable y receptivo a colisiones destructivas (`Frightened`), y la causalidad obligatoria de retorno a la base antes de recuperar la operatividad normal (`Eaten` $\xrightarrow{h}$ `Scatter`). Las transiciones modelan adecuadamente las interrupciones del entorno (el consumo de una píldora de poder interrumpe inmediatamente cualquier modo agresivo previo) y la persistencia de modos críticos de final de nivel (`Rage`).

Por otro lado, la abstracción deliberadamente deja fuera toda la dimensión espacial y cinemática continua del videojuego: no modela la posición euclidiana $(x, y)$ de los personajes, la geometría del laberinto, los muros ni las decisiones de giro en cada casilla de intersección. Tampoco modela las velocidades diferenciales en píxeles por segundo (por ejemplo, el hecho de que en el juego real un fantasma en modo `Eaten` se desplace al doble de velocidad que Pac-Man, o que en `Frightened` su velocidad se reduzca a la mitad). Finalmente, el modelo abstracto asume que eventos como el temporizador ($t$) o la llegada a casa ($h$) son símbolos atómicos discretos generados externamente, abstrayendo los bucles de reloj de hardware y las rutinas de búsqueda de caminos (*pathfinding* A* o cálculo de distancia Manhattan) que calculan localmente el siguiente paso del fantasma. Esta simplificación demuestra cómo un autómata finito determinista es el formalismo óptimo para gobernar la máquina de estados de alto nivel de una IA en tiempo real sin saturar la memoria del sistema.
