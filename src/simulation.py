# Script that runs Monte-Carlo simulation of the combat

import logging
import pandas as pd
import numpy as np
import random

from classes import martial, blaster
from utils import calculate_attack_damage, calculate_spell_damage, calculate_group_hp
from config import monte_carlo_iterations, heroes, monsters

def choose_heal_or_attack_target(character, heroes, monsters):
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
    # If heal is False or no allies are at 0hp, choose attack target
    if len(potential_targets)==0:
        for creature in enemies:
            if creature.hp>0:
                potential_targets.append(creature)
                target_type = "enemy"

    # Randomly sellect target among potential targets
    if len(potential_targets)!=0:
        target = random.choice(potential_targets)
    else:
        target_type = None
        target = None

    return target_type, target


def initialize_combat():
    # Function to reset the combat
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

    return heroes, monsters, all_creatures, initiative_dict, monsters_hp, heroes_hp, rounds


def run_one_combat():
    # Function to run one combat

    heroes, monsters, all_creatures, initiative_dict, monsters_hp, heroes_hp, rounds = initialize_combat()

    while (monsters_hp>0 and heroes_hp>0):
        rounds=rounds+1
        for character, _ in initiative_dict.items():
            if character.hp>0:
                if character in heroes:
                    target_type, target = choose_heal_or_attack_target(character, heroes, monsters)
                    if target == None:
                        break
                    target.take_damage_or_status(character.best_action(target_type))
                else:
                    target_type, target = choose_heal_or_attack_target(character, heroes, monsters)
                    if target == None:
                        break
                    target.take_damage_or_status(character.best_action(target_type))
        monsters_hp = calculate_group_hp(monsters)
        heroes_hp = calculate_group_hp(heroes)

    return rounds, heroes_hp, monsters_hp


def monte_carlo() -> pd.DataFrame:
    # Run combat for number of iterations defined in config and save results in a df for futher analysis
    data = []
    for i in range(0, monte_carlo_iterations):
        rounds, heroes_hp, monsters_hp = run_one_combat()
        data.append([rounds, heroes_hp, monsters_hp])
    combats_df = pd.DataFrame(columns=['rounds','heroes_hp', 'monsters_hp'], data = data)
    combats_df['TPK'] = np.where((combats_df['heroes_hp']==0), True, False)

    return combats_df

def main():
    combats_df = monte_carlo()
    print(f"Ran {monte_carlo_iterations} combats, {combats_df['TPK'].sum()} of them are TPK!")

if __name__ == "__main__":
    main()

