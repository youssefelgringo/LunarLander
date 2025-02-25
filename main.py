import pygame
import math
import random
from settings import *
from game import generate_map_segment, add_flat_surfaces, calculate_landing_score

# Couleurs personnalisées pour le nouveau design
SKY_BLUE_DARK = (100, 149, 237)  # Bleu ciel un peu plus foncé
BROWN = (139, 69, 19)            # Marron pour le "dirt"
GRASS_GREEN = (34, 139, 34)      # Vert pour la simple couche en haut

def get_mountain_height(x, map_points):
    """
    Retourne la hauteur de la montagne (y) pour une coordonnée x donnée (en coordonnées monde).
    Si x n'est pas dans le range des points, on renvoie le bas de l'écran.
    """
    for i in range(len(map_points) - 1):
        x1, y1 = map_points[i]
        x2, y2 = map_points[i + 1]
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1)
            return y1 + (y2 - y1) * t
    return HEIGHT  # Par défaut si hors limite

def draw_mountain_map(win, map_points, scroll_x, screen_height):
    """
    Dessine la montagne avec un polygone marron (pour la terre)
    et une simple couche verte (ligne) au sommet.
    """
    # Polygone principal marron
    polygon_points = [(x + scroll_x, y) for (x, y) in map_points]
    polygon_points.append((map_points[-1][0] + scroll_x, screen_height))
    polygon_points.append((map_points[0][0] + scroll_x, screen_height))
    pygame.draw.polygon(win, BROWN, polygon_points)

    # Ligne verte au sommet
    top_line = [(x + scroll_x, y) for (x, y) in map_points]
    pygame.draw.lines(win, GRASS_GREEN, False, top_line, 5)

def check_collision(rect, map_points):
    """
    Vérifie si rect (vaisseau) entre en collision avec un segment
    de la montagne. Renvoie (True, y_collision) ou (False, None).
    """
    for i in range(len(map_points) - 1):
        p1 = map_points[i]
        p2 = map_points[i + 1]
        if rect.clipline(p1, p2):
            return True, p1[1]
    return False, None

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

def main():
    pygame.init()
    # Passage en mode plein écran
    win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width = win.get_width()
    screen_height = win.get_height()
    pygame.display.set_caption("Lunar Lander - Carte infinie et caméra centrée sur la fusée")

    # Chargement des images
    try:
        menu_bg = pygame.image.load("assets/menu_background.png")
        menu_bg = pygame.transform.scale(menu_bg, (screen_width, screen_height))
    except Exception:
        menu_bg = None

    rocket_img = pygame.transform.scale(pygame.image.load(ROCKET_IMG), (SHIP_WIDTH, SHIP_HEIGHT))
    flame_img = pygame.transform.scale(pygame.image.load(FLAME_IMG), (25, 40))

    # Chargement de la police "Retro Gaming"
    title_font = pygame.font.Font("assets/RetroGaming.ttf", 80)
    menu_font = pygame.font.Font("assets/RetroGaming.ttf", 40)
    fuel_font = pygame.font.Font("assets/RetroGaming.ttf", 30)
    end_font = pygame.font.Font("assets/RetroGaming.ttf", 50)

    clock = pygame.time.Clock()

    # États possibles : "menu", "playing", "game_over"
    state = "menu"

    # Variables de jeu dans le scope de main
    ship = None
    map_points = []
    map_start = 0
    map_end = 0
    scroll_x = 0
    landing_score = 0
    extend_threshold = 300
    segment_length = screen_width * 2

    # Liste des arbres (pas de collisions)
    trees = []

    def place_trees():
        """
        Place aléatoirement des arbres sur la carte, sans collision.
        Chaque arbre a un x aléatoire et on calcule sa hauteur
        en fonction du relief.
        """
        nonlocal trees
        trees = []
        # Par exemple, un arbre tous les ~400-600 pixels
        x = map_start
        while x < map_end:
            x += random.randint(400, 600)
            y = get_mountain_height(x, map_points)
            trees.append({"x": x, "y": y})

    def draw_trees(win, scroll_x):
        """
        Dessine les arbres (un simple tronc rectangulaire + feuillage circulaire).
        Pas de collisions.
        """
        for tree in trees:
            tx = tree["x"] + scroll_x
            ty = tree["y"]
            # Tronc (marron foncé)
            pygame.draw.rect(win, (101, 67, 33), (tx - 5, ty, 10, 30))
            # Feuillage (cercle vert)
            pygame.draw.circle(win, (0, 128, 0), (int(tx), int(ty) - 10), 20)

    def init_game():
        nonlocal ship, map_points, map_start, map_end, scroll_x, landing_score, extend_threshold, segment_length, trees

        ship = Ship()
        map_start = -screen_width
        map_end = screen_width * 2
        map_points = []
        map_points += generate_map_segment(map_start, map_end, screen_height)
        map_points = add_flat_surfaces(map_points, FLAT_WIDTH)
        scroll_x = 0
        landing_score = 0
        extend_threshold = 300
        segment_length = screen_width * 2

        # On place les arbres après avoir généré la carte
        place_trees()

    running = True
    while running:
        clock.tick(60)

        # Gestion des événements globaux (fermeture, ESC pour quitter)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if state == "menu":
            # Écran d'accueil
            if menu_bg:
                win.blit(menu_bg, (0, 0))
            else:
                win.fill(SKY_BLUE_DARK)

            title_text = title_font.render("Lunar Lander", True, WHITE)
            start_text = menu_font.render("Appuyez sur ENTREE pour démarrer", True, GREEN)
            quit_text = menu_font.render("Appuyez sur ECHAP pour quitter", True, RED)
            title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
            start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2))
            quit_rect = quit_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            win.blit(title_text, title_rect)
            win.blit(start_text, start_rect)
            win.blit(quit_text, quit_rect)
            pygame.display.update()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                init_game()
                state = "playing"
                pygame.time.delay(300)  # Pour éviter une action multiple involontaire

        elif state == "playing":
            # Fond du ciel plus foncé
            win.fill(SKY_BLUE_DARK)
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

            # Génération de nouveaux segments si nécessaire
            view_left = ship.rect.centerx - screen_width // 2
            view_right = ship.rect.centerx + screen_width // 2

            if view_right > map_end - extend_threshold:
                new_segment = generate_map_segment(map_end, map_end + segment_length, screen_height)
                new_segment = add_flat_surfaces(new_segment, FLAT_WIDTH)
                map_points.extend(new_segment)
                map_end += segment_length
                place_trees()  # On replace des arbres sur la nouvelle zone

            if view_left < map_start + extend_threshold:
                new_segment = generate_map_segment(map_start - segment_length, map_start, screen_height)
                new_segment = add_flat_surfaces(new_segment, FLAT_WIDTH)
                map_points = new_segment + map_points
                map_start -= segment_length
                place_trees()

            # Détection des collisions
            collision, map_y = check_collision(ship.rect, map_points)
            if collision:
                landing_score = calculate_landing_score(ship.velocity_y, ship.angle)
                state = "game_over"

            # Dessin de la montagne (fond marron + simple ligne verte)
            draw_mountain_map(win, map_points, scroll_x, screen_height)

            # Dessin des arbres (sans collision)
            draw_trees(win, scroll_x)

            # Affichage de la fusée avec décalage
            rotated_rocket = pygame.transform.rotate(rocket_img, ship.angle)
            rocket_draw_rect = rotated_rocket.get_rect(center=(ship.rect.centerx + scroll_x, ship.rect.centery))
            win.blit(rotated_rocket, rocket_draw_rect)

            # Affichage de la flamme lors de l'accélération
            if keys[pygame.K_UP] and ship.fuel > 0:
                offset_distance = SHIP_HEIGHT // 2 + 10
                offset_vector = pygame.math.Vector2(0, offset_distance).rotate(-ship.angle)
                flame_position = (ship.rect.centerx + scroll_x + offset_vector.x, ship.rect.centery + offset_vector.y)
                rotated_flame = pygame.transform.rotate(flame_img, ship.angle)
                win.blit(rotated_flame, rotated_flame.get_rect(center=flame_position))

            # Affichage du carburant et de la vitesse (en km/h)
            fuel_text = fuel_font.render(f"Carburant: {ship.fuel}", True, RED)
            win.blit(fuel_text, (10, 10))
            speed_pixels = (ship.velocity_x**2 + ship.velocity_y**2) ** 0.5
            speed_km_h = speed_pixels * 100  # Facteur de conversion (ajustable)
            speed_text = fuel_font.render(f"Vitesse: {int(speed_km_h)} km/h", True, WHITE)
            win.blit(speed_text, (10, 40))

            pygame.display.update()

        elif state == "game_over":
            # Écran de fin
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            win.blit(overlay, (0, 0))

            score_text = end_font.render(f"Score: {landing_score}/100", True, GREEN)
            replay_text = end_font.render("Appuyez sur ESPACE pour rejouer", True, GREEN)
            menu_text = end_font.render("Appuyez sur M pour le menu", True, GREEN)
            score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            replay_rect = replay_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            menu_rect = menu_text.get_rect(center=(screen_width // 2, screen_height // 2 + 110))
            win.blit(score_text, score_rect)
            win.blit(replay_text, replay_rect)
            win.blit(menu_text, menu_rect)
            pygame.display.update()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                init_game()
                state = "playing"
                pygame.time.delay(300)
            if keys[pygame.K_m]:
                state = "menu"
                pygame.time.delay(300)

    pygame.quit()

if __name__ == "__main__":
    main()
