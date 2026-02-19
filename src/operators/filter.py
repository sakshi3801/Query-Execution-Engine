from typing import Any, Iterator, List

from ..ast import BinaryOp, Predicate
from .base import Operator


def _eval_predicate(pred: Predicate, row: List[Any], col_index: dict[str, int]) -> bool:
    if pred.op in (BinaryOp.EQ, BinaryOp.NE, BinaryOp.LT, BinaryOp.LE, BinaryOp.GT, BinaryOp.GE):
        col = pred.left
        val = pred.right
        if col not in col_index:
            return False
        row_val = row[col_index[col]]
        if pred.op == BinaryOp.EQ:
            return row_val == val
        if pred.op == BinaryOp.NE:
            return row_val != val
        if pred.op == BinaryOp.LT:
            return row_val < val
        if pred.op == BinaryOp.LE:
            return row_val <= val
        if pred.op == BinaryOp.GT:
            return row_val > val
        if pred.op == BinaryOp.GE:
            return row_val >= val
    if pred.op == BinaryOp.AND:
        return _eval_predicate(pred.left, row, col_index) and _eval_predicate(pred.right, row, col_index)
    if pred.op == BinaryOp.OR:
        return _eval_predicate(pred.left, row, col_index) or _eval_predicate(pred.right, row, col_index)
    return False


class FilterOperator(Operator):
    """Consumes rows from child and yields only rows satisfying the predicate."""

    def __init__(self, child: Operator, predicate: Predicate, column_index: dict[str, int]) -> None:
        self.child = child
        self.predicate = predicate
        self.column_index = column_index
        self._child_iter: Iterator[List[Any]] = None  # type: ignore

    def __iter__(self) -> Iterator[List[Any]]:
        self._child_iter = iter(self.child)
        return self

    def __next__(self) -> List[Any]:
        if self._child_iter is None:
            self._child_iter = iter(self.child)
        while True:
            row = next(self._child_iter)
            if _eval_predicate(self.predicate, row, self.column_index):
                return row
        raise StopIteration  # unreachable, next() raises
