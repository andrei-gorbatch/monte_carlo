# Script that contains class definitions for all characters
import random

from utils import calculate_attack_damage, calculate_spell_damage, calculate_group_hp


class character:
    # Parent class that is shared between all characters
    def __init__(self, name, hp, ac, initiative_bonus, saves, healer, heal_amount):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.ac = ac
        self.saves = saves
        self.initiative_bonus = initiative_bonus
        self.initiative = initiative_bonus
        self.healer = healer
        self.heal_amount = heal_amount

    def take_attack_damage(self, attack_roll):
        """Function to take damage from an attack"""
        to_attack, damage = attack_roll
        if to_attack >= self.ac:
            self.hp = max(self.hp - damage, 0)

    def take_heal(self, heal):
        """function to take healing"""
        self.hp = min(self.hp + heal, self.max_hp)

    def take_saving_throw_damage(self, spell_attack):
        """function to take damage from spell attack that requires a saving throw"""
        targeted_save, spell_save_dc, saved_damage, damage = spell_attack
        save = random.randint(1, 20) + self.saves[targeted_save]
        if spell_save_dc > save:
            self.hp = max(self.hp - damage, 0)
        else:
            self.hp = max(self.hp - int(damage*saved_damage), 0)

    def take_damage_or_status(self, attack_info):
        """Wrapper function that determines which function to apply based on attack information"""
        attack_type, attack = attack_info
        if attack_type == "roll_to_attack":
            self.take_attack_damage(attack)
        elif attack_type == "spell_attack":
            self.take_saving_throw_damage(attack)
        elif attack_type == "heal":
            self.take_heal(attack)

    def heal(self):
        """Function to roll healing """
        heal = calculate_spell_damage(self.heal_amount)
        return heal


class martial(character):
    # Child class for martial characters
    def __init__(self, name, hp, ac, attack_bonus, attack_damage, number_of_attacks, initiative_bonus, saves, healer, heal_amount):
        super().__init__(name, hp, ac, initiative_bonus, saves, healer, heal_amount)
        self.attack_bonus = int(attack_bonus)
        self.attack_damage = attack_damage
        self.number_of_attacks = int(number_of_attacks)

    def roll_to_attack(self):
        """Function to roll to attack and damage"""
        to_attack = random.randint(1, 20) + self.attack_bonus
        damage = calculate_attack_damage(to_attack, self.attack_damage)
        return tuple([to_attack, damage])

    def best_action(self, target_type):
        """Wrapper function that determines which action to take based on target"""
        if target_type == "ally":
            return tuple(["heal", self.heal()])
        else:
            return tuple(["roll_to_attack", self.roll_to_attack()])


class blaster(character):
    # Child class for AOE blaster characters
    def __init__(self, name, hp, ac, spell_save_dc, attack_damage, saved_damage, number_of_targets, initiative_bonus, saves, healer, heal_amount, targeted_save):
        super().__init__(name, hp, ac, initiative_bonus, saves, healer, heal_amount)
        self.spell_save_dc = int(spell_save_dc)
        self.attack_damage = attack_damage
        self.saved_damage = saved_damage
        self.number_of_targets = int(number_of_targets)
        self.targeted_save = targeted_save

    def spell_attack(self):
        """Function that outputs required information for an AOE spell attack"""
        damage = calculate_spell_damage(self.attack_damage)
        return tuple([self.targeted_save, self.spell_save_dc, self.saved_damage, damage])

    def best_action(self, target_type):
        """Wrapper function that determines which action to take based on target"""
        if target_type == "ally":
            return tuple(["heal", self.heal()])
        else:
            return tuple(["spell_attack", self.spell_attack()])
