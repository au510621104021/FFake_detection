"""
Prepare ISOT Fake News dataset into project-friendly CSV format.

Input:
    data/isot/Fake.csv
    data/isot/True.csv

Output:
    data/isot/dataset.csv with columns: text,image_path,label
    label: 0=real, 1=fake
"""

import argparse
from pathlib import Path

import pandas as pd


def build_rows(df: pd.DataFrame, label: int) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        title = str(row.get("title", "")).strip()
        body = str(row.get("text", "")).strip()
        text = f"{title}. {body}".strip(". ").strip()
        if not text:
            continue
        rows.append({
            "text": text,
            "image_path": "",
            "label": label,
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Prepare ISOT dataset for this project")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data/isot",
        help="Directory containing Fake.csv and True.csv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output CSV path (defaults to <data_dir>/dataset.csv)",
    )
    parser.add_argument(
        "--fake_csv",
        type=str,
        default=None,
        help="Optional direct path to Fake.csv",
    )
    parser.add_argument(
        "--true_csv",
        type=str,
        default=None,
        help="Optional direct path to True.csv",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    fake_path = Path(args.fake_csv) if args.fake_csv else data_dir / "Fake.csv"
    true_path = Path(args.true_csv) if args.true_csv else data_dir / "True.csv"
    output_path = Path(args.output) if args.output else data_dir / "dataset.csv"

    # Resolve common casing variants automatically when exact names are missing.
    if not fake_path.exists() and not args.fake_csv:
        for candidate in data_dir.glob("*.csv"):
            if candidate.name.lower() == "fake.csv":
                fake_path = candidate
                break
    if not true_path.exists() and not args.true_csv:
        for candidate in data_dir.glob("*.csv"):
            if candidate.name.lower() == "true.csv":
                true_path = candidate
                break

    if not fake_path.exists() or not true_path.exists():
        available = []
        if data_dir.exists():
            available = sorted([p.name for p in data_dir.glob("*.csv")])
        raise FileNotFoundError(
            "Missing input files.\n"
            f"Expected Fake.csv and True.csv under: {data_dir}\n"
            f"Resolved paths: fake={fake_path}, true={true_path}\n"
            f"Available CSVs: {available if available else 'none'}\n"
            "Tip: pass --fake_csv and --true_csv with explicit file paths."
        )

    fake_df = pd.read_csv(fake_path)
    true_df = pd.read_csv(true_path)

    rows = []
    rows.extend(build_rows(fake_df, 1))
    rows.extend(build_rows(true_df, 0))

    out_df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    print(f"[ISOT] Wrote {len(out_df)} samples to {output_path}")
    print("[ISOT] Labels: 0=real, 1=fake")


if __name__ == "__main__":
    main()
