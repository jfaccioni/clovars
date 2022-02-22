import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
RUN_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'run_settings.toml')
COLONIES_PATH = os.path.join(ROOT_PATH, 'settings', 'colonies.toml')
VIEW_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'view_settings.toml')
ANALYSE_SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings', 'analyse_settings.toml')
