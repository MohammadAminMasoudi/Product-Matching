"""Configuration for the product matching pipeline."""

from dataclasses import dataclass

@dataclass
class ColumnConfig:
    title: str = "Title"
    detail: str = "Detail"
    category: str = "Category"
    price: str = "Price"

@dataclass
class MatchingConfig:
    # Model name for sentence-transformers
    model_name: str = "all-MiniLM-L6-v2"

    # Threshold for accepting a match based on embedding similarity
    EMB_SIM_THRESHOLD: float = 0.85

    # Whether to require at least one overlapping category token
    require_category_overlap: bool = False

COLUMNS = ColumnConfig()
MATCHING = MatchingConfig()