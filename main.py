import pygame  # Importa la librería Pygame para crear la ventana y manejar gráficos.
import random  # Importa la librería para generar números aleatorios (pesos y posiciones).
import math    # Importa la librería matemática para funciones trigonométricas (seno, coseno).

# --- Inicialización de Pygame ---
pygame.init()  # Inicializa todos los módulos internos de Pygame (imprescindible para empezar).

# --- Constantes (Valores fijos del juego) ---
SCREEN_WIDTH = 800   # Ancho de la ventana en píxeles.
SCREEN_HEIGHT = 600  # Alto de la ventana en píxeles.
FPS = 60             # Cuadros por segundo: velocidad de actualización del juego.

# Definición de colores usando el formato RGB (Rojo, Verde, Azul).
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Variables de configuración de la física y jugabilidad.
PLAYER_WEIGHT = 60       # Peso del jugador para el cálculo de torque.
PLAYER_SPEED = 4         # Velocidad de movimiento lateral (píxeles por actualización).
BOARD_LENGTH = 400       # Largo total de la tabla de balance.
GAME_OVER_ANGLE = 45     # Ángulo límite de inclinación antes de perder.
TORQUE_FACTOR = 0.000009 # Factor de escala para convertir torque en aceleración (ajuste de sensibilidad).
INITIAL_SPAWN_RATE = 120 # Frames iniciales para que aparezca una caja (120 frames / 60 FPS = 2 segundos).

# --- Configuración de la Pantalla ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Crea la ventana gráfica.
pygame.display.set_caption("Juego de Balance") # Pone el título en la barra superior de la ventana.
clock = pygame.time.Clock() # Crea un reloj para controlar los FPS (velocidad del juego).

# Fuentes de texto para mostrar información en pantalla.
main_font = pygame.font.Font(None, 36) # Fuente por defecto, tamaño 36.
box_font = pygame.font.Font(None, 20)  # Fuente pequeña para los pesos de las cajas.
go_font = pygame.font.Font(None, 72)   # Fuente grande para "GAME OVER".

# --- Clases del Juego ---

class Player:
    def __init__(self, peso):
        self.peso = peso      # Guarda el peso del jugador.
        self.pos_x = 0        # Posición inicial en el centro de la tabla (0 es el pivote).
        self.width = 20       # Ancho visual del jugador.
        self.height = 40      # Alto visual del jugador.
        self.color = BLUE     # Color del jugador.

    def move(self, dx):
        # Actualiza la posición sumando el desplazamiento (dx puede ser positivo o negativo).
        self.pos_x += dx
        
        # Calcula el límite para que el jugador no se salga visualmente de la tabla.
        # Longitud media de la tabla menos la mitad del ancho del jugador.
        max_pos = (BOARD_LENGTH / 2) - (self.width / 2)
        
        # Si se pasa a la derecha, corregir posición al máximo permitido.
        if self.pos_x > max_pos:
            self.pos_x = max_pos
        # Si se pasa a la izquierda, corregir posición al mínimo permitido.
        if self.pos_x < -max_pos:
            self.pos_x = -max_pos

    def draw(self, surface, board_center_y, board_angle):
        # Convierte el ángulo de grados a radianes porque math.cos y math.sin usan radianes.
        rad_angle = math.radians(board_angle)
        
        # --- Cálculo de trigonometría para ubicar al jugador sobre la tabla inclinada ---
        # Coordenada X del pie: Centro pantalla + (Distancia desde el centro * Coseno del ángulo).
        # Esto proyecta la posición horizontal considerando la rotación.
        foot_x = (SCREEN_WIDTH / 2) + self.pos_x * math.cos(rad_angle)
        
        # Coordenada Y del pie: Centro Y de la tabla + (Distancia * Seno del ángulo).
        # Esto calcula cuánto sube o baja el punto de apoyo debido a la inclinación.
        foot_y = board_center_y + self.pos_x * math.sin(rad_angle)
        
        # Ajusta las coordenadas para dibujar desde la esquina superior izquierda del rectángulo.
        draw_x = foot_x - (self.width / 2) # Centrar horizontalmente respecto al punto de apoyo.
        draw_y = foot_y - self.height      # Subir la altura del jugador para que los pies toquen la tabla.
        
        # Dibuja el rectángulo del jugador en la pantalla.
        pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))


class Box:
    def __init__(self):
        # Asigna propiedades aleatorias a cada nueva caja.
        self.peso = random.randint(10, 50) # Peso aleatorio entre 10kg y 50kg.
        
        # Posición X aleatoria dentro de los límites de la tabla (-mitad a +mitad, con margen).
        self.pos_x = random.randint(int(-BOARD_LENGTH/2 + 20), int(BOARD_LENGTH/2 - 20))
        
        self.pos_y = 0         # Comienza en la parte superior de la pantalla.
        self.width = 30        # Ancho de la caja.
        self.height = 30       # Alto de la caja.
        self.color = RED       # Color de la caja.
        self.fall_speed = 3    # Velocidad de caída en píxeles.
        self.is_falling = True # Bandera (flag) para saber si está en el aire o ya cayó.

    def update(self, board_center_y, board_angle):
        # Solo actualizamos la posición si la caja está cayendo.
        if self.is_falling:
            self.pos_y += self.fall_speed # Aumenta Y para que baje.
            
            # --- Detección de colisión con la tabla ---
            rad_angle = math.radians(board_angle) # Convertir ángulo actual de la tabla a radianes.
            
            # Calculamos a qué altura (Y) está la tabla justo debajo de esta caja.
            # Y de la tabla = Centro Y + (Distancia X * Seno del ángulo).
            board_height_at_x = board_center_y + self.pos_x * math.sin(rad_angle)

            # Si la parte inferior de la caja (pos_y + height) toca o pasa la altura de la tabla...
            if self.pos_y + self.height >= board_height_at_x:
                self.pos_y = board_height_at_x - self.height # Corregir posición para que quede justo encima.
                self.is_falling = False # Marcar como "aterrizada", ahora es parte del peso de la tabla.

    def draw(self, surface, board_center_y, board_angle):
        rad_angle = math.radians(board_angle)
        
        if self.is_falling:
            # Si cae, dibujamos en coordenadas normales (sin rotación).
            # draw_x se calcula desde el centro de la pantalla + su desplazamiento relativo.
            draw_x = (SCREEN_WIDTH / 2) + self.pos_x - (self.width / 2)
            draw_y = self.pos_y
            pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))
        
        else:
            # Si ya aterrizó, debe rotar junto con la tabla.
            # Calculamos su posición rotada igual que con el jugador.
            base_x = (SCREEN_WIDTH / 2) + self.pos_x * math.cos(rad_angle)
            base_y = board_center_y + self.pos_x * math.sin(rad_angle)
            
            # Ajuste para dibujar desde la esquina superior izquierda.
            draw_x = base_x - (self.width / 2)
            draw_y = base_y - self.height
            pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))

        # --- Dibujar el texto del peso sobre la caja ---
        text = box_font.render(f"{self.peso}kg", True, WHITE) # Crear superficie de texto.
        # Obtener rectángulo centrado en la caja.
        text_rect = text.get_rect(center=(draw_x + self.width / 2, draw_y + self.height / 2))
        surface.blit(text, text_rect) # Dibujar el texto en la pantalla.


class Board:
    def __init__(self):
        # Variables físicas para la rotación.
        self.angle = 0.0               # Ángulo actual (posición).
        self.angular_velocity = 0.0    # Velocidad actual (qué tan rápido gira).
        self.angular_acceleration = 0.0 # Aceleración (cómo cambia la velocidad según el peso).
        
        self.length = BOARD_LENGTH     # Longitud de la tabla.
        self.center_x = SCREEN_WIDTH / 2 # Pivote en el centro horizontal.
        self.center_y = SCREEN_HEIGHT - 150 # Pivote cerca del fondo.
        self.pivot_height = 50         # Altura visual del soporte triangular.

    def calculate_physics(self, player, boxes_on_board):
        # --- Cálculo de momentos (Torque) ---
        # Torque = Fuerza x Distancia.
        
        # 1. Torque generado por el jugador:
        # Si pos_x es positivo (derecha), torque positivo (gira horario).
        # Si pos_x es negativo (izquierda), torque negativo (gira anti-horario).
        torque_player = player.peso * player.pos_x
        
        # 2. Torque generado por todas las cajas que han aterrizado.
        torque_boxes = 0
        for box in boxes_on_board:
            if not box.is_falling: # Doble verificación de seguridad.
                torque_boxes += box.peso * box.pos_x # Sumatoria de torques.
            
        # 3. Torque Neto (Suma total de fuerzas de rotación).
        net_torque = torque_player + torque_boxes
        
        # 4. Segunda Ley de Newton para rotación: Torque = Inercia * Aceleración.
        # Aquí simplificamos la Inercia asumiendo que es 1/TORQUE_FACTOR.
        self.angular_acceleration = net_torque * TORQUE_FACTOR
        
    def update(self):
        # --- Integración de Euler (Física básica) ---
        # Velocidad nueva = Velocidad actual + Aceleración.
        self.angular_velocity += self.angular_acceleration
        
        # --- Fricción / Amortiguación ---
        # Multiplicar por 0.98 reduce la velocidad un 2% en cada frame.
        # Esto evita que la tabla oscile eternamente como un péndulo perfecto.
        self.angular_velocity *= 0.98 
        
        # --- Límite de velocidad terminal ---
        # Evita que la tabla gire descontroladamente rápido (glitch visual).
        max_vel = 5
        if self.angular_velocity > max_vel: self.angular_velocity = max_vel
        if self.angular_velocity < -max_vel: self.angular_velocity = -max_vel

        # Posición nueva = Posición actual + Velocidad.
        self.angle += self.angular_velocity

    def draw(self, surface):
        # 1. Dibujar el triángulo de soporte (pivote).
        pygame.draw.polygon(surface, GREEN, [
            (self.center_x, self.center_y), # Punta superior (pivote).
            (self.center_x - 20, self.center_y + self.pivot_height), # Base izq.
            (self.center_x + 20, self.center_y + self.pivot_height)  # Base der.
        ])
        
        # 2. Calcular coordenadas de los extremos de la tabla para dibujar la línea.
        rad_angle = math.radians(self.angle)
        half_len = self.length / 2 # Distancia del centro a un extremo.
        
        # Trigonometría para encontrar el extremo izquierdo (start).
        # x = centro - radio * cos(a)
        start_x = self.center_x - (half_len * math.cos(rad_angle))
        # y = centro - radio * sin(a)
        start_y = self.center_y - (half_len * math.sin(rad_angle))
        
        # Trigonometría para encontrar el extremo derecho (end).
        # x = centro + radio * cos(a)
        end_x = self.center_x + (half_len * math.cos(rad_angle))
        # y = centro + radio * sin(a)
        end_y = self.center_y + (half_len * math.sin(rad_angle))
        
        # Dibujar la línea que representa la tabla.
        pygame.draw.line(surface, WHITE, (start_x, start_y), (end_x, end_y), 10)

    def check_game_over(self):
        # Si el valor absoluto del ángulo supera el límite, se pierde.
        if abs(self.angle) > GAME_OVER_ANGLE:
            return True
        return False

# --- Función Principal (Main Loop) ---

def main():
    running = True      # Controla si la ventana sigue abierta.
    game_over = False   # Controla el estado de "perdiste".
    
    # Instanciar objetos.
    player = Player(peso=PLAYER_WEIGHT) # Crear jugador.
    board = Board()                     # Crear tabla.
    
    boxes = [] # Lista vacía para almacenar objetos Box.
    
    box_spawn_timer = 0          # Contador de frames para generar cajas.
    spawn_rate = INITIAL_SPAWN_RATE # Frecuencia de generación actual.
    time_survived = 0            # Contador de tiempo de juego.

    while running:
        # --- Procesamiento de Eventos ---
        for event in pygame.event.get(): # Obtener cola de eventos (teclas, mouse, cerrar).
            if event.type == pygame.QUIT: # Si se da clic en la X de la ventana.
                running = False
            if event.type == pygame.KEYDOWN: # Si se presiona una tecla.
                if event.key == pygame.K_r and game_over:
                    # Reinicio: llamada recursiva a main() para empezar de cero.
                    main() 
                    return # Cierra la ejecución actual para no tener bucles dobles.

        if not game_over:
            # --- Lectura de Teclado Continuo ---
            keys = pygame.key.get_pressed() # Devuelve estado de todas las teclas.
            if keys[pygame.K_LEFT]:
                player.move(-PLAYER_SPEED) # Mover negativo (izquierda).
            if keys[pygame.K_RIGHT]:
                player.move(PLAYER_SPEED)  # Mover positivo (derecha).

            # --- Lógica del Juego ---
            
            # 1. Generador de cajas.
            box_spawn_timer += 1
            if box_spawn_timer > spawn_rate:
                boxes.append(Box()) # Crear nueva caja y añadir a la lista.
                box_spawn_timer = 0 # Resetear contador.
                
                # Aumentar dificultad reduciendo el tiempo de aparición.
                if spawn_rate > 30: 
                    spawn_rate *= 0.98 # Multiplicar por 0.98 reduce el valor un 2%.

            # 2. Filtrar cajas que están sobre la tabla para la física.
            boxes_on_board = []
            for box in boxes:
                box.update(board.center_y, board.angle) # Mover caja / chequear colisión.
                if not box.is_falling:
                    boxes_on_board.append(box) # Solo cajas aterrizadas cuentan para el peso.

            # 3. Calcular rotación de la tabla basada en pesos.
            board.calculate_physics(player, boxes_on_board)
            
            # 4. Mover la tabla según la física calculada.
            board.update()
            
            # 5. Sumar tiempo (1 / 60 segundos por frame).
            time_survived += 1 / FPS 

            # 6. Verificar condición de derrota.
            if board.check_game_over():
                game_over = True

        # --- Renderizado (Dibujo) ---
        screen.fill(BLACK) # Limpiar pantalla pintándola de negro.
        
        # Dibujar todos los elementos en su nueva posición.
        board.draw(screen)
        player.draw(screen, board.center_y, board.angle)
        for box in boxes:
            box.draw(screen, board.center_y, board.angle)
            
        # Dibujar el puntaje en la esquina.
        score_text = main_font.render(f"Tiempo: {int(time_survived)}s", True, WHITE)
        screen.blit(score_text, (10, 10)) # blit copia la superficie de texto a la pantalla principal.

        if game_over:
            # Dibujar mensajes de fin de juego en el centro.
            go_text = go_font.render("GAME OVER", True, RED)
            # get_rect(center=...) ayuda a centrar el texto automáticamente.
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
            screen.blit(go_text, go_rect)
            
            restart_text = main_font.render("Presiona 'R' para reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
            screen.blit(restart_text, restart_rect)

        # Intercambiar buffers (mostrar lo que acabamos de dibujar).
        pygame.display.flip()

        # Esperar lo necesario para mantener 60 FPS estables.
        clock.tick(FPS)

    pygame.quit() # Cerrar Pygame correctamente al salir del bucle.

# Bloque estándar de Python: asegura que main() solo corra si ejecutamos este archivo directamente.
if __name__ == "__main__":
    main()


#      /$$$$$$  /$$$$$$$  /$$$$$$ /$$$$$$$ 
#     /$$__  $$| $$__  $$|_  $$_/| $$__  $$
#    | $$  \__/| $$  \ $$  | $$  | $$  \ $$
#    | $$      | $$$$$$$/  | $$  | $$$$$$$/
#    | $$      | $$__  $$  | $$  | $$____/ 
#    | $$    $$| $$  \ $$  | $$  | $$      
#    |  $$$$$$/| $$  | $$ /$$$$$$| $$      
#     \______/ |__/  |__/|______/|__/      
#                                          
#                                          
#                                          