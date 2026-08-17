import csv
import random
from pathlib import Path


def build_validation_sample(
    audit_trail_path: str | Path = "output/audit_trail.csv",
    output_sample_path: str | Path = "output/validation_sample.csv",
    sample_size: int = 18,
    seed: int = 42,
) -> Path:
    """Select a reproducible random sample of rows from the audit trail for manual review."""
    audit_file = Path(audit_trail_path)
    output_file = Path(output_sample_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(audit_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    random.seed(seed)
    sampled_rows = random.sample(reader, min(sample_size, len(reader)))

    fieldnames = [
        "folder_name",
        "assigned_category",
        "classification_source",
        "correct_yn",
        "correct_category_if_wrong",
        "notes",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for row in sampled_rows:
            writer.writerow([
                row["folder_name"],
                row["category"],
                row["source"],
                "",  # correct_yn
                "",  # correct_category_if_wrong
                "",  # notes
            ])

    return output_file


def main():
    output_path = build_validation_sample()
    print(f"Generated validation sample of 18 records at: {output_path}")


if __name__ == "__main__":
    main()
