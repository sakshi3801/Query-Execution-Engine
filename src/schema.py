"""Schema definitions for structured data: columns and types."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional


class DataType(Enum):
    """Supported column data types."""

    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"


@dataclass
class Column:
    """A named column with a data type."""

    name: str
    dtype: DataType

    def __hash__(self) -> int:
        return hash((self.name, self.dtype))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Column):
            return False
        return self.name == other.name and self.dtype == other.dtype


@dataclass
class Schema:
    """Table schema: ordered list of columns."""

    columns: List[Column] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._name_to_idx = {c.name: i for i, c in enumerate(self.columns)}

    def column_index(self, name: str) -> int:
        """Return 0-based index for column name. Raises KeyError if not found."""
        return self._name_to_idx[name]

    def column_names(self) -> List[str]:
        return [c.name for c in self.columns]

    def get_column(self, name: str) -> Optional[Column]:
        idx = self._name_to_idx.get(name)
        return self.columns[idx] if idx is not None else None

    def project(self, names: List[str]) -> "Schema":
        """Return a new schema with only the given column names (preserving order)."""
        cols = []
        for name in names:
            c = self.get_column(name)
            if c is None:
                raise KeyError(f"Column not found: {name}")
            cols.append(c)
        return Schema(columns=cols)

    def validate_row(self, row: List[Any]) -> bool:
        """Check that row length matches schema. Does not validate types deeply."""
        return len(row) == len(self.columns)
