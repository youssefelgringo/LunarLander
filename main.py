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
        self.rect.center = (self.x + SHIP_WIDTH//2, self.y + SHIP_HEIGHT//2)

def draw_mountain_map(win, map_points, scroll_x):
    for i in range(len(map_points) - 1):
        pygame.draw.line(win, WHITE, (map_points[i][0] + scroll_x, map_points[i][1]),
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
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lunar Lander - Score à 0 en cas de Crash")

    # Initialisation des ressources
    rocket_img = pygame.transform.scale(pygame.image.load(ROCKET_IMG), (SHIP_WIDTH, SHIP_HEIGHT))
    flame_img = pygame.transform.scale(pygame.image.load(FLAME_IMG), (25, 40))

    ship = Ship()
    map_points = add_flat_surfaces(generate_complex_map(MAP_WIDTH, HEIGHT), FLAT_WIDTH)
    scroll_x = 0
    game_over = False
    landing_score = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        win.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

            # Gestion du défilement
            scroll_x = WIDTH//2 - ship.rect.centerx

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

            # Dessin de la flamme
            if keys[pygame.K_UP] and ship.fuel > 0:
                flame_pos = rotated_rocket.get_rect(center=ship.rect.center)
                flame_pos.y += 35
                win.blit(pygame.transform.rotate(flame_img, ship.angle), flame_pos)

            # Affichage du carburant
            font = pygame.font.SysFont("comicsans", 30)
            win.blit(font.render(f"Carburant: {ship.fuel}", True, RED), (10, 10))
        else:
            # Écran de fin
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(TRANSPARENT_BLACK)
            win.blit(overlay, (0, 0))

            font = pygame.font.SysFont("comicsans", 50)
            win.blit(font.render(f"Score: {landing_score}/100", True, GREEN), (WIDTH//2-100, HEIGHT//2-50))
            win.blit(font.render("Appuyez sur ESPACE pour rejouer", True, GREEN), (WIDTH//2-250, HEIGHT//2+50))

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                ship.reset()
                game_over = False
                scroll_x = 0

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()