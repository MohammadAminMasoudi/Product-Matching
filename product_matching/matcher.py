from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Iterable, Union

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

from .text_utils import clean_text, normalize_price, normalize_category
from .config import COLUMNS, MATCHING


def load_workbook(path: str) -> Dict[str, pd.DataFrame]:
    \"\"\"Load all sheets of an Excel workbook into a dict of DataFrames.\"\"\"
    xls = pd.ExcelFile(path)
    sheets = {}
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        sheets[sheet] = df
    return sheets


def preprocess_sheet(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Apply text & price normalization to a single catalog sheet.\"\"\"
    df = df.copy()
    df["clean_title"] = df[COLUMNS.title].apply(clean_text)
    df["clean_desc"] = df[COLUMNS.detail].apply(clean_text)
    df["clean_category"] = df[COLUMNS.category].apply(normalize_category)
    df["price_norm"] = df[COLUMNS.price].apply(normalize_price)
    return df


def generate_candidates(
    df1: pd.DataFrame, df2: pd.DataFrame
) -> List[Tuple[int, int]]:
    \"\"\"Generate candidate index pairs (row indices in df1, df2).

    If MATCHING.require_category_overlap is True, we only keep pairs with at
    least one overlapping category token; otherwise, all pairs are kept.
    \"\"\"
    candidates: List[Tuple[int, int]] = []
    for i, r1 in df1.iterrows():
        cat1_tokens = set(r1["clean_category"].split(" > ")) if r1["clean_category"] else set()
        for j, r2 in df2.iterrows():
            if not MATCHING.require_category_overlap:
                candidates.append((i, j))
                continue

            if not r1["clean_category"] or not r2["clean_category"]:
                continue

            cat2_tokens = set(r2["clean_category"].split(" > ")) if r2["clean_category"] else set()
            if cat1_tokens & cat2_tokens:
                candidates.append((i, j))
    return candidates


def compute_features(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    candidates: Iterable[Tuple[int, int]],
    model_name: str = None,
) -> pd.DataFrame:
    \"\"\"Compute similarity features for candidate product pairs.

    Returns a DataFrame with columns:
        a_idx, b_idx, fuzz_title, tfidf_sim, emb_sim, price_diff
    \"\"\"
    model_name = model_name or MATCHING.model_name
    model = SentenceTransformer(model_name)

    rows = []
    for a_idx, b_idx in candidates:
        a_title = df_a.loc[a_idx, "clean_title"]
        b_title = df_b.loc[b_idx, "clean_title"]

        # Fuzzy similarity (token sort ratio)
        fuzz_title = fuzz.token_sort_ratio(a_title, b_title) / 100.0

        # TF-IDF cosine similarity
        tfidf = TfidfVectorizer().fit([a_title, b_title])
        tfidf_sim = cosine_similarity(
            tfidf.transform([a_title]),
            tfidf.transform([b_title])
        )[0][0]

        # Embedding similarity
        emb_sim = util.cos_sim(
            model.encode(a_title),
            model.encode(b_title)
        ).item()

        # Price difference
        a_price = df_a.loc[a_idx, "price_norm"]
        b_price = df_b.loc[b_idx, "price_norm"]
        if not (pd.isna(a_price) or pd.isna(b_price)):
            price_diff = abs(float(a_price) - float(b_price))
        else:
            price_diff = np.nan

        rows.append(
            {
                "a_idx": a_idx,
                "b_idx": b_idx,
                "fuzz_title": fuzz_title,
                "tfidf_sim": float(tfidf_sim),
                "emb_sim": float(emb_sim),
                "price_diff": price_diff,
            }
        )

    return pd.DataFrame(rows)


def rule_based_matching(
    features_df: pd.DataFrame,
    emb_threshold: float | None = None,
) -> pd.DataFrame:
    \"\"\"Select best matching pairs using simple rules.

    Rules:
    * Keep only rows with emb_sim >= threshold.
    * For each a_idx, keep the candidate with highest emb_sim.
    * Prevent one-to-many by keeping first b_idx per a_idx sorted by emb_sim.
    \"\"\"
    emb_threshold = emb_threshold or MATCHING.EMB_SIM_THRESHOLD
    rule_matches = features_df[features_df["emb_sim"] >= emb_threshold]

    # sort by a_idx, similarity desc
    rule_matches_sorted = rule_matches.sort_values(
        by=["a_idx", "emb_sim"], ascending=[True, False]
    )

    # best per a_idx
    best_per_a = rule_matches_sorted.groupby("a_idx").first().reset_index()

    # Optional: deduplicate on b_idx (each target used at most once)
    best_unique_b = best_per_a.sort_values(
        "emb_sim", ascending=False
    ).drop_duplicates(subset="b_idx", keep="first")

    return best_unique_b.reset_index(drop=True)


def match_two_sheets(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
) -> pd.DataFrame:
    \"\"\"High-level helper: preprocess two sheets and return final matches.\"\"\"
    df_a_prep = preprocess_sheet(df_a)
    df_b_prep = preprocess_sheet(df_b)

    candidates = generate_candidates(df_a_prep, df_b_prep)
    features_df = compute_features(df_a_prep, df_b_prep, candidates)
    matches_df = rule_based_matching(features_df)
    return matches_df