from __future__ import annotations

from pathlib import Path


class PathCreatorMixin:
    """Mixin that allows a class to output files to a folder (a validated Path object)."""
    def __init__(
            self,
            folder: str,
            *args,
            **kwargs,
    ) -> None:
        """Initializes a PathCreatorMixin instance."""
        self.path = self.create_path(folder=folder)
        super().__init__(*args, **kwargs)

    @staticmethod
    def create_path(folder: str) -> Path:
        """Creates the output folder and returns it as a Path object."""
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_empty(self) -> bool:
        """Returns whether the output folder is empty or not."""
        return not any(self.path.iterdir())

    def delete_if_empty(self) -> None:
        """Deleted the folder if it is empty."""
        if self.is_empty:
            self.path.rmdir()
