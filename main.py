import pygame
import random
import math

# --- Inicialización de Pygame ---
pygame.init()

# --- Constantes ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constantes del juego
PLAYER_WEIGHT = 60   # Peso fijo del jugador en kg
PLAYER_SPEED = 4      # Píxeles por frame que se mueve el jugador
BOARD_LENGTH = 400    # Longitud de la tabla (de -200 a 200)
GAME_OVER_ANGLE = 45  # Ángulo en grados para perder
TORQUE_FACTOR = 0.000009 # Sensibilidad de la física (ajústalo si es muy rápido/lento)
INITIAL_SPAWN_RATE = 120 # Frames entre cajas (2 segundos a 60 FPS)

# --- Configuración de la Pantalla ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Juego de Balance")
clock = pygame.time.Clock()
main_font = pygame.font.Font(None, 36)
box_font = pygame.font.Font(None, 20)
go_font = pygame.font.Font(None, 72)

# --- Clases del Juego ---

class Player:
    def __init__(self, peso):
        self.peso = peso
        self.pos_x = 0  # Posición horizontal relativa al centro (pivote)
        self.width = 20
        self.height = 40
        self.color = BLUE 

    def move(self, dx):
        # Mover al jugador, con límites para que no se caiga de la tabla
        self.pos_x += dx
        
        max_pos = (BOARD_LENGTH / 2) - (self.width / 2)
        if self.pos_x > max_pos:
            self.pos_x = max_pos
        if self.pos_x < -max_pos:
            self.pos_x = -max_pos

    def draw(self, surface, board_center_y, board_angle):
        # --- Lógica de Dibujo en Rotación ---
        rad_angle = math.radians(board_angle)
        
        # 1. Calcular la posición (x, y) de los pies del jugador sobre la tabla inclinada
        # (cx + r*cos(a), cy + r*sin(a)) donde r=pos_x
        # Usamos +sin() porque en pygame el eje Y está invertido (positivo es hacia abajo)
        foot_x = (SCREEN_WIDTH / 2) + self.pos_x * math.cos(rad_angle)
        foot_y = board_center_y + self.pos_x * math.sin(rad_angle)
        
        # 2. Calcular la esquina superior izquierda del rectángulo para dibujarlo
        # El jugador se dibuja "parado" (vertical), no inclinado
        draw_x = foot_x - (self.width / 2)
        draw_y = foot_y - self.height
        
        pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))


class Box:
    def __init__(self):
        self.peso = random.randint(10, 50) # Peso en KG
        # Posición X donde caerá (con un margen para que no caiga justo en el borde)
        self.pos_x = random.randint(int(-BOARD_LENGTH/2 + 20), int(BOARD_LENGTH/2 - 20))
        self.pos_y = 0 # Posición Y (superior de la caja)
        self.width = 30
        self.height = 30
        self.color = RED
        self.fall_speed = 3
        self.is_falling = True

    def update(self, board_center_y, board_angle):
        if self.is_falling:
            self.pos_y += self.fall_speed
            
            # --- Lógica de Colisión con Tabla Inclinada ---
            rad_angle = math.radians(board_angle)
            
            # Calcular la altura Y de la superficie de la tabla en el self.pos_x de la caja
            # board_y = center_y + x * sin(angle)
            board_height_at_x = board_center_y + self.pos_x * math.sin(rad_angle)

            # Comprobar si la parte inferior de la caja (self.pos_y + self.height) ha golpeado la tabla
            if self.pos_y + self.height >= board_height_at_x:
                self.pos_y = board_height_at_x - self.height # Ajustar la caja para que quede "sobre" la tabla
                self.is_falling = False

    def draw(self, surface, board_center_y, board_angle):
        rad_angle = math.radians(board_angle)
        
        if self.is_falling:
            # Dibujo simple mientras cae (centrado horizontalmente)
            draw_x = (SCREEN_WIDTH / 2) + self.pos_x - (self.width / 2)
            draw_y = self.pos_y
            pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))
        
        else:
            # --- Lógica de Dibujo en Rotación (cuando ya aterrizó) ---
            # 1. Calcular la posición (x, y) de la base de la caja
            base_x = (SCREEN_WIDTH / 2) + self.pos_x * math.cos(rad_angle)
            base_y = board_center_y + self.pos_x * math.sin(rad_angle)
            
            # 2. Calcular la esquina superior izquierda
            draw_x = base_x - (self.width / 2)
            draw_y = base_y - self.height
            pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.width, self.height))

        # Dibujar el peso (texto)
        # La posición del texto debe seguir a la caja
        text = box_font.render(f"{self.peso}kg", True, WHITE)
        text_rect = text.get_rect(center=(draw_x + self.width / 2, draw_y + self.height / 2))
        surface.blit(text, text_rect)


class Board:
    def __init__(self):
        self.angle = 0.0 # Ángulo en grados
        self.angular_velocity = 0.0 # Velocidad de rotación
        self.angular_acceleration = 0.0 # Aceleración de rotación
        
        self.length = BOARD_LENGTH
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT - 150 # Altura del pivote
        self.pivot_height = 50 # Altura del soporte

    def calculate_physics(self, player, boxes_on_board):
        # --- ESTA ES LA LÓGICA PRINCIPAL DEL JUEGO ---
        
        # 1. Calcular torque del jugador
        # Torque = Fuerza (Peso) * Distancia (pos_x)
        torque_player = player.peso * player.pos_x
        
        # 2. Calcular torque de las cajas (sumar todas las cajas)
        torque_boxes = 0
        for box in boxes_on_board:
            if not box.is_falling: # Asegurarse de que solo contamos cajas que han aterrizado
                torque_boxes += box.peso * box.pos_x
            
        # 3. Calcular Torque Neto
        # Si es positivo, gira a la derecha (sentido horario)
        # Si es negativo, gira a la izquierda (sentido anti-horario)
        net_torque = torque_player + torque_boxes
        
        # 4. Aplicar física
        # La aceleración angular es proporcional al torque neto.
        # Ajusta TORQUE_FACTOR para cambiar la "sensibilidad"
        self.angular_acceleration = net_torque * TORQUE_FACTOR
        
    def update(self):
        # Actualizar la física (integración simple)
        self.angular_velocity += self.angular_acceleration
        
        # Aplicar "fricción" o "amortiguación de velocidad"
        # Esto evita que gire infinitamente rápido y lo hace más controlable.
        self.angular_velocity *= 0.98 
        
        # Limitar la velocidad angular máxima
        max_vel = 5
        if self.angular_velocity > max_vel: self.angular_velocity = max_vel
        if self.angular_velocity < -max_vel: self.angular_velocity = -max_vel

        self.angle += self.angular_velocity

    def draw(self, surface):
        # 1. Dibujar el pivote (triángulo)
        pygame.draw.polygon(surface, GREEN, [
            (self.center_x, self.center_y),
            (self.center_x - 20, self.center_y + self.pivot_height),
            (self.center_x + 20, self.center_y + self.pivot_height)
        ])
        
        # 2. Calcular los puntos finales de la tabla basada en el ángulo
        rad_angle = math.radians(self.angle)
        half_len = self.length / 2
        
        # Punto izquierdo (start)
        start_x = self.center_x - (half_len * math.cos(rad_angle))
        start_y = self.center_y - (half_len * math.sin(rad_angle)) # -sin() = arriba
        
        # Punto derecho (end)
        end_x = self.center_x + (half_len * math.cos(rad_angle))
        end_y = self.center_y + (half_len * math.sin(rad_angle)) # +sin() = abajo
        
        # Dibujar la tabla (línea gruesa)
        pygame.draw.line(surface, WHITE, (start_x, start_y), (end_x, end_y), 10)

    def check_game_over(self):
        # Comprobar si la tabla tocó el "suelo" (ángulo máximo)
        if abs(self.angle) > GAME_OVER_ANGLE:
            return True
        return False

# --- Bucle Principal del Juego ---

def main():
    running = True
    game_over = False
    
    # Crear los objetos
    player = Player(peso=PLAYER_WEIGHT)
    board = Board()
    
    boxes = [] # Lista para guardar todas las cajas (cayendo y aterrizadas)
    
    box_spawn_timer = 0
    spawn_rate = INITIAL_SPAWN_RATE # El tiempo entre cajas irá disminuyendo
    time_survived = 0

    while running:
        # --- Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Reiniciar el juego
                    main() # Llama a main de nuevo para reiniciar
                    return # Salir de la instancia actual de main

        if not game_over:
            # --- Entradas (Input) ---
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move(-PLAYER_SPEED)
            if keys[pygame.K_RIGHT]:
                player.move(PLAYER_SPEED)

            # --- Actualización (Update) ---
            
            # 1. Spawneo de Cajas (con dificultad creciente)
            box_spawn_timer += 1
            if box_spawn_timer > spawn_rate:
                boxes.append(Box())
                box_spawn_timer = 0
                # Aumentar dificultad: hacer que aparezcan más rápido
                if spawn_rate > 30: # Límite de 0.5 segundos por caja
                    spawn_rate *= 0.98 # Se reduce un 2% cada vez

            # 2. Actualizar Cajas (hacerlas caer y detectar aterrizaje)
            boxes_on_board = []
            for box in boxes:
                box.update(board.center_y, board.angle)
                if not box.is_falling:
                    boxes_on_board.append(box)

            # 3. Calcular Física (El núcleo de tu lógica)
            board.calculate_physics(player, boxes_on_board)
            
            # 4. Actualizar Estado de la Tabla
            board.update()
            
            # 5. Actualizar Score
            time_survived += 1 / FPS # Sumar segundos

            # 6. Comprobar Game Over
            if board.check_game_over():
                game_over = True

        # --- Dibujo (Draw) ---
        screen.fill(BLACK)
        
        board.draw(screen)
        player.draw(screen, board.center_y, board.angle)
        for box in boxes:
            box.draw(screen, board.center_y, board.angle)
            
        # Dibujar Score
        score_text = main_font.render(f"Tiempo: {int(time_survived)}s", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            # Mostrar mensaje de Game Over
            go_text = go_font.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
            screen.blit(go_text, go_rect)
            
            restart_text = main_font.render("Presiona 'R' para reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
            screen.blit(restart_text, restart_rect)

        # Actualizar la pantalla
        pygame.display.flip()

        # Controlar FPS
        clock.tick(FPS)

    pygame.quit()

# --- Ejecutar el juego ---
if __name__ == "__main__":
    main()