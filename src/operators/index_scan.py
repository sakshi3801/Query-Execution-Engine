from typing import Any, Iterator, List

from ..table import Table
from .base import Operator


class IndexScanOperator(Operator):
    def __init__(self, table: Table, column_name: str, value: Any) -> None:
        self.table = table
        self.column_name = column_name
        self.value = value
        self._row_ids: List[int] = []
        self._pos = 0

    def __iter__(self) -> Iterator[List[Any]]:
        index = self.table.get_index(self.column_name)
        if index is None:
            raise RuntimeError(f"No index on column {self.column_name}")
        self._row_ids = sorted(index.lookup(self.value))
        self._pos = 0
        return self

    def __next__(self) -> List[Any]:
        if self._pos >= len(self._row_ids):
            raise StopIteration
        row_id = self._row_ids[self._pos]
        self._pos += 1
        return self.table.get_row(row_id)
