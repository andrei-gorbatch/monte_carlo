# Script that runs Monte-Carlo simulation of the combat

import random
from typing import Tuple
import pandas as pd
import numpy as np
import re
from pathlib import Path
import os
import sys

from classes import martial, blaster
from utils import calculate_group_hp
from config import monte_carlo_iterations, input_data_path, output_data_path, expected_columns, int_columns, must_have_cols, dice_columns, possible_saves, martial_columns, blaster_columns

def validate_dice_cols(col):
    """Function to validate that the dice columns are in the correct format"""
    if not col.apply(lambda x: (re.match(r'^[\d\+]*d[\d\+]*(\+[\d\+]*d[\d\+]*)*$', str(x))) is not None or pd.isna(x)).all():
       raise ValueError(f"Invalid damage: {col}")

def validate_excel_file(input_file: Path = input_data_path/'character_info.xlsx') -> None:
    """Function to test whether the excel file is in the correct format"""

    if not os.path.exists(input_file):
        raise ValueError("Input file is missing or incorrectly named.")

    try:
        heroes_df = pd.read_excel(input_file, sheet_name="Heroes")
    except:
        raise ValueError("Heroes sheet is missing or incorrectly named.")

    try:
        monsters_df = pd.read_excel(input_file, sheet_name="Monsters")
    except:
        raise ValueError("Monsters sheet is missing or incorrectly named.")

    all_characters = pd.concat([heroes_df, monsters_df], ignore_index=True)

    if not (all_characters.columns == expected_columns).all():
        raise ValueError("Columns are missing or incorrectly named.")

    if not (all_characters['Type'].isin(['Martial', 'Blaster'])).all():
        raise ValueError("Type column contains unknown values.")

    try:
        all_characters['healer'].isin([True, False])
    except:
        raise ValueError("healer column contains unknown values.")

    try:
        all_characters[int_columns].fillna(-1).astype(int)
    except:
        raise ValueError("Integer columns contain unknown values.")

    try:
        all_characters[dice_columns].apply(validate_dice_cols)
    except:
        raise ValueError("heal_amount or attack_damage column contains unknown values.")

    if not (all_characters['targeted_save'].isin(possible_saves) | all_characters['targeted_save'].isna()).all():
        raise ValueError("targeted_save column contains unknown values.")

    if not (all_characters['saved_damage'].isin([0, 0.5, 1]) | all_characters['saved_damage'].isna()).all():
        raise ValueError("saved_damage column contains unknown values.")

    # Check that Martial characters have number_of_attacks and attack_bonus
    martial_characters = all_characters[all_characters['Type'] == 'Martial']
    if not martial_characters[martial_columns].notna().all().all():
        raise ValueError("Martial characters are missing number_of_attacks or attack_bonus.")
    
    # Check that Blaster characters have number_of_targets, spell_save_dc, targeted_save, saved_damage
    blaster_characters = all_characters[all_characters['Type'] == 'Blaster']
    if not blaster_characters[blaster_columns].notna().all().all():
        raise ValueError("Blaster characters are missing number_of_targets, spell_save_dc, targeted_save, or saved_damage.")

    # Check that Healers have heal_amount
    healer_characters = all_characters[all_characters['healer'] == True]
    if not healer_characters['heal_amount'].notna().all():
        raise ValueError("Healers are missing heal_amount.")

    # Check that all characters have necessary information
    if not all_characters[must_have_cols].notna().all().all():
        raise ValueError("Some characters are missing necessary information.")


def ingest_creatures_from_excel(input_file: Path = input_data_path/'character_info.xlsx') -> dict:
    """Function to ingest heroes and monsters information from excel spreadsheet"""

    heroes_df = pd.read_excel(input_file, sheet_name="Heroes")
    heroes_df.name = 'heroes'
    monsters_df = pd.read_excel(input_file, sheet_name="Monsters")
    monsters_df.name = 'monsters'

    dfs = [heroes_df, monsters_df]
    characters_dict = dict()
    for df in dfs:
        characters = []
        for index, row in df.iterrows():
            saves = {"str": row['str_save'], "dex": row['dex_save'], "con": row['con_save'],
                     "wis": row['wis_save'], "cha": row['cha_save'], "int": row['int_save']}
            if row['Type'] == "Martial":
                # TODO: add error handling for missing values, wrong formats, etc.
                characters.append(martial(name=row['Name'], hp=row['HP'], ac=row['AC'], saves=saves, initiative_bonus=row['initiative_bonus'],
                                          healer=row['healer'], heal_amount=row['heal_amount'],
                                          number_of_attacks=row['number_of_attacks'], attack_bonus=row['attack_bonus'], attack_damage=row['attack_damage']))
            elif row['Type'] == "Blaster":
                characters.append(blaster(name=row['Name'], hp=row['HP'], ac=row['AC'], saves=saves, initiative_bonus=row['initiative_bonus'],
                                          healer=row['healer'], heal_amount=row['heal_amount'],
                                          number_of_targets=row['number_of_targets'], spell_save_dc=row['spell_save_dc'],
                                          targeted_save=row['targeted_save'], saved_damage=row['saved_damage'], 
                                          attack_damage=row['attack_damage']))
            else:
                print(
                    f"row {index} contains unknown type {row['Type']}, please check.")

        characters_dict[df.name] = characters

    return characters_dict


def choose_attack_target(character: any, heroes: list, monsters: list, number_of_targets: int = 1) -> Tuple[str, list]:
    """Function that selects the target for attack"""

    potential_targets = []
    target_type = "enemy"

    # Assign allies/enemies based on character
    if character in heroes:
        enemies = monsters
    else:
        enemies = heroes

    # Choose attack targets
    for creature in enemies:
        if creature.hp > 0:
            potential_targets.append(creature)

    # Randomly sellect targets among all potential targets
    if len(potential_targets) != 0:
        # Character.number_of_targets can be hit at the same time
        try:
            targets = random.sample(potential_targets, number_of_targets)
        except ValueError:
            targets = potential_targets
    else:
        targets = None

    return target_type, targets


def choose_heal_target(character: any, heroes: list, monsters: list) -> Tuple[str, any]:
    """ Function that chooses whether to heal an ally or attack an enemy, and selects the target"""

    potential_targets = []
    target_type = "ally"

    # Assign allies/enemies based on character
    if character in heroes:
        allies = heroes
    else:
        allies = monsters

    # If heal is True, check if any of the allies are at 0hp and heal them
    if character.healer is True:
        for creature in allies:
            if creature.hp == 0:
                potential_targets.append(creature)
    # Only one target can be healed at a time
    if len(potential_targets) != 0:
        target = random.choice(potential_targets)
    else:
        target = None

    return target_type, target


def initialize_combat(characters_dict: dict) -> Tuple[list, list, dict, int, int, int]:
    """Function to reset the combat"""

    heroes = characters_dict['heroes']
    monsters = characters_dict['monsters']
    all_creatures = heroes + monsters

    initiative_dict = dict()
    for creature in all_creatures:
        creature.hp = creature.max_hp
        creature.initiative = random.randint(1, 20) + creature.initiative_bonus
        initiative_dict[creature] = creature.initiative
    initiative_dict = dict(
        sorted(initiative_dict.items(), key=lambda item: item[1], reverse=True))

    monsters_hp = calculate_group_hp(monsters)
    heroes_hp = calculate_group_hp(heroes)
    rounds = 0

    return heroes, monsters, initiative_dict, monsters_hp, heroes_hp, rounds


def action(character: any, heroes: list, monsters: list) -> None:
    """Function that performs one action for the character"""

    # Heal first if needed
    target_type, target = choose_heal_target(character, heroes, monsters)
    if target != None:
        target.take_damage_or_status(character.best_action(target_type))

    # Then do damage
    if character.__class__.__name__ == 'martial':
        # For martial, each attack is rolled separately for each target
        for i in range(0, character.number_of_attacks):
            target_type, targets = choose_attack_target(
                character, heroes, monsters)
            if targets is not None:
                for target in targets:
                    target.take_damage_or_status(
                        character.best_action(target_type))
            if target_type != "enemy":
                break

    elif character.__class__.__name__ == 'blaster':
        # For blaster, roll damage first and then apply to all targets equally
        target_type, targets = choose_attack_target(
            character, heroes, monsters, character.number_of_targets)
        if targets is not None:
            best_action = character.best_action(target_type)
            for target in targets:
                target.take_damage_or_status(best_action)


def run_one_combat(characters_dict: dict) -> list:
    """Function to run one combat"""

    heroes, monsters, initiative_dict, monsters_hp, heroes_hp, rounds = initialize_combat(
        characters_dict)

    first_hero_to_die = None
    first_monster_to_die = None

    while (monsters_hp > 0 and heroes_hp > 0):
        rounds = rounds + 1
        for character, _ in initiative_dict.items():
            if character.hp > 0:
                action(character, heroes, monsters)
            elif (first_hero_to_die is None) and (character in heroes):
                first_hero_to_die = character.name
            elif (first_monster_to_die is None) and (character in monsters):
                first_monster_to_die = character.name
        monsters_hp = calculate_group_hp(monsters)
        heroes_hp = calculate_group_hp(heroes)

    # Generate the stats file entry
    # Add final health of all creatures
    column_names = ["rounds", "heroes_hp", "monsters_hp",
                    "first_hero_to_die", "first_monster_to_die"]
    combat_stats = [rounds, heroes_hp, monsters_hp,
                    first_hero_to_die, first_monster_to_die]
    all_characters = heroes + monsters
    for character in all_characters:
        column_names.append(f"{character.name}_hp")
        combat_stats.append(character.hp)

    return column_names, combat_stats


def monte_carlo(characters_dict: dict) -> pd.DataFrame:
    """ Run combat for number of iterations defined in config and save results in a df for futher analysis"""
    data = []
    for i in range(0, monte_carlo_iterations):
        column_names, combat_stats = run_one_combat(characters_dict)
        data.append(combat_stats)
    combats_df = pd.DataFrame(columns=column_names, data=data)

    return combats_df


def data_analysis(characters_dict: dict, combats_df: pd.DataFrame) -> pd.DataFrame:
    """ Do data analysis and save results in a csv"""

    heroes = characters_dict['heroes']
    monsters = characters_dict['monsters']

    hero_hp_cols = []
    for hero in heroes:
        hero_hp_cols.append(f"{hero.name}_hp")
    combats_df['At least one hero died'] = np.where(
        (combats_df[hero_hp_cols] == 0).any(axis=1), True, False)

    combats_df['TPK'] = np.where((combats_df['heroes_hp'] == 0), True, False)

    # combats_df.to_csv(output_data_path/"combats_df.csv")

    return combats_df


def main():
    """Main"""
    # Test excel format
    validate_excel_file()
    # Ingest heroes and monsters from excel
    characters_dict = ingest_creatures_from_excel()
    # Run Monte-Carlo simulation
    combats_df = monte_carlo(characters_dict)
    # Do data analysis
    combats_df = data_analysis(characters_dict, combats_df)
    print(
        f"Ran {monte_carlo_iterations} combats.")
    print(f"In {combats_df['TPK'].sum()/monte_carlo_iterations*100:.1f}% cases, all heroes died.")
    print(
        f"In {combats_df['At least one hero died'].sum()/monte_carlo_iterations*100:.1f}% cases, at least one hero died.")

    text = f"Ran {monte_carlo_iterations} combats.\n" + \
    f"In {combats_df['TPK'].sum()/monte_carlo_iterations*100:.1f}% cases, all heroes died.\n" + \
    f"In {combats_df['At least one hero died'].sum()/monte_carlo_iterations*100:.1f}% cases, at least one hero died.\n"

    return text


if __name__ == "__main__":
    main()
