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

    def load_structure(
            self,
            d: dict | None = None,
    ) -> None:
        """Loads the child TomlLoader instances, as indicated by the loading dict."""
        d = d or self.data
        for key, value in d.items():
            if self.is_toml_path(value=value):  # Load structure from another toml file
                toml_path = self.toml_folder / value
                d[key] = self.loading_dict[key](toml_path=toml_path).data
            elif self.is_dict(value=value):  # Recursively get structure from dict
                self.load_structure(d=value)
            else:  # Take the value as it is
                d[key] = value

    @staticmethod
    def is_dict(value: Any) -> bool:
        """Returns True if the given value is a dictionary."""
        return isinstance(value, dict)

    def is_toml_path(
            self,
            value: Any,
    ) -> bool:
        """Returns True if the given value corresponds to an existing toml file in the filesystem."""
        try:
            path = self.toml_folder / value
        except TypeError:  # Value cannot be converted to Path
            return False
        if path.is_file() and path.exists() and path.suffix.lower() == '.toml':
            return True
        return False


class ConstantDict(dict):
    def __init__(
            self,
            constant: Any,
            *args,
            **kwargs,
    ) -> None:
        """Initializes a ConstantDict."""
        self._constant = constant
        super().__init__(*args, **kwargs)

    def __missing__(
            self,
            key: Any,
    ) -> Any:
        """Returns the constant value whenever a missing key is accessed, and sets the key's value to the constant."""
        self[key] = self._constant
        return self._constant


@dataclass
class TreatmentRegimenTomlLoader(TomlLoader):
    """Class representing the treatment_regimen.toml loader."""
    loading_dict: ClassVar[ConstantDict] = None


TreatmentRegimenTomlLoader.loading_dict = ConstantDict(TreatmentRegimenTomlLoader)


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
    print(loader.data)


if __name__ == '__main__':
    main(
        actors_path=SETTINGS['actors_path'],
        run_file_name=SETTINGS['run_file_name'],
    )
