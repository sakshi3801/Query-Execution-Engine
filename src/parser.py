"""SQL-like query parser: SELECT ... FROM ... WHERE ... into AST."""

import re
from typing import List, Optional, Tuple

from .ast import BinaryOp, Predicate, SelectQuery


class ParseError(Exception):
    """Raised when query parsing fails."""

    pass


def _tokenize(s: str) -> List[str]:
    """Split query into tokens (keywords, identifiers, literals, operators)."""
    s = s.strip()
    tokens = []
    # Match: words, numbers, quoted strings, = != < <= > >= ( ) , *
    pattern = r"(?i)\b(SELECT|FROM|WHERE|AND|OR)\b|\*|[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|'[^']*'|\"[^\"]*\"|[=<>!]=?|[,()]"
    for m in re.finditer(pattern, s):
        tokens.append(m.group(0))
    return tokens


def _parse_value(tok: str):
    """Convert token to Python value (number or string)."""
    if tok.startswith("'") and tok.endswith("'"):
        return tok[1:-1]
    if tok.startswith('"') and tok.endswith('"'):
        return tok[1:-1]
    try:
        if "." in tok:
            return float(tok)
        return int(tok)
    except ValueError:
        pass
    if tok.upper() in ("TRUE", "FALSE"):
        return tok.upper() == "TRUE"
    return tok


def _parse_predicate(tokens: List[str], pos: int) -> Tuple[Predicate, int]:
    """Parse WHERE predicate: col op value [AND/OR pred]*. Returns (predicate, next_pos)."""
    if pos >= len(tokens):
        raise ParseError("Unexpected end in WHERE clause")

    def parse_primary(p: int) -> Tuple[Predicate, int]:
        if p + 2 >= len(tokens):
            raise ParseError("Incomplete comparison in WHERE")
        col = tokens[p]
        op_str = tokens[p + 1]
        val_tok = tokens[p + 2]
        op_map = {
            "=": BinaryOp.EQ, "!=": BinaryOp.NE,
            "<": BinaryOp.LT, "<=": BinaryOp.LE,
            ">": BinaryOp.GT, ">=": BinaryOp.GE,
        }
        if op_str not in op_map:
            raise ParseError(f"Unknown operator: {op_str}")
        value = _parse_value(val_tok)
        return Predicate(op=op_map[op_str], left=col, right=value), p + 3

    pred, pos = parse_primary(pos)

    while pos < len(tokens):
        upper = tokens[pos].upper()
        if upper == "AND":
            pos += 1
            right, pos = parse_primary(pos)
            pred = Predicate(op=BinaryOp.AND, left=pred, right=right)
        elif upper == "OR":
            pos += 1
            right, pos = parse_primary(pos)
            pred = Predicate(op=BinaryOp.OR, left=pred, right=right)
        else:
            break
    return pred, pos


def parse(query: str) -> SelectQuery:
    """Parse a SQL-like query into a SelectQuery AST.

    Supported: SELECT col1, col2 | * FROM table [WHERE col op value [AND|OR ...]]
    """
    tokens = _tokenize(query)
    if not tokens:
        raise ParseError("Empty query")

    if tokens[0].upper() != "SELECT":
        raise ParseError("Query must start with SELECT")
    pos = 1

    # Parse column list
    columns: List[str] = []
    while pos < len(tokens) and tokens[pos].upper() not in ("FROM",):
        if tokens[pos] == "*":
            columns = ["*"]
            pos += 1
            break
        if tokens[pos] == ",":
            pos += 1
            continue
        columns.append(tokens[pos])
        pos += 1

    if pos >= len(tokens) or tokens[pos].upper() != "FROM":
        raise ParseError("Expected FROM")
    pos += 1
    if pos >= len(tokens):
        raise ParseError("Expected table name after FROM")
    table_name = tokens[pos]
    pos += 1

    where: Optional[Predicate] = None
    if pos < len(tokens) and tokens[pos].upper() == "WHERE":
        pos += 1
        where, pos = _parse_predicate(tokens, pos)
    if pos < len(tokens):
        raise ParseError(f"Unexpected token after query: {tokens[pos]}")

    return SelectQuery(columns=columns or ["*"], table_name=table_name, where=where)
