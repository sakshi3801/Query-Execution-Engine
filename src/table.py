from typing import Any, Iterator, List, Optional

from .schema import Schema
from .index import HashIndex


class Table:
    """In-memory table with schema and row storage. Supports hash indexes."""

    def __init__(self, name: str, schema: Schema) -> None:
        self.name = name
        self.schema = schema
        self._rows: List[List[Any]] = []
        self._indexes: dict[str, HashIndex] = {}

    def insert(self, row: List[Any]) -> None:
        """Insert a row. Row must match schema length and order."""
        if not self.schema.validate_row(row):
            raise ValueError(
                f"Row length {len(row)} does not match schema {len(self.schema.columns)}"
            )
        idx = len(self._rows)
        self._rows.append(list(row))
        for index in self._indexes.values():
            index.insert(row, idx)

    def insert_many(self, rows: List[List[Any]]) -> None:
        for row in rows:
            self.insert(row)

    def row_count(self) -> int:
        return len(self._rows)

    def get_row(self, row_id: int) -> List[Any]:
        return self._rows[row_id]

    def rows(self) -> Iterator[List[Any]]:
        """Iterate over all rows (full table scan)."""
        yield from self._rows

    def create_index(self, column_name: str) -> None:
        """Build a hash index on the given column for faster lookups."""
        if column_name not in self.schema._name_to_idx:
            raise KeyError(f"Column not in schema: {column_name}")
        idx = HashIndex(self.schema, column_name)
        for i, row in enumerate(self._rows):
            idx.insert(row, i)
        self._indexes[column_name] = idx

    def has_index(self, column_name: str) -> bool:
        return column_name in self._indexes

    def get_index(self, column_name: str) -> Optional[HashIndex]:
        return self._indexes.get(column_name)

    def __repr__(self) -> str:
        return f"Table(name={self.name!r}, rows={self.row_count()}, schema={self.schema.column_names()})"
