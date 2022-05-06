from __future__ import annotations

import json
from pathlib import Path

from PySide6 import QtWidgets as qtw

from clovars import ROOT_PATH


class FileHandler:
    """Class responsible for loading/saving Treatment and Colony presets."""
    project_root_path: Path = ROOT_PATH
    treatment_path: Path = project_root_path / 'presets' / 'treatment'
    colony_path: Path = project_root_path / 'presets' / 'colony'
    presets = {
        'Treatment': treatment_path,
        'Colony': colony_path,
    }

    def __init__(
            self,
            parent: qtw.QWidget = None
    ) -> None:
        """Initializes a FileHandler instance."""
        self.parent = parent
        for path in self.presets.values():
            path.mkdir(parents=True, exist_ok=True)

    @property
    def colony_names(self) -> list[str]:
        """Returns a list of names for all existing colonies."""
        return [p.stem for p in self.colony_path.iterdir()]

    def write_colony(
            self,
            colony_dict: dict,
    ) -> None:
        """Writes the colony data to a json file."""
        self.write(data=colony_dict, preset_name='Colony')

    def load_colony(self) -> dict | None:
        """Returns the colony data from a json file."""
        return self.load(preset_name='Colony')

    @property
    def treatment_names(self) -> list[str]:
        """Returns a list of names for all existing treatments."""
        return [p.stem for p in self.treatment_path.iterdir()]

    def write_treatment(
            self,
            treatment_dict: dict,
    ) -> None:
        """Writes the treatment data to a json file."""
        self.write(data=treatment_dict, preset_name='Treatment')

    def load_treatment(
            self,
    ) -> dict | None:
        """Returns the treatment data from a json file."""
        return self.load(preset_name='Treatment')

    def write(
            self,
            data: dict,
            preset_name: str,
    ) -> None:
        """Writes the data to a json file."""
        base_path = self.presets[preset_name]
        name = data['name']
        path = base_path / (name + '.json')
        if path.exists():
            if self.prompt_overwrite(name=name, preset_name=preset_name) is False:
                return
        self.write_json(path=path, data=data)
        self.display_write_confirmation(name=name, preset_type='Treatment')

    def prompt_overwrite(
            self,
            name: str,
            preset_name: str,
    ) -> bool:
        """Prompts the user to confirm or decline ovewriting an existing file."""
        answer = qtw.QMessageBox.question(  # does not work with keyword arguments!
            self.parent,
            f'Overwrite {preset_name}',
            f'{preset_name} "{name}" already exists - do you want to overwrite it?',
        )
        return answer == qtw.QMessageBox.Yes

    @staticmethod
    def write_json(
            path: Path,
            data: dict,
    ) -> None:
        """Writes the data to a json file."""
        with open(path, 'w') as json_file:
            json_file.write(json.dumps(data, indent=4))

    def display_write_confirmation(
            self,
            name: str,
            preset_type: str,
    ) -> None:
        """Displays a confirmation dialog after writing."""
        qtw.QMessageBox.information(  # does not work with keyword arguments!
            self.parent,
            f'{preset_type} saved!',
            f'{preset_type} "{name}" was successfully saved.',
        )

    def load(
            self,
            preset_name: str,
    ) -> dict | None:
        """Returns the data from a json file."""
        base_path = self.presets[preset_name]
        names = {
            'Colony': self.colony_names,
            'Treatment': self.treatment_names,
        }[preset_name]
        if (name := self.prompt_load(names=names, preset_type='Colony')) is None:
            return None
        path = base_path / (name + '.json')
        # if not path.exists():
        #     raise OSError(f'Path {str(path)} should exist, but does not!')
        return self.load_json(path=path)

    def prompt_load(
            self,
            names: list[str],
            preset_type: str,
    ) -> str | None:
        """Prompts the user to select a data to load."""
        if not names:
            qtw.QMessageBox.information(
                self.parent,
                f'Load {preset_type}',
                f'No {preset_type} to load - please save a {preset_type} first!')
            return None
        else:
            name, confirm = qtw.QInputDialog.getItem(
                self.parent,
                f'Load {preset_type}',
                f'Choose a {preset_type}:',
                names,
                0,
                editable=False,
            )
            if confirm is True:
                return name
            else:
                return None

    @staticmethod
    def load_json(
            path: Path,
    ) -> dict:
        """Loads the data from a json file."""
        with open(path, 'r') as json_file:
            content = json_file.read()
        return json.loads(content)
