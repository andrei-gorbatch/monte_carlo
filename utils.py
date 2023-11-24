# Script that contains useful functions
import random


def dice_damage(number_of_dice: int, dice_value: int, crit: bool = False) -> int:
    """Function to calculate value of several dice thrown, e.g. 3d6"""
    if crit==True:
        number_of_dice = number_of_dice*2

    damage = 0
    for i in range(0, number_of_dice):
        damage = damage + random.randint(1, dice_value)

    return damage


def calculate_attack_damage(attack_damage: str, to_attack: int = 10) -> int:
    """Function to calculate damage based on string of format e.g. 2d6+1d8+3. 
    If to_attack=20, calculate critical damage"""
    
    if to_attack==20:
        crit=True
    else:
        crit=False

    damages_str = attack_damage.lower().split('+')
    damage = 0
    for damage_str in damages_str:
        if 'd' in damage_str:
            dice_values = damage_str.split('d')
            damage = damage + dice_damage(int(dice_values[0]), int(dice_values[1]), crit)
        else:
            damage = damage + int(damage_str)

    return damage


def calculate_group_hp(creatures: list) -> int:
    """Function to total hp of a group of creatures"""
    creatures_hp = 0
    for creature in creatures:
        creatures_hp = creatures_hp + creature.hp

    return creatures_hp
