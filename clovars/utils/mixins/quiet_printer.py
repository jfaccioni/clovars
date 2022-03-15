from __future__ import annotations


class QuietPrinterMixin:
    """Mixin that allows a class to control its printing output by using a verbose flag."""
    def __init__(
            self,
            verbose: bool = False,
            *args,
            **kwargs,
    ) -> None:
        """Initializes a QuietPrinterMixin instance."""
        self.verbose = verbose
        super().__init__(*args, **kwargs)

    def quiet_print(
            self,
            *args,
            **kwargs
    ) -> None:
        """Prints the message only if the verbose flag is set to True."""
        if self.verbose is True:
            print(*args, **kwargs)
