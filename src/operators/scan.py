"""Full table scan operator: iterates over all rows in a table."""

from typing import Any, Iterator, List

from ..table import Table
from .base import Operator


class ScanOperator(Operator):
    """Produces all rows from a table (full table scan)."""

    def __init__(self, table: Table) -> None:
        self.table = table
        self._iter: Iterator[List[Any]] = None  # type: ignore

    def __iter__(self) -> Iterator[List[Any]]:
        self._iter = self.table.rows()
        return self

    def __next__(self) -> List[Any]:
        if self._iter is None:
            self._iter = self.table.rows()
        return next(self._iter)
