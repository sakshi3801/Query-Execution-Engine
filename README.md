# In-Memory Query Execution Engine

A SQL-like query execution engine that supports **filtering**, **projection**, and **full table scans** over structured in-memory data. It includes a query parser, an execution plan tree, an iterator-based execution model, and hash-based indexing for faster lookups.

## Features

- **SQL-like queries**: `SELECT col1, col2 | * FROM table [WHERE conditions]`
- **Filtering**: `WHERE` with `=`, `!=`, `<`, `<=`, `>`, `>=`, and `AND` / `OR`
- **Projection**: Select specific columns or `*` for all
- **Execution plan tree**: Queries are parsed into an AST and then compiled into an operator pipeline (scan → filter → project)
- **Iterator-based execution**: Pull-based model with **Scan**, **Filter**, and **Project** operators for efficient in-memory processing
- **Hash-based indexing**: Optional indexes on columns to optimize equality lookups (e.g. `WHERE id = 5`) and reduce lookup latency

## Project Structure

```
Query-engine/
├── src/
│   ├── schema.py      # Column types and table schema
│   ├── table.py       # In-memory table with row storage
│   ├── index.py       # Hash index for O(1) equality lookups
│   ├── ast.py         # Abstract syntax tree (SELECT query, predicates)
│   ├── parser.py      # SQL-like query parser
│   ├── planner.py     # Builds operator tree from parsed query
│   ├── engine.py      # Main QueryEngine API
│   └── operators/
│       ├── base.py    # Base operator (iterator interface)
│       ├── scan.py    # Full table scan
│       ├── filter.py  # WHERE predicate filter
│       ├── project.py # Column projection
│       └── index_scan.py  # Index-backed scan for equality
├── examples/
│   └── demo.py        # Demo script
└── README.md
```

## Usage

### 1. Define schema and create a table

```python
from src import QueryEngine, Table, Schema, Column, DataType

schema = Schema(columns=[
    Column("id", DataType.INTEGER),
    Column("name", DataType.STRING),
    Column("department", DataType.STRING),
    Column("salary", DataType.FLOAT),
])
employees = Table("employees", schema)
employees.insert_many([
    [1, "Alice", "Engineering", 95000.0],
    [2, "Bob", "Sales", 72000.0],
])
```

### 2. Optional: create hash indexes

```python
employees.create_index("id")
employees.create_index("department")
```

### 3. Run queries

```python
engine = QueryEngine()
engine.register_table(employees)

# Full result as list
rows = engine.execute("SELECT name, salary FROM employees WHERE department = 'Engineering'")

# Or lazy iterator
for row in engine.execute_iter("SELECT * FROM employees WHERE id = 1"):
    print(row)
```

### Supported query form

- **SELECT** `col1, col2, ...` or `*`
- **FROM** `table_name`
- **WHERE** (optional) `col = value`, `col != value`, `col < value`, etc., combined with **AND** / **OR**

String literals: `'single quoted'` or `"double quoted"`. Numbers and booleans (`true`/`false`) are supported.

## Running the demo

From the project root:

```bash
python examples/demo.py
```

You should see several example queries: projection, filtering, index-optimized lookup, and lazy iteration.

## Design notes

- **Parser**: Tokenizes the query and builds a `SelectQuery` AST with an optional `Predicate` tree for the WHERE clause.
- **Planner**: Chooses a full **Scan** or an **IndexScan** when the WHERE clause is a single equality on an indexed column; then adds **Filter** (if needed) and **Project**.
- **Operators**: Each operator implements the iterator protocol; the pipeline is pull-based (consumer calls `next()` on the root, which pulls from scan → filter → project).
- **Hash index**: Maps column value → set of row IDs so that `WHERE col = value` can resolve matching rows without scanning the whole table.

## Requirements

- Python 3.9+ (uses standard library only; no external dependencies).
