# File with all configurations
import os
from pathlib import Path


def create_data_path(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return path


monte_carlo_iterations = 1000

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_data_path = create_data_path(ROOT_DIR / 'data/upload_xlsx_here/')
output_data_path = create_data_path(ROOT_DIR / 'data/simulation/')

# Config for testing excel file format
expected_columns = ['Type', 'Name', 'HP', 'AC', 'str_save', 'dex_save', 'con_save', 'wis_save', 'cha_save', 'int_save', 'initiative_bonus', 'healer', 'heal_amount', 'number_of_attacks', 'attack_bonus', 'number_of_targets', 'spell_save_dc', 'targeted_save', 'saved_damage', 'attack_damage']
int_columns = ['HP', 'AC', 'str_save', 'dex_save', 'con_save', 'wis_save', 'cha_save', 'int_save', 'initiative_bonus', 'number_of_attacks', 'attack_bonus', 'number_of_targets', 'spell_save_dc']
must_have_cols = ['Type', 'Name', 'HP', 'AC', 'str_save', 'dex_save', 'con_save', 'wis_save', 'cha_save', 'int_save', 'initiative_bonus', 'healer', 'attack_damage']
dice_columns = ['heal_amount', 'attack_damage']
possible_saves = ['str', 'dex', 'con', 'wis', 'cha', 'int']
martial_columns = ['number_of_attacks', 'attack_bonus']
blaster_columns = ['number_of_targets', 'spell_save_dc', 'targeted_save', 'saved_damage']
