from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

from clovars.main import main as clovars_main

RANDOMNESS_SEED = 64


def main() -> None:
    """Main function of this script."""
    random.seed(RANDOMNESS_SEED)
    np.random.seed(RANDOMNESS_SEED)
    for treatment_name in ['control', 'tmz']:
        sys.argv = ['', 'run', 'Fig_S2B_run.toml', f'Fig_S2B_colonies_{treatment_name}.toml']
        clovars_main()
        sys.argv = ['', 'view', 'Fig_S2B_view.toml']
        clovars_main()
        remove_tree(path=Path('output'))


def remove_tree(path: Path) -> None:
    """Recursively deletes files and folders starting from path."""
    # Source: https://stackoverflow.com/a/57892171/11161432
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            remove_tree(child)
    path.rmdir()


if __name__ == '__main__':
    main()
