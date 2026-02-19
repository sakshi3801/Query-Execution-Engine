"""Query engine: parse SQL-like queries, build execution plans, run them."""

from typing import Any, Dict, List

from .parser import parse
from .parser import ParseError
from .planner import Planner
from .table import Table


class QueryEngine:
    """In-memory SQL-like query execution engine.

    Supports:
    - SELECT col1, col2 | * FROM table [WHERE conditions]
    - Filtering (WHERE with =, !=, <, <=, >, >=, AND, OR)
    - Projection (column selection)
    - Full table scans and hash-based index scans for equality
    """

    def __init__(self) -> None:
        self._tables: Dict[str, Table] = {}

    def register_table(self, table: Table) -> None:
        """Register a table by name for query execution."""
        self._tables[table.name] = table

    def execute(self, query: str) -> List[List[Any]]:
        """Parse query, build plan, execute, and return result rows."""
        ast = parse(query)
        planner = Planner(self._tables)
        plan = planner.plan(ast)
        return list(plan)

    def execute_iter(self, query: str):
        """Parse query, build plan, return iterator over result rows (lazy execution)."""
        ast = parse(query)
        planner = Planner(self._tables)
        plan = planner.plan(ast)
        return iter(plan)
