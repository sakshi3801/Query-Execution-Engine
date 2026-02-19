#!/usr/bin/env python3
"""Demo: In-memory query engine with filtering, projection, and index optimization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import QueryEngine, Table, Schema, Column, DataType


def main() -> None:
    # Define schema: id, name, department, salary
    schema = Schema(
        columns=[
            Column("id", DataType.INTEGER),
            Column("name", DataType.STRING),
            Column("department", DataType.STRING),
            Column("salary", DataType.FLOAT),
        ]
    )
    employees = Table("employees", schema)
    employees.insert_many([
        [1, "Alice", "Engineering", 95000.0],
        [2, "Bob", "Sales", 72000.0],
        [3, "Carol", "Engineering", 98000.0],
        [4, "Dave", "Marketing", 65000.0],
        [5, "Eve", "Engineering", 110000.0],
        [6, "Frank", "Sales", 68000.0],
    ])
    # Hash index on id for fast lookups
    employees.create_index("id")
    employees.create_index("department")

    engine = QueryEngine()
    engine.register_table(employees)

    print("=== In-Memory Query Engine Demo ===\n")

    # Full table scan + projection
    print("1. SELECT name, salary FROM employees")
    rows = engine.execute("SELECT name, salary FROM employees")
    for row in rows:
        print("  ", row)
    print()

    # Filter (full scan with WHERE)
    print("2. SELECT * FROM employees WHERE department = 'Engineering'")
    rows = engine.execute("SELECT * FROM employees WHERE department = 'Engineering'")
    for row in rows:
        print("  ", row)
    print()

    # Index-optimized: equality on indexed column (id)
    print("3. SELECT * FROM employees WHERE id = 3  (uses hash index on id)")
    rows = engine.execute("SELECT * FROM employees WHERE id = 3")
    for row in rows:
        print("  ", row)
    print()

    # Filter with comparison
    print("4. SELECT name, salary FROM employees WHERE salary >= 90000")
    rows = engine.execute("SELECT name, salary FROM employees WHERE salary >= 90000")
    for row in rows:
        print("  ", row)
    print()

    # AND condition
    print("5. SELECT * FROM employees WHERE department = 'Sales' AND salary > 70000")
    rows = engine.execute(
        "SELECT * FROM employees WHERE department = 'Sales' AND salary > 70000"
    )
    for row in rows:
        print("  ", row)
    print()

    # Iterator-based (lazy) execution
    print("6. Lazy iteration (first 2 rows only):")
    it = engine.execute_iter("SELECT id, name FROM employees")
    for i, row in enumerate(it):
        if i >= 2:
            break
        print("  ", row)
    print("  ... (iterator can be continued)")
    print()

    print("Done.")


if __name__ == "__main__":
    main()
