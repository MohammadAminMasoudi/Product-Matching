# Product Matching with Text & Price Similarity

This repository contains a small product-matching pipeline that links similar products
between two e‑commerce catalogs using:

* Text cleaning and normalization
* Category normalization
* Fuzzy string matching (RapidFuzz)
* TF‑IDF cosine similarity
* Sentence‑transformer embeddings (`all-MiniLM-L6-v2`)
* Simple rule‑based matching on top of similarity features

The code is adapted from a Google Colab notebook and reorganized into a clean,
reusable Python package.

## Project structure

```text
.
├── product_matching/
│   ├── __init__.py
│   ├── config.py
│   ├── text_utils.py
│   └── matcher.py
├── scripts/
│   └── run_matching.py
├── requirements.txt
└── README.md
```

## Installation

```bash
# optional but recommended
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
```

> Note: `sentence-transformers` will download the model
> `all-MiniLM-L6-v2` the first time you run the script.

## Usage

From the root of the repo:

```bash
python scripts/run_matching.py \
    --input-file data/test.xlsx \
    --sheet-a 0 \
    --sheet-b 1 \
    --output-file data/test_matches.csv
```

* `--sheet-a` and `--sheet-b` can be **indices** (0-based) or **sheet names**.
* The output CSV will contain candidate pairs with similarity features and the
  final rule-based matching.

## Configuration

You can tweak thresholds and column names in [`product_matching/config.py`](product_matching/config.py):

* `EMB_SIM_THRESHOLD` – minimum embedding cosine similarity to accept a match
* `COLUMNS` – mapping of logical names (`title`, `detail`, `category`, `price`)
  to the actual column names in your Excel sheets.

