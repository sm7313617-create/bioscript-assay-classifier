import csv
from pathlib import Path
import pytest
from src.classify import (
    load_categories,
    load_overrides,
    classify_folder,
    extract_metadata_category,
    normalize_category,
    enumerate_folders,
    export_results,
    parse_args,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "categories.yaml"
OVERRIDES_FILE = Path(__file__).parent.parent / "config" / "overrides.yaml"


@pytest.fixture
def categories():
    return load_categories(CONFIG_FILE)


@pytest.fixture
def overrides():
    return load_overrides(OVERRIDES_FILE)


def test_load_categories(categories):
    assert "ELISA_Immunoassay" in categories
    assert "PCR_NucleicAcid" in categories
    assert "Cell_Based_Assay" in categories
    assert "Phytochemical_Colorimetric_Assay" in categories
    assert "Clinical_Diagnostics_Newborn_Screening" in categories
    assert "Enzyme_Kinetics_Screening" in categories
    assert "Synthetic_Biology_Genetic_Engineering" in categories
    assert "Oncology_Cell_Pathology" in categories
    assert "Device_Fabrication_Protocol_Formalization" in categories
    assert "RNA_Sequencing_Epigenomics" in categories
    assert "Chemistry_Synthesis_Purification_MS" in categories
    assert "Aptamer_Selection_SELEX" in categories
    assert "Antimicrobial_Susceptibility_Testing" in categories
    assert "CRISPR_Based_Diagnostics" in categories
    assert "Other" in categories
    assert "elisa" in categories["ELISA_Immunoassay"]
    assert "selex" in categories["Aptamer_Selection_SELEX"]
    assert "mic_screen" in categories["Antimicrobial_Susceptibility_Testing"]
    assert "cas13" in categories["CRISPR_Based_Diagnostics"]


def test_load_overrides(overrides):
    assert overrides.get("Heroin") == "ELISA_Immunoassay"
    assert overrides.get("ahmadi_2024_mab_discovery") == "Cell_Based_Assay"
    assert overrides.get("deng2025_d2_droplet_digital_recovery") == "Cell_Based_Assay"


def test_normalize_category(categories):
    assert normalize_category("pcr_amplification_assay", categories) == "PCR_NucleicAcid"
    assert normalize_category("single_cell_signalling_assay", categories) == "Cell_Based_Assay"
    assert normalize_category("microproteomics_sample_preparation", categories) == "Omics_Proteomics"
    assert normalize_category("flavonoid_content_analysis", categories) == "Phytochemical_Colorimetric_Assay"
    assert normalize_category("aptamer_selection_assay", categories) == "Aptamer_Selection_SELEX"
    assert normalize_category("antibiotic_mic_test", categories) == "Antimicrobial_Susceptibility_Testing"
    assert normalize_category("crispr_diagnostic_detection", categories) == "CRISPR_Based_Diagnostics"
    assert normalize_category("completely_random_xyz", categories) is None


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


def test_classify_selex_keyword(categories):
    folder = FIXTURES_DIR / "SELEX_example"
    category, source = classify_folder(folder, categories)
    assert category == "Aptamer_Selection_SELEX"
    assert source == "keyword"


def test_classify_ast_keyword(categories):
    folder = FIXTURES_DIR / "Antibiotic_MIC_example"
    category, source = classify_folder(folder, categories)
    assert category == "Antimicrobial_Susceptibility_Testing"
    assert source == "keyword"


def test_classify_crispr_keyword(categories):
    folder = FIXTURES_DIR / "CRISPR_example"
    category, source = classify_folder(folder, categories)
    assert category == "CRISPR_Based_Diagnostics"
    assert source == "keyword"


def test_classify_override(categories):
    pcr_folder = FIXTURES_DIR / "PCR_example"
    mock_overrides = {"PCR_example": "Custom_Override_Category"}
    category, source = classify_folder(pcr_folder, categories, overrides=mock_overrides)
    assert category == "Custom_Override_Category"
    assert source == "override"


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
    assert "SELEX_example" in folder_names
    assert "Antibiotic_MIC_example" in folder_names
    assert "CRISPR_example" in folder_names


def test_export_results(tmp_path, categories):
    records = [
        {"folder_name": "ELISA_example", "category": "ELISA_Immunoassay", "source": "keyword"},
        {"folder_name": "PCR_example", "category": "PCR_NucleicAcid", "source": "metadata"},
        {"folder_name": "Override_example", "category": "Cell_Based_Assay", "source": "override"},
        {"folder_name": "Other_example", "category": "Other", "source": "unmatched"},
    ]
    summary_file, audit_file = export_results(records, output_dir=tmp_path, categories=categories)

    assert summary_file.exists()
    assert audit_file.exists()

    with open(audit_file, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["folder_name", "category", "source"]
        assert len(reader) == 5

    with open(summary_file, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["category", "count", "percent"]


def test_parse_args():
    args = parse_args(["my_dataset", "-c", "custom.yaml", "--overrides", "custom_ov.yaml", "-o", "custom_out", "-v"])
    assert args.dataset_root == "my_dataset"
    assert args.config == "custom.yaml"
    assert args.overrides == "custom_ov.yaml"
    assert args.output_dir == "custom_out"
    assert args.verbose is True
