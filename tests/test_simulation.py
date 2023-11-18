# Unit tests for simulation.py

import unittest
import pandas as pd
import numpy as np
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import sample_data_path, tests_path, output_data_path, monte_carlo_iterations
from simulation import validate_excel_file, validate_dice_cols, ingest_creatures_from_excel, choose_attack_target, choose_heal_target, action, initialize_combat, run_one_combat, monte_carlo, data_analysis
from utils import calculate_group_hp

class TestExcelIngest(unittest.TestCase):
    def test_validate_excel_file(self):
        # Test with sample excel file
        self.assertIsNone(validate_excel_file(sample_data_path/'character_info.xlsx'))

        # Test with invalid excel file
        self.assertRaises(ValueError, validate_excel_file, tests_path/'invalid.xlsx')

    def test_validate_dice_cols(self):
        # Test with valid dice columns
        valid_cols = pd.Series(['1d6', '2d8+3', np.nan])
        self.assertIsNone(validate_dice_cols(valid_cols))

        # Test with invalid dice columns
        invalid_cols = pd.Series(['1d6', '2d8+3', 'invalid', '3d6+1d4'])
        with self.assertRaises(ValueError):
            validate_dice_cols(invalid_cols)
 
    def test_ingest_creatures_from_excel(self):
        # Test with sample excel file
        characters_dict = ingest_creatures_from_excel(input_file=sample_data_path/'character_info.xlsx')
        self.assertEqual(len(characters_dict), 2)
        self.assertEqual(len(characters_dict['heroes']), 3)
        self.assertEqual(len(characters_dict['monsters']), 3)
        self.assertEqual(characters_dict['heroes'][0].name, 'Barbarian')
        self.assertEqual(characters_dict['heroes'][0].hp, 12)
        self.assertEqual(characters_dict['monsters'][0].ac, 14)
        self.assertEqual(characters_dict['heroes'][1].saves, {'str': 3, 'dex': 4, 'con': 3, 'wis': 0, 'cha': 0, 'int': -1})
        self.assertEqual(characters_dict['heroes'][2].initiative_bonus, 0)
        self.assertEqual(characters_dict['heroes'][2].healer, True)
        self.assertEqual(characters_dict['monsters'][1].number_of_attacks, 1)
        self.assertEqual(characters_dict['monsters'][0].attack_bonus, 2)
        self.assertEqual(characters_dict['monsters'][2].number_of_targets, 2)
        self.assertEqual(characters_dict['monsters'][2].spell_save_dc, 13)
        self.assertEqual(characters_dict['monsters'][2].targeted_save, 'dex')
        self.assertEqual(characters_dict['monsters'][2].saved_damage, 0)
        self.assertEqual(characters_dict['heroes'][0].attack_damage, '2d6+4')

        
class TestCharacterActions(unittest.TestCase):
    def setUp(self):
        self.characters_dict = ingest_creatures_from_excel(sample_data_path/'character_info.xlsx')
        self.heroes = self.characters_dict['heroes']
        self.monsters = self.characters_dict['monsters']

    def test_choose_attack_target(self):
        # Test with heroes attacking monsters
        character = self.heroes[0]
        target_type, targets = choose_attack_target(character, self.heroes, self.monsters, number_of_targets=1)
        self.assertEqual(target_type, "enemy")
        self.assertIn(targets[0], self.monsters)

        # Test with monsters attacking heroes
        character = self.monsters[0]
        target_type, targets = choose_attack_target(character, self.heroes, self.monsters, number_of_targets=1)
        self.assertEqual(target_type, "enemy")
        self.assertIn(targets[0], self.heroes)

        # Test with multiple targets
        character = self.monsters[2]
        target_type, targets = choose_attack_target(character, self.heroes, self.monsters, number_of_targets=2)
        self.assertEqual(target_type, "enemy")
        self.assertEqual(len(targets), 2)
        self.assertIn(targets[0], self.heroes)
        self.assertIn(targets[1], self.heroes)
        self.assertNotEqual(targets[0], targets[1])

        # Test with no potential targets
        self.heroes[0].hp = 0
        self.heroes[1].hp = 0
        self.heroes[2].hp = 0
        character = self.monsters[0]
        target_type, targets = choose_attack_target(character, self.heroes, self.monsters, number_of_targets=1)
        self.assertIsNone(targets)


    def test_choose_heal_target(self):
        # Test with no potential targets
        character = self.heroes[2]
        target_type, target = choose_heal_target(character, self.heroes, self.monsters)
        self.assertIsNone(target)

        # Test with one potential target
        self.heroes[1].hp = 0
        character = self.heroes[2]
        target_type, target = choose_heal_target(character, self.heroes, self.monsters)
        self.assertEqual(target_type, "ally")
        self.assertEqual(target, self.heroes[1])

        # Test with multiple potential targets
        self.heroes[0].hp = 0
        self.heroes[1].hp = 0
        character = self.heroes[2]
        target_type, target = choose_heal_target(character, self.heroes, self.monsters)
        self.assertEqual(target_type, "ally")
        self.assertIn(target, [self.heroes[0], self.heroes[1]])

        # Test with no allies at 0hp
        character = self.monsters[2]
        target_type, target = choose_heal_target(character, self.heroes, self.monsters)
        self.assertIsNone(target)

        # Test with healer = False
        character = self.monsters[0]
        target_type, target = choose_heal_target(character, self.heroes, self.monsters)
        self.assertIsNone(target)

    def test_action(self):
        # Test with a martial character attacking an enemy
        character = self.heroes[0]
        character.attack_bonus = 100
        monsters_hp_initial = calculate_group_hp(self.monsters)
        action(character, self.heroes, self.monsters)
        monsters_hp_final = calculate_group_hp(self.monsters)
        self.assertLess(monsters_hp_final, monsters_hp_initial)

        # Test with a blaster character attacking an enemy
        character = self.heroes[2]
        character.spell_save_dc = 100
        monsters_hp_initial = calculate_group_hp(self.monsters)
        action(character, self.heroes, self.monsters)
        monsters_hp_final = calculate_group_hp(self.monsters)
        self.assertLess(monsters_hp_final, monsters_hp_initial)

        # Test with a healer character healing an ally
        character = self.heroes[2]
        self.heroes[1].hp = 0
        action(character, self.heroes, self.monsters)
        self.assertGreater(self.heroes[1].hp, 0)

class TestCombatRun(unittest.TestCase):
    def setUp(self):
        self.characters_dict = ingest_creatures_from_excel(sample_data_path/'character_info.xlsx')
        self.heroes = self.characters_dict['heroes']
        self.monsters = self.characters_dict['monsters']

    def test_initialize_combat(self):
        heroes, monsters, initiative_dict, monsters_hp, heroes_hp, rounds = initialize_combat(self.characters_dict)

        # Test that all creatures are at full health
        for creature in heroes + monsters:
            self.assertEqual(creature.hp, creature.max_hp)

        # Test that initiative is calculated correctly
        initiative_values = list(initiative_dict.values())
        self.assertEqual(len(initiative_dict), len(heroes) + len(monsters))  # Check that all creatures are included
        for creature, initiative in initiative_dict.items():
            self.assertIn(creature.initiative, range(creature.initiative_bonus, 20+creature.initiative_bonus+1))  # Check that initiative is in range

        # Test that initiative is sorted correctly
        self.assertEqual(initiative_values, sorted(initiative_values, reverse=True))

        # Test that monsters_hp and heroes_hp are calculated correctly
        self.assertEqual(monsters_hp, calculate_group_hp(monsters))
        self.assertEqual(heroes_hp, calculate_group_hp(heroes))

        # Test that rounds is initialized to 0
        self.assertEqual(rounds, 0)

    def test_run_one_combat(self):

        # Test that combat ends when all monsters are dead
        self.monsters[0].max_hp = 0
        self.monsters[1].max_hp = 0
        self.monsters[2].max_hp = 0
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertEqual(combat_stats[0], 0)
        self.assertEqual(combat_stats[2], 0)

        # Test that combat ends when all heroes are dead
        self.monsters[0].max_hp = 12
        self.monsters[1].max_hp = 12
        self.monsters[2].max_hp = 8
        self.heroes[0].max_hp = 0
        self.heroes[1].max_hp = 0
        self.heroes[2].max_hp = 0
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertEqual(combat_stats[0], 0)
        self.assertEqual(combat_stats[1], 0)

        # Test that first hero to die and first monster to die is recorded
        self.heroes[0].max_hp = 100
        self.heroes[1].max_hp = 100
        self.heroes[2].max_hp = 0
        self.monsters[0].max_hp = 100
        self.monsters[1].max_hp = 100
        self.monsters[2].max_hp = 0
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertEqual(self.heroes[2].name, combat_stats[3])
        self.assertEqual(self.monsters[2].name, combat_stats[4])
        self.heroes[0].max_hp = 12
        self.heroes[1].max_hp = 10
        self.heroes[2].max_hp = 8
        self.monsters[0].max_hp = 12
        self.monsters[1].max_hp = 12
        self.monsters[2].max_hp = 8

        # Test that combat ends if all heroes are dead，or all monsters are dead
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertTrue(combat_stats[1] == 0 or combat_stats[2] == 0)

        # Test that it's not possible for everyone to die 
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertFalse(combat_stats[1] == 0 and combat_stats[2] == 0)

        # Test that combat ends after 1000 rounds
        column_names, combat_stats = run_one_combat(self.characters_dict)
        self.assertLess(combat_stats[0], 1000)

        # Test that number of rounds is recorded
        self.assertGreater(combat_stats[0], 0)

        # Test that column names are correct
        self.assertEqual(column_names, ["rounds", "heroes_hp", "monsters_hp", "first_hero_to_die", "first_monster_to_die", "Barbarian_hp", "Fighter_hp", "Cleric_hp", "Goblin_hp", "Goblin_hp", "Goblin shaman_hp"])
        # Test that column names and combat stats are the same length
        self.assertEqual(len(column_names), len(combat_stats))


    def test_monte_carlo(self):
        combats_df = monte_carlo(self.characters_dict)
        # Test basics
        self.assertIsInstance(combats_df, pd.DataFrame)
        self.assertEqual(len(combats_df), monte_carlo_iterations)
        self.assertEqual(set(combats_df.columns), set(['rounds', 'heroes_hp', 'monsters_hp', 'first_hero_to_die', 'first_monster_to_die', 'Barbarian_hp', 'Fighter_hp', 'Cleric_hp', 'Goblin_hp', 'Goblin_hp', 'Goblin shaman_hp']))
        

class TestDataAnalysis(unittest.TestCase):
    def setUp(self):
        self.characters_dict = ingest_creatures_from_excel(sample_data_path/'character_info.xlsx')
        self.combats_df = monte_carlo(self.characters_dict)

    def test_data_analysis(self):
        # Test that the function returns a DataFrame
        result = data_analysis(self.characters_dict, self.combats_df)
        self.assertIsInstance(result, pd.DataFrame)

        # Test that the DataFrame has the expected columns
        expected_columns = ['rounds', 'heroes_hp', 'monsters_hp', 'first_hero_to_die', 'first_monster_to_die', 'Barbarian_hp', 'Fighter_hp', 'Cleric_hp', 'Goblin_hp', 'Goblin_hp', 'Goblin shaman_hp', 'At least one hero died', 'TPK']
        self.assertEqual(set(result.columns), set(expected_columns))

        # Test that the "At least one hero died" column is calculated correctly
        self.combats_df['Barbarian_hp'].iloc[0] = 0
        result = data_analysis(self.characters_dict, self.combats_df)
        self.assertEqual(result['At least one hero died'].iloc[0], True)

        # Test that the "TPK" column is calculated correctly
        self.combats_df['heroes_hp'].iloc[0] = 0
        result = data_analysis(self.characters_dict, self.combats_df)
        self.assertEqual(result['TPK'].iloc[0], True)

        # Test that the "TPK" column is calculated correctly
        self.combats_df['heroes_hp'].iloc[1] = 10
        result = data_analysis(self.characters_dict, self.combats_df)
        self.assertEqual(result['TPK'].iloc[1], False)

        # # Test that the DataFrame is saved to a CSV file
        # expected_file_path = output_data_path/"combats_df.csv"
        # self.assertTrue(expected_file_path.exists())

if __name__ == '__main__':
    unittest.main()
