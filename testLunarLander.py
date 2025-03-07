import unittest
from game import generate_map_segment, add_flat_surfaces, check_collision, calculate_landing_score
from main import main
from settings import WIDTH, HEIGHT, SHIP_WIDTH, SHIP_HEIGHT, WHITE, BLACK, RED, GREEN, TRANSPARENT_BLACK, INITIAL_FUEL, GRAVITY, THRUST, ROTATION_SPEED, ROCKET_IMG, FLAME_IMG, MAP_WIDTH, FLAT_WIDTH
import pygame

class TestLunarLander(unittest.TestCase):

    def test_generate_map_segment(self):
        segment = generate_map_segment(0, 100, HEIGHT)
        self.assertTrue(len(segment) > 0)
        for point in segment:
            self.assertTrue(0 <= point[0] <= 100)
            self.assertTrue(HEIGHT * 0.5 <= point[1] <= HEIGHT * 0.9)

    def test_add_flat_surfaces(self):
        map_points = [(x, HEIGHT // 2) for x in range(300)]
        flat_map = add_flat_surfaces(map_points, 50)
        self.assertTrue(len(flat_map) == len(map_points))
        for i in range(0, len(flat_map), 150):
            self.assertTrue(flat_map[i][1] == flat_map[i + 49][1])

    def test_check_collision(self):
        map_points = [(0, HEIGHT), (100, HEIGHT - 50), (200, HEIGHT)]
        ship_rect = pygame.Rect(50, HEIGHT - 25, SHIP_WIDTH, SHIP_HEIGHT)
        collision, _ = check_collision(ship_rect, map_points, 0)
        self.assertTrue(collision)

    def test_calculate_landing_score(self):
        score = calculate_landing_score(0, 0)
        self.assertEqual(score, 100)
        score = calculate_landing_score(5, 5)
        self.assertTrue(score < 100)

    def test_main_function_call(self):
        # Teste que la fonction main ne lève pas d'exception lorsqu'elle est appelée
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_settings_constants(self):
        self.assertEqual(WIDTH, 800)
        self.assertEqual(HEIGHT, 600)
        self.assertEqual(WHITE, (255, 255, 255))
        self.assertEqual(BLACK, (0, 0, 0))
        self.assertEqual(RED, (255, 0, 0))
        self.assertEqual(GREEN, (0, 255, 0))
        self.assertEqual(TRANSPARENT_BLACK, (0, 0, 0, 128))
        self.assertEqual(INITIAL_FUEL, 1000)
        self.assertEqual(GRAVITY, 0.035)
        self.assertEqual(THRUST, 0.1)
        self.assertEqual(ROTATION_SPEED, 2)
        self.assertEqual(ROCKET_IMG, "assets/PngFusee.png")
        self.assertEqual(FLAME_IMG, "assets/PngParticule.png")
        self.assertEqual(MAP_WIDTH, WIDTH * 3)
        self.assertEqual(FLAT_WIDTH, 50)

if __name__ == '__main__':
    unittest.main()
