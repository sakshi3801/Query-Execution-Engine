"""Base operator: iterator interface for pull-based execution."""

from abc import ABC, abstractmethod
from typing import Any, Iterator, List


class Operator(ABC):
    """Base class for all operators. Each operator is an iterator yielding rows."""

    @abstractmethod
    def __iter__(self) -> Iterator[List[Any]]:
        """Return iterator over result rows (each row is a list of values)."""
        ...

    @abstractmethod
    def __next__(self) -> List[Any]:
        """Return next row. Raises StopIteration when done."""
        ...

    def next(self) -> List[Any]:
        """Alias for __next__ for Python 2 style iteration."""
        return self.__next__()

    def execute(self) -> List[List[Any]]:
        """Consume entire iterator and return all rows (for testing/convenience)."""
        return list(self)
