"""Product matching package."""

from .config import COLUMNS, MATCHING
from .matcher import (
    load_workbook,
    preprocess_sheet,
    generate_candidates,
    compute_features,
    rule_based_matching,
    match_two_sheets,
)

__all__ = [
    "COLUMNS",
    "MATCHING",
    "load_workbook",
    "preprocess_sheet",
    "generate_candidates",
    "compute_features",
    "rule_based_matching",
    "match_two_sheets",
]