import math
import random
import pygame
from settings import *

def generate_map_segment(start_x, end_x, height, spacing=50):
    # Génère des points de contrôle pour un relief de montagne réaliste sur un segment donné
    control_points = []
    for x in range(start_x, end_x + spacing, spacing):
        # Les montagnes se situent dans la partie basse de l'écran
        y = random.randint(int(height * 0.5), int(height * 0.9))
        control_points.append((x, y))
    segment_points = []
    for i in range(len(control_points) - 1):
        x1, y1 = control_points[i]
        x2, y2 = control_points[i + 1]
        for x in range(x1, x2):
            t = (x - x1) / (x2 - x1)
            y = int(y1 * (1 - t) + y2 * t) + random.randint(-3, 3)
            segment_points.append((x, y))
    return segment_points

def add_flat_surfaces(map_points, flat_width):
    # Ajoute plus fréquemment des zones d'atterrissage
    for i in range(len(map_points) - flat_width):
        if i % 150 == 0:  # Tous les 150 points, créer une zone plate
            y = map_points[i][1]
            for j in range(flat_width):
                map_points[i + j] = (map_points[i + j][0], y)
    return map_points

def draw_mountain_map(surface, map_points, scroll_x):
    for i in range(len(map_points) - 1):
        pygame.draw.line(surface, WHITE, 
                         (map_points[i][0] - scroll_x, map_points[i][1]),
                         (map_points[i + 1][0] - scroll_x, map_points[i + 1][1]), 2)

def check_collision(ship_rect, map_points, scroll_x):
    ship_bottom = ship_rect.bottom
    for i in range(len(map_points) - 1):
        x1, y1 = map_points[i]
        x2, y2 = map_points[i + 1]
        if x1 - scroll_x <= ship_rect.centerx <= x2 - scroll_x:
            map_y = y1 + (y2 - y1) * (ship_rect.centerx - (x1 - scroll_x)) / (x2 - x1)
            if ship_bottom >= map_y:
                return True, map_y
    return False, None

def calculate_landing_score(vertical_speed, angle):
    if abs(vertical_speed) > 2 or abs(angle) > 15:
        return 0
    return int(max(0, 50 - abs(vertical_speed) * 10) + max(0, 50 - abs(angle) * 2))
