# Script that contains useful functions
import random


def calculate_attack_damage(to_attack: int, attack_damage: str) -> int:
    """Function to calculate attack damage based on string of format e.g. 2d6+3"""
    damages = attack_damage.replace('d', '+').split('+')
    damage = calculate_spell_damage(attack_damage)
    # Critical hit
    if to_attack == 20 and len(damages) > 1:
        damage = damage + random.randint(1, int(damages[1]))

    return damage


def calculate_spell_damage(attack_damage: str) -> int:
    """Function to calculate spell damage based on string of format e.g. 2d6+3"""
    damages = attack_damage.replace('d', '+').split('+')
    damage = 0
    if len(damages) == 1:
        damage = int(damages[0])
    else:
        for i in range(0, int(damages[0])):
            damage = damage + random.randint(1, int(damages[1]))
        if len(damages) == 3:
            damage = damage + int(damages[2])

    return damage


def calculate_group_hp(creatures: list) -> int:
    """Function to total hp of a group of creatures"""
    creatures_hp = 0
    for creature in creatures:
        creatures_hp = creatures_hp + creature.hp

    return creatures_hp
