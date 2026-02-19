"""Execution planner: converts parsed SelectQuery into an operator tree."""

from typing import Dict, Union

from .ast import SelectQuery
from .table import Table
from .operators import ScanOperator, FilterOperator, ProjectOperator, IndexScanOperator


class Planner:
    """Builds an operator pipeline from a parsed query and table catalog."""

    def __init__(self, tables: Dict[str, Table]) -> None:
        self.tables = tables

    def plan(
        self, query: SelectQuery
    ) -> Union[ScanOperator, FilterOperator, ProjectOperator, IndexScanOperator]:
        """Build execution plan: (Index)Scan -> optional Filter -> optional Project."""
        if query.table_name not in self.tables:
            raise KeyError(f"Table not found: {query.table_name}")
        table = self.tables[query.table_name]
        schema = table.schema
        col_index = {c.name: i for i, c in enumerate(schema.columns)}

        # Root: full scan or index scan when WHERE is single equality on indexed column
        root = self._build_scan(table, query)

        # Optional filter (full scan + WHERE, or index scan has no extra predicate)
        if query.where is not None and not isinstance(root, IndexScanOperator):
            root = FilterOperator(root, query.where, col_index)

        # Projection
        if not query.select_all():
            if query.columns == ["*"]:
                indices = list(range(len(schema.columns)))
            else:
                indices = [schema.column_index(c) for c in query.columns]
            root = ProjectOperator(root, indices)

        return root

    def _build_scan(self, table: Table, query: SelectQuery):
        """Use IndexScan when WHERE is a single equality on an indexed column."""
        if query.where is None or not query.where.is_equality():
            return ScanOperator(table)
        col = query.where.left
        if isinstance(col, str) and table.has_index(col):
            return IndexScanOperator(table, col, query.where.right)
        return ScanOperator(table)
