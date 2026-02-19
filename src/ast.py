"""Abstract syntax tree for parsed SQL-like queries."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union


class BinaryOp(Enum):
    """Comparison and logical operators for WHERE clauses."""

    EQ = "="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    AND = "AND"
    OR = "OR"


@dataclass
class Predicate:
    """A predicate: column op value, or left AND/OR right."""

    op: BinaryOp
    left: Union["Predicate", str, None] = None  # column name or left predicate
    right: Union[Any, "Predicate", None] = None  # value or right predicate

    def is_equality(self) -> bool:
        return self.op == BinaryOp.EQ

    def is_comparison(self) -> bool:
        return self.op in (BinaryOp.EQ, BinaryOp.NE, BinaryOp.LT, BinaryOp.LE, BinaryOp.GT, BinaryOp.GE)


@dataclass
class SelectQuery:
    """Parsed SELECT ... FROM ... [WHERE ...] query."""

    columns: List[str]  # empty or ["*"] means all columns
    table_name: str
    where: Optional[Predicate] = None

    def select_all(self) -> bool:
        return not self.columns or (len(self.columns) == 1 and self.columns[0] == "*")
