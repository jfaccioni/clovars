import random
import sys
from pathlib import Path

import numpy as np

from clovars.main import main as clovars_main

RANDOMNESS_SEED = 31


def main():
    """Main function of this script."""
    random.seed(RANDOMNESS_SEED)
    np.random.seed(RANDOMNESS_SEED)
    for scenario in ['i', 'ii', 'iii']:
        sys.argv = ['', 'run', 'Fig_2B_run.toml', f'Fig_2B_colonies_{scenario}.toml']
        clovars_main()
        sys.argv = ['', 'view', 'Fig_2B_view.toml']
        clovars_main()
        remove_tree(path=Path('output'))


def remove_tree(path: Path):
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
