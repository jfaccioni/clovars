from __future__ import annotations


def get_dropdown_label_from_index(
        dropdown_index: int,
        dropdown_options: list,
) -> str:
    """Returns the dropdown's label, given its current index and its options."""
    dropdown_label = [x['label'] for x in dropdown_options if x['value'] == dropdown_index]
    return dropdown_label[0]


class IndexString(str):
    """String representing an index-name combination."""
    def __init__(
            self,
            idx: int,
            name: str,
    ) -> None:
        """Initializes an IndexString instance."""
        self._index = self.validate_index(index=idx)
        self._name = self.validate_name(name=name)
        super().__init__(self._index + self._name)

    def __new__(
            cls,
            s: IndexString,
            **kwargs,
    ) -> IndexString:
        """
        Overrides str.__new__, allowing keyword arguments to be supplied to IndexString
        (see: https://stackoverflow.com/a/38575015/11161432)
        """
        inst = str.__new__(cls, s)
        inst.__dict__.update(kwargs)
        return inst

    @property
    def idx(self) -> int:
        """Returns the index portion of the IndexString (as an integer)."""
        return int(self._index)

    @property
    def name(self) -> str:
        """Returns the index (as an integer) of the IndexString."""
        return self._name

    @staticmethod
    def validate_index(index: int) -> str:
        """Validates the index portion of the IndexString."""
        if not isinstance(index, int):
            raise TypeError(f'"index" must be int, not "{index.__class__.__name__}"')
        return str(index)

    @staticmethod
    def validate_name(name: str) -> str:
        """Validates the name portion of the IndexString."""
        if not isinstance(name, str):
            raise TypeError(f'"name" must be str, not "{name.__class__.__name__}"')
        if not name:
            raise ValueError('"name" cannot be an empty string')
        return name
