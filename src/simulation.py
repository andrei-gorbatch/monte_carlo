# Script that runs Monte-Carlo simulation of the combat

import logging
import pandas as pd
import numpy as np
import random

from classes import martial, blaster
from utils import calculate_attack_damage, calculate_spell_damage, calculate_group_hp
from config import monte_carlo_iterations, data_path

def ingest_creatures_from_excel():
    # Function to ingest heroes and monsters information from excel spreadsheet
    input_file = data_path/'character_info.xlsx'
    heroes_df = pd.read_excel(input_file, sheet_name="Heroes")
    heroes_df.name = 'heroes'
    monsters_df = pd.read_excel(input_file, sheet_name="Monsters")
    monsters_df.name = 'monsters'

    dfs = [heroes_df, monsters_df]
    characters_dict=dict()
    for df in dfs:
        characters = []
        for index, row in df.iterrows():
            saves = {"str": row['str_save'], "dex": row['dex_save'], "con": row['con_save'], "wis": row['wis_save'], "cha": row['cha_save'], "int": row['int_save']}
            if row['Type']=="Martial":
                #TODO: add error handling for missing values, wrong formats, etc.
                characters.append(martial(name=row['Name'], hp=row['HP'], ac=row['AC'], saves=saves, initiative_bonus=row['initiative_bonus'],
                                    healer = row['healer'], heal_amount=row['heal_amount'],
                                    number_of_attacks=row['number_of_attacks'], attack_bonus=row['attack_bonus'], attack_damage=row['attack_damage']))
            elif row['Type']=="Blaster":
                characters.append(blaster(name=row['Name'], hp=row['HP'], ac=row['AC'], saves=saves, initiative_bonus=row['initiative_bonus'],
                                    healer = row['healer'], heal_amount=row['heal_amount'],
                                    number_of_targets=row['number_of_targets'], spell_save_dc=row['spell_save_dc'],
                                    targeted_save=row['targeted_save'], attack_damage=row['attack_damage']))
            else:
                print(f"row {index} contains unknown type {row['Type']}, please check.")

        characters_dict[df.name] = characters

    return characters_dict #['heroes'], characters_dict['monsters']

def choose_attack_target(character, heroes, monsters, number_of_targets=1):
    # Function that selects the target for attack

    potential_targets = []

    # Assign allies/enemies based on character
    if character in heroes:
        allies = heroes
        enemies = monsters
    else:
        allies = monsters
        enemies = heroes

    # Choose attack targets
    for creature in enemies:
        if creature.hp>0:
            potential_targets.append(creature)
            target_type = "enemy"

    # Randomly sellect targets among all potential targets
    if len(potential_targets)!=0:
        # Character.number_of_targets can be hit at the same time
        try:
            targets = random.sample(potential_targets, number_of_targets)
        except ValueError:
            targets = potential_targets
    else:
        target_type = None
        targets = None

    return target_type, targets

def choose_heal_target(character, heroes, monsters):
    # Function that chooses whether to heal an ally or attack an enemy, and selects the target

    potential_targets = []

    # Assign allies/enemies based on character
    if character in heroes:
        allies = heroes
        enemies = monsters
    else:
        allies = monsters
        enemies = heroes

    # If heal is True, check if any of the allies are at 0hp and heal them
    if character.healer == True:
        for creature in allies:
            if creature.hp==0:
                potential_targets.append(creature)
                target_type = "ally"
    # Only one target can be healed at a time
    if len(potential_targets)!=0:
        target = random.choice(potential_targets)
    else:
        target_type = None
        target = None

    return target_type, target


def initialize_combat(characters_dict):
    # Function to reset the combat
    heroes = characters_dict['heroes']
    monsters = characters_dict['monsters']
    all_creatures = heroes + monsters

    initiative_dict = dict()
    for creature in all_creatures:
        creature.hp = creature.max_hp
        creature.initiative = random.randint(1, 20) + creature.initiative_bonus
        initiative_dict[creature] = creature.initiative
    initiative_dict = dict(sorted(initiative_dict.items(), key=lambda item: item[1]))

    monsters_hp = calculate_group_hp(monsters)
    heroes_hp = calculate_group_hp(heroes)
    rounds=0

    return heroes, monsters, initiative_dict, monsters_hp, heroes_hp, rounds

def action(character, heroes, monsters):
    # Function that performs one action for the character

    # Heal first if needed
    target_type, target = choose_heal_target(character, heroes, monsters)
    if target != None:
        target.take_damage_or_status(character.best_action(target_type))

    #Then do damage 
    if character.__class__.__name__ == 'martial':
        # For martial, each attack is rolled separately for each target
        for i in range(0, character.number_of_attacks):
            target_type, targets = choose_attack_target(character, heroes, monsters)
            if targets != None:
                for target in targets:
                    target.take_damage_or_status(character.best_action(target_type))
            if target_type != "enemy":
                break
            
    elif character.__class__.__name__ == 'blaster':
        # For blaster, roll damage first and then apply to all targets equally
        target_type, targets = choose_attack_target(character, heroes, monsters, character.number_of_targets)
        if targets != None:
            best_action = character.best_action(target_type)
            for target in targets:
                target.take_damage_or_status(best_action)

def run_one_combat(characters_dict):
    # Function to run one combat

    heroes, monsters, initiative_dict, monsters_hp, heroes_hp, rounds = initialize_combat(characters_dict)

    while (monsters_hp>0 and heroes_hp>0):
        rounds=rounds+1
        for character, _ in initiative_dict.items():
            if character.hp>0:
                action(character, heroes, monsters)
        monsters_hp = calculate_group_hp(monsters)
        heroes_hp = calculate_group_hp(heroes)

    return rounds, heroes_hp, monsters_hp


def monte_carlo(characters_dict) -> pd.DataFrame:
    # Run combat for number of iterations defined in config and save results in a df for futher analysis
    data = []
    for i in range(0, monte_carlo_iterations):
        rounds, heroes_hp, monsters_hp = run_one_combat(characters_dict)
        data.append([rounds, heroes_hp, monsters_hp])
    combats_df = pd.DataFrame(columns=['rounds','heroes_hp', 'monsters_hp'], data = data)
    combats_df['TPK'] = np.where((combats_df['heroes_hp']==0), True, False)

    return combats_df

def main():
    characters_dict = ingest_creatures_from_excel()
    combats_df = monte_carlo(characters_dict)
    print(f"Ran {monte_carlo_iterations} combats, {combats_df['TPK'].sum()} of them are TPK!")

if __name__ == "__main__":
    main()

