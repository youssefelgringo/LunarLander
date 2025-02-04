import math
import random
import pygame
from settings import *

def generate_complex_map(width, height):
    map_points = []
    for x in range(width):
        y = (
            int(math.sin(x / 50) * 50) +
            int(math.sin(x / 20) * 20) +
            int(math.sin(x / 100) * 100) +
            random.randint(-10, 10)
        )
        y = max(100, min(height - 100, y + height * 0.5))
        map_points.append((x, y))
    return map_points

def add_flat_surfaces(map_points, flat_width):
    for i in range(len(map_points) - flat_width):
        if i % 300 == 0:
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