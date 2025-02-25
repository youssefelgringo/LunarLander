import pygame
import math
from settings import *
from game import *

class Ship:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = INITIAL_SHIP_X
        self.y = INITIAL_SHIP_Y
        self.velocity_x = 0
        self.velocity_y = 0
        self.fuel = INITIAL_FUEL
        self.angle = 0
        self.rect = pygame.Rect(self.x, self.y, SHIP_WIDTH, SHIP_HEIGHT)

    def update(self):
        self.rect.center = (self.x + SHIP_WIDTH // 2, self.y + SHIP_HEIGHT // 2)

def draw_mountain_map(win, map_points, scroll_x):
    for i in range(len(map_points) - 1):
        pygame.draw.line(win, WHITE,
                         (map_points[i][0] + scroll_x, map_points[i][1]),
                         (map_points[i + 1][0] + scroll_x, map_points[i + 1][1]), 2)

def check_collision(rect, map_points, scroll_x):
    for i in range(len(map_points) - 1):
        p1 = (map_points[i][0] + scroll_x, map_points[i][1])
        p2 = (map_points[i + 1][0] + scroll_x, map_points[i + 1][1])
        if rect.clipline(p1, p2):
            return True, p1[1]
    return False, None

def main():
    pygame.init()
    # Variables pour la taille de la fenêtre qui s'adaptent au redimensionnement
    screen_width, screen_height = WIDTH, HEIGHT
    win = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Lunar Lander - Score à 0 en cas de Crash")

    # Initialisation des ressources
    rocket_img = pygame.transform.scale(pygame.image.load(ROCKET_IMG), (SHIP_WIDTH, SHIP_HEIGHT))
    flame_img = pygame.transform.scale(pygame.image.load(FLAME_IMG), (25, 40))

    ship = Ship()
    # On régénère la map en fonction de la taille actuelle de la fenêtre
    map_points = add_flat_surfaces(generate_complex_map(screen_width * 3, screen_height), FLAT_WIDTH)
    scroll_x = 0
    game_over = False
    landing_score = 0

    clock = pygame.time.Clock()
    running = True

    # Préparation des polices
    fuel_font = pygame.font.SysFont("comicsans", 30)
    end_font = pygame.font.SysFont("comicsans", 50)

    while running:
        clock.tick(60)
        win.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                win = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                # Optionnel : régénérer la map avec la nouvelle taille si besoin
                map_points = add_flat_surfaces(generate_complex_map(screen_width * 3, screen_height), FLAT_WIDTH)

        if not game_over:
            keys = pygame.key.get_pressed()

            # Gestion des contrôles
            if keys[pygame.K_UP] and ship.fuel > 0:
                ship.velocity_x -= THRUST * math.sin(math.radians(ship.angle))
                ship.velocity_y -= THRUST * math.cos(math.radians(ship.angle))
                ship.fuel -= 1

            if keys[pygame.K_LEFT]:
                ship.angle += ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                ship.angle -= ROTATION_SPEED

            # Application de la gravité
            ship.velocity_y += GRAVITY
            ship.x += ship.velocity_x
            ship.y += ship.velocity_y
            ship.update()

            # Gestion du défilement centré sur le vaisseau
            scroll_x = screen_width // 2 - ship.rect.centerx

            # Collision et score
            collision, map_y = check_collision(ship.rect, map_points, scroll_x)
            if collision:
                landing_score = calculate_landing_score(ship.velocity_y, ship.angle)
                game_over = True

            # Dessin de la map
            draw_mountain_map(win, map_points, scroll_x)

            # Dessin du vaisseau
            rotated_rocket = pygame.transform.rotate(rocket_img, ship.angle)
            win.blit(rotated_rocket, rotated_rocket.get_rect(center=ship.rect.center))

            # Placement amélioré de la flamme :
            if keys[pygame.K_UP] and ship.fuel > 0:
                # Calcule un décalage depuis le centre du vaisseau, aligné dans la direction opposée à la poussée
                offset_distance = SHIP_HEIGHT // 2 + 10  # 10 pixels supplémentaires pour que la flamme déborde
                offset_vector = pygame.math.Vector2(0, offset_distance).rotate(-ship.angle)
                flame_position = (ship.rect.centerx + offset_vector.x, ship.rect.centery + offset_vector.y)
                rotated_flame = pygame.transform.rotate(flame_img, ship.angle)
                win.blit(rotated_flame, rotated_flame.get_rect(center=flame_position))

            # Affichage du carburant
            fuel_text = fuel_font.render(f"Carburant: {ship.fuel}", True, RED)
            win.blit(fuel_text, (10, 10))
        else:
            # Écran de fin avec overlay semi-transparent
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill(TRANSPARENT_BLACK)
            win.blit(overlay, (0, 0))

            # Préparer les textes et centrer leur affichage
            score_text = end_font.render(f"Score: {landing_score}/100", True, GREEN)
            replay_text = end_font.render("Appuyez sur ESPACE pour rejouer", True, GREEN)
            score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            replay_rect = replay_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

            # Ajout d'une ombre légère pour embellir le rendu
            shadow_offset = 2
            score_shadow = end_font.render(f"Score: {landing_score}/100", True, BLACK)
            replay_shadow = end_font.render("Appuyez sur ESPACE pour rejouer", True, BLACK)
            score_shadow_rect = score_rect.copy()
            replay_shadow_rect = replay_rect.copy()
            score_shadow_rect.x += shadow_offset
            score_shadow_rect.y += shadow_offset
            replay_shadow_rect.x += shadow_offset
            replay_shadow_rect.y += shadow_offset

            win.blit(score_shadow, score_shadow_rect)
            win.blit(score_text, score_rect)
            win.blit(replay_shadow, replay_shadow_rect)
            win.blit(replay_text, replay_rect)

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                # Réinitialisation du jeu
                ship.reset()
                game_over = False
                scroll_x = 0

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
