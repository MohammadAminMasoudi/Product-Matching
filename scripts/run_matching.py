import argparse
import os
import pandas as pd

from product_matching import load_workbook, match_two_sheets


def _get_sheet(df_by_name, ref):
    if isinstance(ref, int):
        name = list(df_by_name.keys())[ref]
        return name, df_by_name[name]
    else:
        return ref, df_by_name[ref]


def main():
    parser = argparse.ArgumentParser(
        description="Rule-based product matching between two catalog sheets."
    )
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Path to Excel workbook (e.g. data/test.xlsx).",
    )
    parser.add_argument(
        "--sheet-a",
        type=str,
        default="0",
        help="Sheet index (0-based) or name for company A (default: 0).",
    )
    parser.add_argument(
        "--sheet-b",
        type=str,
        default="1",
        help="Sheet index (0-based) or name for company B (default: 1).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Path to output CSV (default: data/test_matches.csv in same folder).",
    )

    args = parser.parse_args()

    workbook = load_workbook(args.input_file)

    # interpret sheet refs
    try:
        sa = int(args.sheet_a)
    except ValueError:
        sa = args.sheet_a
    try:
        sb = int(args.sheet_b)
    except ValueError:
        sb = args.sheet_b

    sheet_a_name, df_a = _get_sheet(workbook, sa)
    sheet_b_name, df_b = _get_sheet(workbook, sb)

    print(f"Loaded sheets: A='{sheet_a_name}', B='{sheet_b_name}'")
    print(f"A rows={len(df_a)}, B rows={len(df_b)}")

    matches_df = match_two_sheets(df_a, df_b)
    print(f"Found {len(matches_df)} matches (after thresholding).")

    # Add original titles for easier inspection
    matches_df = matches_df.copy()
    matches_df["A_Title"] = df_a.loc[matches_df["a_idx"]]["Title"].values
    matches_df["B_Title"] = df_b.loc[matches_df["b_idx"]]["Title"].values

    # default output path
    if args.output_file is None:
        base_dir = os.path.dirname(args.input_file)
        args.output_file = os.path.join(base_dir, "test_matches.csv")

    matches_df.to_csv(args.output_file, index=False)
    print(f"Saved matches to: {args.output_file}")


if __name__ == "__main__":
    main()