import os
import sys
from pathlib import Path


def enumerate_folders(dataset_root: str) -> list[Path]:
    """Walk immediate subfolders of the dataset root directory."""
    root_path = Path(dataset_root)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Error: Directory '{dataset_root}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    folders = [item for item in root_path.iterdir() if item.is_dir()]
    return folders


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/classify.py <dataset_root>")
        sys.exit(1)

    dataset_root = sys.argv[1]
    folders = enumerate_folders(dataset_root)
    print(f"Found {len(folders)} protocol folder(s) in '{dataset_root}'.")


if __name__ == "__main__":
    main()
