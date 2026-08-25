import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
import yaml

SPECIFIC_CATEGORIES = [
    "RNA_Sequencing_Epigenomics",
    "Synthetic_Biology_Genetic_Engineering",
    "CRISPR_Based_Diagnostics",
    "Aptamer_Selection_SELEX",
    "Antimicrobial_Susceptibility_Testing",
    "Clinical_Diagnostics_Newborn_Screening",
    "Phytochemical_Colorimetric_Assay",
    "Chemistry_Synthesis_Purification_MS",
    "Oncology_Cell_Pathology",
    "Enzyme_Kinetics_Screening",
    "Device_Fabrication_Protocol_Formalization",
]

BROAD_CATEGORIES = [
    "Cell_Based_Assay",
    "PCR_NucleicAcid",
    "ELISA_Immunoassay",
    "Extraction_Purification",
    "Omics_Proteomics",
    "Small_Molecule_Drug",
    "Immunoprecipitation",
    "Aerosol_Environmental",
    "Dilution",
]


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


def find_non_negated_match(raw_text: str, keyword: str) -> bool:
    """Check whether keyword matches raw_text without being negated by prefixes/suffixes."""
    if not raw_text or not keyword:
        return False
    raw_lower = raw_text.lower()
    kw_lower = keyword.lower()
    negation_prefixes = ("no_", "non_", "without_", "no-", "non-", "without-", "free_", "free-", "_free", "-free")
    negation_suffixes = ("_free", "-free", "free_", "free-", "free")

    start = 0
    while True:
        idx = raw_lower.find(kw_lower, start)
        if idx == -1:
            return False

        is_negated = False
        prefix_part = raw_lower[:idx]
        for prefix in negation_prefixes:
            if prefix_part.endswith(prefix):
                is_negated = True
                break

        if not is_negated:
            suffix_part = raw_lower[idx + len(kw_lower):]
            if not suffix_part.startswith(("_free_radical", "-free-radical", "free_radical")):
                for suffix in negation_suffixes:
                    if suffix_part.startswith(suffix):
                        is_negated = True
                        break

        if not is_negated:
            return True

        start = idx + 1


def get_best_match(raw_value: str | None, categories: dict[str, list[str]]) -> dict | None:
    """Find the best matching category for a raw string based on specificity and keyword length."""
    if not raw_value:
        return None
    raw_lower = raw_value.strip().lower()

    # Exact match with canonical category names (case-insensitive)
    for canonical in categories.keys():
        if raw_lower == canonical.lower():
            is_spec = canonical in SPECIFIC_CATEGORIES
            return {
                "category": canonical,
                "keyword": canonical,
                "is_specific": is_spec,
                "kw_len": len(canonical),
            }

    candidates = []
    for canonical, keywords in categories.items():
        if not keywords or canonical == "Other":
            continue
        for keyword in keywords:
            if find_non_negated_match(raw_lower, keyword):
                is_spec = canonical in SPECIFIC_CATEGORIES
                candidates.append({
                    "category": canonical,
                    "keyword": keyword,
                    "is_specific": is_spec,
                    "kw_len": len(keyword),
                })

    if not candidates:
        return None

    # Ranking:
    # 1. is_specific (Specific categories beat Broad categories)
    # 2. kw_len (Longer, more specific keyword beats shorter keyword)
    candidates.sort(key=lambda c: (1 if c["is_specific"] else 0, c["kw_len"]), reverse=True)
    return candidates[0]


def normalize_category(raw_value: str, categories: dict[str, list[str]]) -> str | None:
    """Map a raw string (from metadata or folder name) to one of the canonical categories."""
    best = get_best_match(raw_value, categories)
    return best["category"] if best else None


def classify_folder(
    folder_path: Path,
    categories: dict[str, list[str]],
    overrides: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Classify a folder returning (category, method).

    Method is one of: 'override', 'metadata', 'keyword', 'unmatched'
    Priority order:
    1. config/overrides.yaml exact match (highest priority — verified ground truth)
    2. Specific category match from metadata.category
    3. Specific category match from folder name
    4. Broad category match from metadata.category
    5. Broad category match from folder name
    6. Other (fallback)
    """
    # 1. Check manual overrides (ground truth)
    if overrides and folder_path.name in overrides:
        return overrides[folder_path.name], "override"

    # Evaluate matches from metadata and folder name
    meta_raw = extract_metadata_category(folder_path)
    meta_match = get_best_match(meta_raw, categories) if meta_raw else None
    folder_match = get_best_match(folder_path.name, categories)

    # 2. Specific metadata match
    if meta_match and meta_match["is_specific"]:
        return meta_match["category"], "metadata"

    # 3. Specific folder name match
    if folder_match and folder_match["is_specific"]:
        return folder_match["category"], "keyword"

    # 4. Broad metadata match
    if meta_match and meta_match["category"] != "Other":
        return meta_match["category"], "metadata"

    # 5. Broad folder name match
    if folder_match and folder_match["category"] != "Other":
        return folder_match["category"], "keyword"

    # 6. Fall back to Other if unmatched
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
