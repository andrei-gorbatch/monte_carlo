# Test utils.py

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from utils import dice_damage, calculate_attack_damage, calculate_group_hp

class TestUtils(unittest.TestCase):
    def test_dice_damage(self):
        # Test with 1d6
        self.assertIn(dice_damage(1, 6), range(1, 7))

        # Test with 2d6
        self.assertIn(dice_damage(2, 6), range(2, 13))

        # Test with 3d8
        self.assertIn(dice_damage(3, 8), range(3, 25))

        # Test with 4d10
        self.assertIn(dice_damage(4, 10), range(4, 41))

        # Test with 2d6 and crit
        self.assertIn(dice_damage(2, 6, True), range(4, 25))

    def test_calculate_attack_damage(self):
        self.assertIn(calculate_attack_damage('2d6+1d8+3'), range(6, 24))
        self.assertIn(calculate_attack_damage('2d6+1d8+3', to_attack = 20), range(9, 44))
        self.assertIn(calculate_attack_damage('1d4'), range(1, 5))
        self.assertIn(calculate_attack_damage('1d4+1d6'), range(2, 11))
        self.assertIn(calculate_attack_damage('1d4+1d6+1'), range(3, 12))
        self.assertIn(calculate_attack_damage('1d4+1d6+1', to_attack = 20), range(5, 22))
    
    def test_calculate_group_hp(self):
        # Test with empty list
        self.assertEqual(calculate_group_hp([]), 0)

        # Test with one creature
        class Creature:
            def __init__(self, hp):
                self.hp = hp

        creature = Creature(10)
        self.assertEqual(calculate_group_hp([creature]), 10)

        # Test with multiple creatures
        creature1 = Creature(10)
        creature2 = Creature(20)
        creature3 = Creature(30)
        self.assertEqual(calculate_group_hp([creature1, creature2, creature3]), 60)


if __name__ == '__main__':
    unittest.main()
