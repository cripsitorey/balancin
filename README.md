# Simulación de Balancín con Física de Torques (Juego de Balance)

**Versión:** 1.0.1  
**Autor:** Emilio Cuenca, Alex Gaior, Jose Velasco  
**Asignatura:** Lógica de Programación - Ingeniería en Sistemas

---

## 1. Descripción General

Este proyecto es una aplicación gráfica desarrollada en Python que simula un sistema físico de palanca de primer grado (balancín). El objetivo es mantener el equilibrio de una tabla basculante contrarrestando el peso de cajas que caen aleatoriamente, evitando que la inclinación supere el ángulo crítico mediante el movimiento estratégico de un personaje (contrapeso).

El sistema integra lógica de colisiones avanzada, cálculo de momentos de fuerza (torques) y renderizado gráfico en tiempo real utilizando la librería `pygame`.

---

## 2. Instalación y Ejecución

### Requisitos Previos
* **Python 3.8** o superior.
* **Pip** (Gestor de paquetes de Python).

### Pasos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/cripsitorey/balancin
    cd balancin
    ```

2.  **Instalar dependencias:**
    Se requiere la librería `pygame` para el renderizado y manejo de eventos.
    ```bash
    pip install pygame
    ```

3.  **Ejecutar el juego:**
    ```bash
    python main.py
    ```

---

## 3. Manual de Usuario

### Objetivo
Sobrevivir la mayor cantidad de tiempo posible manteniendo la tabla equilibrada. El juego termina (Game Over) si la inclinación de la tabla supera los **45 grados** y toca el suelo.

### Controles
El juego se controla exclusivamente mediante el teclado:

| Acción | Tecla | Descripción |
| :--- | :---: | :--- |
| **Mover a la Izquierda** | `🡄` (Flecha Izq) | Desplaza al personaje hacia el extremo izquierdo (genera torque negativo). |
| **Mover a la Derecha** | `🡆` (Flecha Der) | Desplaza al personaje hacia el extremo derecho (genera torque positivo). |
| **Reiniciar Juego** | `R` | Disponible únicamente en la pantalla de "GAME OVER". |
| **Salir** | `X` (Ventana) | Cierra la aplicación inmediatamente. |

### Interfaz (HUD) y Mecánicas
1.  **El Jugador (Bloque Azul):** Masa constante de **60kg**. Su distancia al centro determina el torque de control.
2.  **Las Cajas (Bloques Rojos):** Masa variable (**10-50kg**). Caen con frecuencia creciente. Al contactar la tabla, se convierten en parte del sistema físico.
3.  **Marcador de Tiempo:** Indica la duración de la sesión en segundos (Score).

---

## 4. Manual Técnico

### 4.1 Requerimientos del Sistema
* **Procesador:** Dual Core 2.0GHz o superior (recomendado para mantener 60 FPS estables).
* **RAM:** 2 GB mínimo.
* **Pantalla:** Resolución mínima de 800x600 píxeles.

### 4.2 Arquitectura del Código
El proyecto sigue el paradigma de **Programación Orientada a Objetos (POO)**. Todo el código fuente se encuentra en `main.py` para facilitar la portabilidad académica.

#### Estructura de Clases
* **`class Player`**: Gestiona la posición lineal del usuario y su renderizado relativo al ángulo de la tabla mediante transformación de coordenadas.
* **`class Box`**: Controla la caída libre, la detección de colisión con la superficie inclinada (plano rotado) y el estado de reposo.
* **`class Board`**: Núcleo de la simulación. Calcula la física del sistema, torques, aceleración angular y renderizado del pivote.

### 4.3 Lógica Física y Algoritmos

El motor físico implementa la **Segunda Ley de Newton para la rotación**.

#### Cálculo del Torque Neto
El equilibrio del sistema se determina mediante la sumatoria de momentos de fuerza ($\tau$):

$$
\tau_{neto} = \tau_{jugador} + \sum_{i=0}^{n} \tau_{caja_i}
$$

Donde cada torque individual se calcula como el producto del peso ($P$) por la distancia al pivote ($d$):

$$
\tau = P \cdot d
$$

* **Signo del Torque:**
    * $d > 0$ (Derecha): Torque positivo (Giro horario).
    * $d < 0$ (Izquierda): Torque negativo (Giro anti-horario).

#### Integración Numérica (Euler Semi-implícito)
En cada frame (1/60s), se actualiza el estado angular:

1.  **Aceleración Angular ($\alpha$):**
    `self.angular_acceleration = net_torque * TORQUE_FACTOR`
2.  **Velocidad Angular ($\omega$):**
    `self.angular_velocity += self.angular_acceleration`
3.  **Amortiguación (Damping):** Se aplica un factor de fricción (0.98) para simular resistencia del aire y evitar oscilación perpetua.
4.  **Posición Angular ($\theta$):**
    `self.angle += self.angular_velocity`

#### Detección de Colisiones en Superficie Inclinada
Para detectar el aterrizaje de una caja sobre la tabla rotada, no se puede usar una colisión AABB simple. Se calcula la altura $Y$ de la tabla en la coordenada $X$ específica de la caja usando trigonometría:

$$
Y_{tabla} = Y_{centro} + X_{caja} \cdot \sin(\theta)
$$

Si la posición vertical de la caja (`pos_y + height`) es mayor o igual a $Y_{tabla}$, se registra la colisión y la caja pasa a formar parte del sistema de torques.

---

**© 2025 Emilio Cuenca, Alex Gaibor, Jose Velasco .** Proyecto académico para la Universidad Internacional del Ecuador (UIDE).
