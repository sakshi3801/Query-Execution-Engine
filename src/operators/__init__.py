"""Query execution operators: scan, filter, project (iterator-based pipeline)."""

from .base import Operator
from .scan import ScanOperator
from .filter import FilterOperator
from .project import ProjectOperator
from .index_scan import IndexScanOperator

__all__ = [
    "Operator",
    "ScanOperator",
    "FilterOperator",
    "ProjectOperator",
    "IndexScanOperator",
]
