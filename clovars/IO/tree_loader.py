from types import SimpleNamespace
from typing import Any

from ete3 import TreeNode


class CellNode(TreeNode):
    """Class representing a single node in a Tree."""
    def __init__(
            self,
            dist: float | None = None,
            support: float | None = None,
            name: str | None = None,
            **kwargs,
    ) -> None:
        """Initializes a CellNode instance."""
        super().__init__(dist=dist, support=support, name=name)
        self._clovars_namespace = SimpleNamespace(**kwargs)

    def __getattr__(
            self,
            name: str,
    ) -> Any:
        """
        Attempts to return the attribute from the clovars namespace
        if the attr_name hasn't been found by usual attribute access.
        """
        try:
            return getattr(self._clovars_namespace, name)
        except AttributeError:
            raise AttributeError(
                f'Clovars attribute "{name}" not found in object of type "{self.__class__.__name__}".\n'
                f'Existing attributes: {self.__clovars_attrs}'
            )

    def __setattr__(
            self,
            name: str,
            value: Any,
    ) -> None:
        """Sets the clovars attribute if the attr_name is found in the __clovars_attrs dict."""
        if name not in self.__dict__:
            return setattr(self._clovars_namespace, name, value)
        return super().__setattr__(name, value)


class TreeLoader:
    """Class responsible for loading """


if __name__ == '__main__':
    n = CellNode(foo='bar')
    print(n)
    print(n.foo2)
