import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
DEFAULT_SETTINGS_FOLDER = Path(ROOT_PATH, 'clovars', 'default_settings')
DEFAULT_RUN_PATH = Path(DEFAULT_SETTINGS_FOLDER, 'default_run.toml')
DEFAULT_COLONIES_PATH = Path(DEFAULT_SETTINGS_FOLDER, 'default_colonies.toml')
DEFAULT_VIEW_PATH = Path(DEFAULT_SETTINGS_FOLDER, 'default_view.toml')
DEFAULT_ANALYSIS_PATH = Path(DEFAULT_SETTINGS_FOLDER, 'default_analysis.toml')
DEFAULT_FIT_PATH = Path(DEFAULT_SETTINGS_FOLDER, 'default_fit.toml')
