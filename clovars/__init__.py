import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
COLONY_DATA_PATH = os.path.join(ROOT_PATH, 'colonies.toml')
RUN_SETTINGS_PATH = os.path.join(ROOT_PATH, 'run_settings.toml')
ANALYSE_SETTINGS_PATH = os.path.join(ROOT_PATH, 'view_settings.toml')
VIEW_SETTINGS_PATH = os.path.join(ROOT_PATH, 'analyse_settings.toml')
