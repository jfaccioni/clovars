from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from clovars.bio import Treatment, get_treatment


class SimulationLoader:
    """Class that loads data from a complete Simulation run."""
    default_simulation_input_folder = '.'
    default_cell_csv_file_name = 'cell_output.csv'
    default_colony_csv_file_name = 'colony_output.csv'
    default_parameters_file_name = 'params.json'

    def __init__(
            self,
            settings: dict[str, Any] | None = None,
    ) -> None:
        """Initializes a SimulationLoader instance."""
        self._cell_data = self._colony_data = self._params = self._treatments = None
        if settings is None:
            settings = {}
        self.input_folder = Path(settings.get('simulation_input_folder', self.default_simulation_input_folder))
        self.cell_data_path = Path(
            self.input_folder,
            settings.get('cell_csv_file_name', self.default_cell_csv_file_name)
        )
        self.colony_data_path = Path(
            self.input_folder,
            settings.get('colony_csv_file_name', self.default_colony_csv_file_name),
        )
        self.params_path = Path(
            self.input_folder,
            settings.get('parameters_file_name', self.default_parameters_file_name)
        )

    @property
    def cell_data(self) -> pd.DataFrame:
        """Returns the Cell DataFrame, loading it beforehand if it hasn't been done yet."""
        if self._cell_data is None:
            self._cell_data = self.load_cell_data()
        return self._cell_data

    def load_cell_data(self) -> pd.DataFrame:
        """Parses and returns the DataFrame containing the Cell data."""
        data = pd.read_csv(self.cell_data_path, index_col=None)
        data['colony_name'] = data['colony_name'].astype(str)
        return data

    @property
    def colony_data(self) -> pd.DataFrame:
        """Returns the Colony DataFrame, loading it beforehand if it hasn't been done yet."""
        if self._colony_data is None:
            self._colony_data = self.load_colony_data()
        return self._colony_data

    def load_colony_data(self) -> pd.DataFrame:
        """Parses and returns the DataFrame containing the Colony data."""
        data = pd.read_csv(self.colony_data_path, index_col=None)
        data['name'] = data['name'].astype(str)
        return data

    @property
    def params(self) -> dict[str, Any]:
        """Returns the Params dictionary, loading it beforehand if it hasn't been done yet."""
        if self._params is None:
            self._params = self.load_params()
        return self._params

    def load_params(self) -> dict:
        """Returns the contents of the JSON parameters file."""
        with open(self.params_path, "r") as file:
            return json.loads(file.read())

    @property
    def delta(self) -> int:
        """Returns the Simulation delta loaded from the Simulation parameters."""
        return self.params['simulation_runner_settings']['delta']

    @property
    def treatments(self) -> dict[tuple[str, int], Treatment]:
        """Returns a list of the Treatments applied for each Colony, loaded from the Simulation parameters."""
        if self._treatments is None:
            self._treatments = self.load_treatments()
        return self._treatments

    def load_treatments(self) -> dict[tuple[str, int], Treatment]:
        """
        Parses the information in the list of Treatments into a dictionary containing the Colony name,
        the Treatment and the frame in which it was added.
        """
        treatment_data = {}
        treatment_params = [colony_data['treatment_data'] for colony_data in self.params['colony_data']]
        colony_names = self.cell_data['colony_name'].str.extract(r'(\d)')[0].unique()
        for treatment, colony_name in zip(treatment_params, colony_names):
            for treatment_frame, treatment_parameters in treatment.items():
                key = (colony_name, int(treatment_frame))
                value = get_treatment(**treatment_parameters)
                treatment_data[key] = value
        return treatment_data

    @property
    def well_radius(self) -> float:
        """Returns the Well radius loaded from the Simulation parameters."""
        return self.params['well_settings']['well_radius']
