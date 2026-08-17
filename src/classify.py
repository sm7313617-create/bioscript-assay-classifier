import os
import sys
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


def classify_by_keyword(folder_name: str, categories: dict[str, list[str]]) -> str:
    """Classify folder by case-insensitive substring match against keyword lists."""
    folder_lower = folder_name.lower()
    for category, keywords in categories.items():
        if not keywords:
            continue
        for keyword in keywords:
            if keyword.lower() in folder_lower:
                return category
    return "Other"


def enumerate_folders(dataset_root: str | Path) -> list[Path]:
    """Walk immediate subfolders of the dataset root directory."""
    root_path = Path(dataset_root)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Error: Directory '{dataset_root}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    folders = [item for item in root_path.iterdir() if item.is_dir()]
    return folders


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/classify.py <dataset_root> [config_path]")
        sys.exit(1)

    dataset_root = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "config/categories.yaml"

    categories = load_categories(config_path)
    folders = enumerate_folders(dataset_root)

    print(f"Found {len(folders)} protocol folder(s) in '{dataset_root}'.")
    for folder in folders:
        category = classify_by_keyword(folder.name, categories)
        print(f"  {folder.name} -> {category}")


if __name__ == "__main__":
    main()
