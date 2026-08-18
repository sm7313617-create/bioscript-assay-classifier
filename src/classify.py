import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
import yaml


def load_categories(config_path: str | Path) -> dict[str, list[str]]:
    """Load categories and their associated keywords from a YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        categories = yaml.safe_load(f)
    return categories or {}


def load_overrides(config_path: str | Path = "config/overrides.yaml") -> dict[str, str]:
    """Load manual overrides mapping folder names to categories from a YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        return {}

    with open(config_file, "r", encoding="utf-8") as f:
        overrides = yaml.safe_load(f)
    return overrides or {}


def extract_metadata_category(folder_path: Path) -> str | None:
    """Extract category from a .json file with a metadata.category field if present."""
    for json_file in folder_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                metadata = data.get("metadata")
                if isinstance(metadata, dict) and metadata.get("category"):
                    return str(metadata["category"])
        except Exception:
            continue
    return None


def normalize_category(raw_value: str, categories: dict[str, list[str]]) -> str | None:
    """Map a raw string (from metadata or folder name) to one of the canonical categories."""
    if not raw_value:
        return None

    # Check exact match with canonical category names (case-insensitive)
    for canonical in categories.keys():
        if raw_value.strip().lower() == canonical.lower():
            return canonical

    # Check substring match against keywords in categories config
    raw_lower = raw_value.lower()
    for canonical, keywords in categories.items():
        if not keywords:
            continue
        for keyword in keywords:
            if keyword.lower() in raw_lower:
                return canonical

    return None


def classify_folder(
    folder_path: Path,
    categories: dict[str, list[str]],
    overrides: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Classify a folder returning (category, method).

    Method is one of: 'override', 'metadata', 'keyword', 'unmatched'
    Priority order:
    1. config/overrides.yaml exact match (highest priority — verified ground truth)
    2. metadata.category from the folder's .json file
    3. keyword match against config/categories.yaml
    4. Other (fallback)
    """
    # 1. Check manual overrides (ground truth)
    if overrides and folder_path.name in overrides:
        return overrides[folder_path.name], "override"

    # 2. Prefer metadata.category from .json files, normalized to canonical category
    meta_raw = extract_metadata_category(folder_path)
    if meta_raw:
        normalized_cat = normalize_category(meta_raw, categories)
        if normalized_cat and normalized_cat != "Other":
            return normalized_cat, "metadata"

    # 3. Fall back to keyword match on folder name
    folder_cat = normalize_category(folder_path.name, categories)
    if folder_cat and folder_cat != "Other":
        return folder_cat, "keyword"

    # 4. Fall back to Other if unmatched
    return "Other", "unmatched"


def enumerate_folders(dataset_root: str | Path) -> list[Path]:
    """Walk immediate subfolders of the dataset root directory."""
    root_path = Path(dataset_root)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Error: Directory '{dataset_root}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    folders = [item for item in root_path.iterdir() if item.is_dir()]
    return folders


def export_results(
    audit_records: list[dict[str, str]],
    output_dir: str | Path = "output",
    categories: dict[str, list[str]] | None = None,
) -> tuple[Path, Path]:
    """Export summary and audit-trail CSV files to output directory."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    summary_file = out_path / "summary.csv"
    audit_file = out_path / "audit_trail.csv"

    # 1. Export audit trail
    with open(audit_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["folder_name", "category", "source"])
        for record in audit_records:
            writer.writerow([record["folder_name"], record["category"], record["source"]])

    # 2. Export summary table
    total = len(audit_records)
    category_counts = Counter(r["category"] for r in audit_records)

    seen_categories = []
    if categories:
        for cat in categories.keys():
            if cat not in seen_categories:
                seen_categories.append(cat)
    for cat in category_counts.keys():
        if cat not in seen_categories:
            seen_categories.append(cat)

    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "count", "percent"])
        for cat in seen_categories:
            count = category_counts.get(cat, 0)
            percent = (count / total * 100) if total > 0 else 0.0
            writer.writerow([cat, count, f"{percent:.2f}%"])

    return summary_file, audit_file


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Classify BioScript protocol folders into assay-type categories."
    )
    parser.add_argument(
        "dataset_root",
        type=str,
        help="Path to dataset root folder containing protocol subdirectories.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/categories.yaml",
        help="Path to YAML category definitions (default: config/categories.yaml).",
    )
    parser.add_argument(
        "--overrides",
        type=str,
        default="config/overrides.yaml",
        help="Path to YAML manual overrides (default: config/overrides.yaml).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="output",
        help="Directory to save CSV outputs (default: output).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed classification per folder during execution.",
    )
    return parser.parse_args(args)


def main():
    args = parse_args()
    categories = load_categories(args.config)
    overrides = load_overrides(args.overrides)
    folders = enumerate_folders(args.dataset_root)

    print(f"Found {len(folders)} protocol folder(s) in '{args.dataset_root}'.")
    audit_records = []
    for folder in folders:
        category, source = classify_folder(folder, categories, overrides=overrides)
        audit_records.append({"folder_name": folder.name, "category": category, "source": source})
        if args.verbose:
            print(f"  {folder.name} -> {category} [{source}]")

    summary_file, audit_file = export_results(
        audit_records, output_dir=args.output_dir, categories=categories
    )
    print(f"\nClassification complete.")
    print(f"Exported summary to:     {summary_file}")
    print(f"Exported audit trail to: {audit_file}")


if __name__ == "__main__":
    main()
