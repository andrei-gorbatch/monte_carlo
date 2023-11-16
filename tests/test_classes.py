# Tests for the classes module

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from classes import character, martial, blaster

class TestCharacter(unittest.TestCase):
    def setUp(self):
        self.character = character("Test Character", 20, 10, 2, {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0}, False, "")

    def test_take_attack_damage(self):
        self.character.take_attack_damage((10, 5))
        self.assertEqual(self.character.hp, 15)

        self.character.take_attack_damage((5, 5))
        self.assertEqual(self.character.hp, 15)

    def test_take_heal(self):
        self.character.take_attack_damage((10, 5))
        self.character.take_heal(5)
        self.assertEqual(self.character.hp, 20)

        self.character.take_heal(10)
        self.assertEqual(self.character.hp, 20)

    def test_take_saving_throw_damage(self):
        self.character.take_saving_throw_damage(("str", 100, 0.5, 10))
        self.assertEqual(self.character.hp, 10)

        self.character.take_saving_throw_damage(("str", 0, 0.5, 10))
        self.assertEqual(self.character.hp, 5)

        self.character.take_saving_throw_damage(("str", 100, 0.5, 10))
        self.assertEqual(self.character.hp, 0)

    def test_take_damage_or_status(self):
        self.character.take_damage_or_status(("roll_to_attack", (10, 5)))
        self.assertEqual(self.character.hp, 15)

        self.character.take_damage_or_status(("roll_to_attack", (5, 5)))
        self.assertEqual(self.character.hp, 15)

        self.character.take_damage_or_status(("spell_attack", ("dex", 100, 0.5, 10)))
        self.assertEqual(self.character.hp, 5)

        self.character.take_damage_or_status(("spell_attack", ("dex", 0, 0, 2)))
        self.assertEqual(self.character.hp, 5)

        self.character.take_damage_or_status(("spell_attack", ("dex", 100, 0, 10)))
        self.assertEqual(self.character.hp, 0)

        self.character.take_damage_or_status(("heal", 5))
        self.assertEqual(self.character.hp, 5)

        self.character.take_damage_or_status(("heal", 100))
        self.assertEqual(self.character.hp, 20)


class TestMartial(unittest.TestCase):
    def setUp(self):
        self.martial = martial("Test Martial", 20, 10, 2, "1d6", 2, 0, {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0}, True, "1d6")

    def test_roll_to_attack(self):
        self.assertIn(self.martial.roll_to_attack()[0], range(2, 23))
        self.assertIn(self.martial.roll_to_attack()[1], range(1, 13))

    def test_best_action(self):
        self.assertEqual(self.martial.best_action("enemy")[0], "roll_to_attack")
        self.assertEqual(self.martial.best_action("ally")[0], "heal")
        self.martial.healer = False
        self.assertRaises(ValueError, self.martial.best_action, "ally")


class TestBlaster(unittest.TestCase):
    def setUp(self):
        self.blaster = blaster("Test Blaster", 20, 10, 12, "1d6", 2, 3, 0, {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0}, True, "1d6", "dex")

    def test_spell_attack(self):
        self.assertEqual(self.blaster.spell_attack()[0], "dex")
        self.assertEqual(self.blaster.spell_attack()[1], 12)
        self.assertIn(self.blaster.spell_attack()[2], range(1, 4))
        self.assertIn(self.blaster.spell_attack()[3], range(1, 7))

    def test_best_action(self):
        self.assertEqual(self.blaster.best_action("enemy")[0], "spell_attack")
        self.assertEqual(self.blaster.best_action("ally")[0], "heal")
        self.blaster.healer = False
        self.assertRaises(ValueError, self.blaster.best_action, "ally")

if __name__ == '__main__':
    unittest.main()
