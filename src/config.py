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
