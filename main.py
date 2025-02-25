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
    screen_width, screen_height = WIDTH, HEIGHT
    win = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Lunar Lander - Carte infinie et caméra centrée sur la fusée")

    # Chargement et redimensionnement des images
    rocket_img = pygame.transform.scale(pygame.image.load(ROCKET_IMG), (SHIP_WIDTH, SHIP_HEIGHT))
    flame_img = pygame.transform.scale(pygame.image.load(FLAME_IMG), (25, 40))

    ship = Ship()
    # Initialisation de la carte : de -screen_width à 2*screen_width
    map_start = -screen_width
    map_end = screen_width * 2
    map_points = []
    map_points += generate_map_segment(map_start, map_end, screen_height)
    map_points = add_flat_surfaces(map_points, FLAT_WIDTH)

    scroll_x = 0
    game_over = False
    landing_score = 0

    clock = pygame.time.Clock()
    running = True

    fuel_font = pygame.font.SysFont("comicsans", 30)
    end_font = pygame.font.SysFont("comicsans", 50)

    # Paramètres pour l'extension de la carte
    extend_threshold = 300
    segment_length = screen_width * 2

    while running:
        clock.tick(60)
        win.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                win = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                # Optionnel : adapter la carte en fonction de la nouvelle taille

        if not game_over:
            keys = pygame.key.get_pressed()

            # Contrôles de la fusée
            if keys[pygame.K_UP] and ship.fuel > 0:
                ship.velocity_x -= THRUST * math.sin(math.radians(ship.angle))
                ship.velocity_y -= THRUST * math.cos(math.radians(ship.angle))
                ship.fuel -= 1

            if keys[pygame.K_LEFT]:
                ship.angle += ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                ship.angle -= ROTATION_SPEED

            ship.velocity_y += GRAVITY
            ship.x += ship.velocity_x
            ship.y += ship.velocity_y
            ship.update()

            # Calcul du décalage pour centrer la caméra sur la fusée
            scroll_x = screen_width // 2 - ship.rect.centerx

            # Calcul des bords de la vue en fonction de la caméra
            view_left = ship.rect.centerx - screen_width // 2
            view_right = ship.rect.centerx + screen_width // 2

            # Génération de nouveaux segments si la vue approche des limites de la carte
            if view_right > map_end - extend_threshold:
                new_segment = generate_map_segment(map_end, map_end + segment_length, screen_height)
                new_segment = add_flat_surfaces(new_segment, FLAT_WIDTH)
                map_points.extend(new_segment)
                map_end += segment_length

            if view_left < map_start + extend_threshold:
                new_segment = generate_map_segment(map_start - segment_length, map_start, screen_height)
                new_segment = add_flat_surfaces(new_segment, FLAT_WIDTH)
                map_points = new_segment + map_points
                map_start -= segment_length

            # Gestion des collisions
            collision, map_y = check_collision(ship.rect, map_points, scroll_x)
            if collision:
                landing_score = calculate_landing_score(ship.velocity_y, ship.angle)
                game_over = True

            draw_mountain_map(win, map_points, scroll_x)

            # Dessin de la fusée en tenant compte du décalage de la caméra
            rotated_rocket = pygame.transform.rotate(rocket_img, ship.angle)
            # On centre la fusée sur la position calculée par la caméra
            rocket_draw_rect = rotated_rocket.get_rect(center=(ship.rect.centerx + scroll_x, ship.rect.centery))
            win.blit(rotated_rocket, rocket_draw_rect)

            # Placement amélioré de la flamme (avec le même décalage)
            if keys[pygame.K_UP] and ship.fuel > 0:
                offset_distance = SHIP_HEIGHT // 2 + 10
                offset_vector = pygame.math.Vector2(0, offset_distance).rotate(-ship.angle)
                flame_position = (ship.rect.centerx + scroll_x + offset_vector.x, ship.rect.centery + offset_vector.y)
                rotated_flame = pygame.transform.rotate(flame_img, ship.angle)
                win.blit(rotated_flame, rotated_flame.get_rect(center=flame_position))

            fuel_text = fuel_font.render(f"Carburant: {ship.fuel}", True, RED)
            win.blit(fuel_text, (10, 10))
        else:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill(TRANSPARENT_BLACK)
            win.blit(overlay, (0, 0))

            score_text = end_font.render(f"Score: {landing_score}/100", True, GREEN)
            replay_text = end_font.render("Appuyez sur ESPACE pour rejouer", True, GREEN)
            score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            replay_rect = replay_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

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
                ship.reset()
                game_over = False
                scroll_x = 0

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
