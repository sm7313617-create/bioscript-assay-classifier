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


def classify_folder(folder_path: Path, categories: dict[str, list[str]]) -> tuple[str, str]:
    """Classify a folder returning (category, method).

    Method is one of: 'metadata', 'keyword', 'unmatched'
    """
    # 1. Prefer metadata.category from .json files
    meta_cat = extract_metadata_category(folder_path)
    if meta_cat:
        return meta_cat, "metadata"

    # 2. Fall back to keyword match on folder name
    folder_lower = folder_path.name.lower()
    for category, keywords in categories.items():
        if not keywords:
            continue
        for keyword in keywords:
            if keyword.lower() in folder_lower:
                return category, "keyword"

    # 3. Fall back to Other if unmatched
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/classify.py <dataset_root> [config_path] [output_dir]")
        sys.exit(1)

    dataset_root = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "config/categories.yaml"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"

    categories = load_categories(config_path)
    folders = enumerate_folders(dataset_root)

    print(f"Found {len(folders)} protocol folder(s) in '{dataset_root}'.")
    audit_records = []
    for folder in folders:
        category, source = classify_folder(folder, categories)
        audit_records.append({"folder_name": folder.name, "category": category, "source": source})
        print(f"  {folder.name} -> {category} [{source}]")

    summary_file, audit_file = export_results(audit_records, output_dir=output_dir, categories=categories)
    print(f"\nExported summary to: {summary_file}")
    print(f"Exported audit trail to: {audit_file}")


if __name__ == "__main__":
    main()
