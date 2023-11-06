# File with all configurations
import os
from pathlib import Path

monte_carlo_iterations = 1000

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = ROOT_DIR / 'data//upload_xlsx_here/'