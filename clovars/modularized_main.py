from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Any, Type

import toml

from clovars import ROOT_PATH

SETTINGS = {
    'actors_path': ROOT_PATH / 'clovars' / 'default_actors',
    'run_file_name': 'default_run.toml'
}

numeric = (int, float)


@dataclass
class Validator:
    """Class representing a parameter that can be validated."""
    valid_types: Type | tuple[Type, ...]
    required: bool
    default_value: Any

    def validate(
            self,
            name: str,
            value: str,
    ) -> None:
        """Validates the given value."""
        if not isinstance(value, self.valid_types):
            if self.required:
                raise ValueError(f'Required value "{name}" is of wrong type {type(value)}, not {self.valid_types}')


@dataclass
class TomlLoader:
    """Class representing a generic TOML file loader."""
    validation_dict: ClassVar[dict] = {}
    loading_dict: ClassVar[dict] = {}
    toml_path: Path

    def __post_init__(self) -> None:
        """Loads and validates the TOML in the given Path."""
        self.data = toml.load(self.toml_path)
        self.validate()
        self.load_structure()

    @property
    def toml_folder(self) -> Path:
        """Returns the Path to the TOML file's containing folder."""
        return self.toml_path.parent

    def validate(self) -> None:
        """Validates the loaded TOML file, as indicated by the validation dict."""
        for key, value in self.data.items():
            if key in self.validation_dict:
                validator = self.validation_dict[key]
                validator.validate(name=key, value=value)

    def load_structure(self) -> None:
        """Loads the child TomlLoader instances, as indicated by the loading dict."""
        for key, value in self.loading_dict.items():
            data = self.data[key]
            if isinstance(data, dict):
                for k, v in data.items():
                    self.load_value(key=k, value=v)
            elif isinstance(data, str):
                toml_file_name = f"{data}.toml"
                loader_path = self.toml_folder / toml_file_name
                loader = value(toml_path=loader_path)
                replaced_data = loader.data
            else:
                raise TypeError(f'Unexpected type: {type(data)}')
            self.data[key] = replaced_data

    def load_value(
            self,
            key: str,
            value: Any,
    ) -> Any:
        """Docstring."""
        if isinstance(value, dict):
            d = {}
            for k, v in value.items():
                d[k] = self.load_value(key=k, value=v)
            return d
        else:

            loader_path = self.toml_folder / toml_file_name
            loader = value(toml_path=loader_path)
            d = loader.data
        return d

@dataclass
class TreatmentRegimenTomlLoader(TomlLoader):
    """Class representing the treatment_regimen.toml loader."""
    loading_dict: ClassVar[dict] = {
    }


@dataclass
class WellTomlLoader(TomlLoader):
    """Class representing the well.toml loader."""
    validation_dict: ClassVar[dict] = {
        'radius': Validator(valid_types=numeric, required=True, default_value=13351.624),
    }
    loading_dict: ClassVar[dict] = {
        'treatment_regimen': TreatmentRegimenTomlLoader,
    }


@dataclass
class RunTomlLoader(TomlLoader):
    """Class representing the run.toml loader."""
    validation_dict: ClassVar[dict] = {
        'verbose': Validator(valid_types=bool, required=False, default_value=False),
        'delta': Validator(valid_types=numeric, required=True, default_value=3600),
    }
    loading_dict: ClassVar[dict] = {
        'well': WellTomlLoader,
    }


def main(
        actors_path: Path,
        run_file_name: str,
) -> None:
    """Main function of this script."""
    run_file_path = actors_path / run_file_name
    loader = RunTomlLoader(toml_path=run_file_path)
    print(loader)
    print(loader.data)


if __name__ == '__main__':
    main(
        actors_path=SETTINGS['actors_path'],
        run_file_name=SETTINGS['run_file_name'],
    )
