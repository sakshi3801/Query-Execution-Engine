"""Hash-based index for fast equality lookups on a column."""

from typing import Any, List, Set

from .schema import Schema


class HashIndex:
    """Hash index mapping column value -> set of row indices for O(1) lookups."""

    def __init__(self, schema: Schema, column_name: str) -> None:
        self.schema = schema
        self.column_name = column_name
        self._col_idx = schema.column_index(column_name)
        self._map: dict[Any, Set[int]] = {}

    def _key(self, row: List[Any]) -> Any:
        """Extract index key from row. Use hashable representation for lists/dicts."""
        v = row[self._col_idx]
        if isinstance(v, list):
            v = tuple(v)
        if isinstance(v, dict):
            v = tuple(sorted(v.items()))
        return v

    def insert(self, row: List[Any], row_id: int) -> None:
        k = self._key(row)
        if k not in self._map:
            self._map[k] = set()
        self._map[k].add(row_id)

    def lookup(self, value: Any) -> Set[int]:
        """Return set of row indices where column equals value."""
        k = value
        if isinstance(k, list):
            k = tuple(k)
        if isinstance(k, dict):
            k = tuple(sorted(k.items()))
        return self._map.get(k, set()).copy()

    def contains(self, value: Any) -> bool:
        k = value
        if isinstance(k, list):
            k = tuple(k)
        if isinstance(k, dict):
            k = tuple(sorted(k.items()))
        return k in self._map
