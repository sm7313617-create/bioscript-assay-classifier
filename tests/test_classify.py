import csv
from pathlib import Path
import pytest
from src.classify import (
    load_categories,
    classify_folder,
    extract_metadata_category,
    enumerate_folders,
    export_results,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "categories.yaml"


@pytest.fixture
def categories():
    return load_categories(CONFIG_FILE)


def test_load_categories(categories):
    assert "ELISA_Immunoassay" in categories
    assert "PCR_NucleicAcid" in categories
    assert "Other" in categories
    assert "elisa" in categories["ELISA_Immunoassay"]


def test_classify_elisa_keyword(categories):
    elisa_folder = FIXTURES_DIR / "ELISA_example"
    category, source = classify_folder(elisa_folder, categories)
    assert category == "ELISA_Immunoassay"
    assert source == "keyword"


def test_classify_pcr_metadata(categories):
    pcr_folder = FIXTURES_DIR / "PCR_example"
    category, source = classify_folder(pcr_folder, categories)
    assert category == "PCR_NucleicAcid"
    assert source == "metadata"


def test_classify_other_unmatched(categories):
    other_folder = FIXTURES_DIR / "Other_example"
    category, source = classify_folder(other_folder, categories)
    assert category == "Other"
    assert source == "unmatched"


def test_enumerate_fixtures():
    folders = enumerate_folders(FIXTURES_DIR)
    folder_names = {f.name for f in folders}
    assert "ELISA_example" in folder_names
    assert "PCR_example" in folder_names
    assert "Other_example" in folder_names


def test_export_results(tmp_path, categories):
    records = [
        {"folder_name": "ELISA_example", "category": "ELISA_Immunoassay", "source": "keyword"},
        {"folder_name": "PCR_example", "category": "PCR_NucleicAcid", "source": "metadata"},
        {"folder_name": "Other_example", "category": "Other", "source": "unmatched"},
    ]
    summary_file, audit_file = export_results(records, output_dir=tmp_path, categories=categories)

    assert summary_file.exists()
    assert audit_file.exists()

    with open(audit_file, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["folder_name", "category", "source"]
        assert len(reader) == 4

    with open(summary_file, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["category", "count", "percent"]
