"""Projection operator: selects a subset of columns from child rows."""

from typing import Any, Iterator, List  # noqa: F401

from .base import Operator


class ProjectOperator(Operator):
    """Consumes rows from child and yields rows with only the specified column indices."""

    def __init__(self, child: Operator, column_indices: List[int]) -> None:
        """
        column_indices: list of 0-based column indices to output (in order).
        """
        self.child = child
        self.column_indices = column_indices
        self._child_iter: Iterator[List[Any]] = None  # type: ignore

    def __iter__(self) -> Iterator[List[Any]]:
        self._child_iter = iter(self.child)
        return self

    def __next__(self) -> List[Any]:
        if self._child_iter is None:
            self._child_iter = iter(self.child)
        row = next(self._child_iter)
        return [row[i] for i in self.column_indices]
