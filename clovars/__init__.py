import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
COLONY_DATA_PATH = os.path.join(ROOT_PATH, 'settings', 'colonies.toml')
RUN_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'run_settings.toml')
VIEW_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'view_settings.toml')
ANALYSE_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'analyse_settings.toml')
