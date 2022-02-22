import unittest
from contextlib import contextmanager
from typing import Sequence

# Flag that ignores decorated_tests
SKIP_TESTS = True


class NotEmptyTestCase(unittest.TestCase):
    """TestCase extension with a method for asserting whether a sequence is empty or not."""

    @contextmanager
    def assertSequenceNotEmpty(self, sequence: Sequence):
        """ContextManager for asserting that a Sequence has at least one value in it."""
        if len(sequence) < 1:
            self.fail(f"Empty sequence of type {type(sequence)}")
        yield
