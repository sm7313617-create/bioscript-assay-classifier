# BioScript Assay Classifier

[![Tests](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml/badge.svg)](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated classification and statistics generation tool for BioScript protocol datasets.

## Overview

In biological laboratory automation and domain-specific language research (such as BioScript), datasets frequently consist of hundreds of diverse protocol directories containing assay definitions, execution logs, and configuration manifests.

**BioScript Assay Classifier** parses and categorizes protocol directories into standardized assay categories (e.g., ELISA, PCR, Immunoprecipitation, Cell-based assays). It produces statistical summaries and granular audit trails to help quantify dataset distribution and research domain coverage.

### Classification Strategy
1. **Metadata First**: If a protocol directory contains a `.json` manifest with a `metadata.category` field, that category is assigned with `source: metadata`.
2. **Keyword Fallback**: If no metadata category exists, the folder name is matched (case-insensitively) against keyword rules configured in `config/categories.yaml` (`source: keyword`).
3. **Unmatched / Other**: Any folder that does not match metadata or keyword rules is assigned to the `Other` category (`source: unmatched`).

---

## Project Structure

```
bioscript-assay-classifier/
├── README.md
├── .gitignore
├── LICENSE
├── requirements.txt
├── src/
│   └── classify.py               # Main classification CLI script
├── config/
│   └── categories.yaml           # Externalized category & keyword rules
├── tests/
│   ├── __init__.py
│   ├── test_classify.py          # Pytest unit and integration tests
│   └── fixtures/                 # Test fixture protocol folders
├── .github/
│   └── workflows/
│       └── tests.yml             # GitHub Actions CI workflow
└── output/
    ├── summary.csv               # Aggregated statistics (% and counts)
    └── audit_trail.csv           # Per-folder classification audit log
```

---

## Installation

### Prerequisites
- Python 3.10+
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/sm7313617-create/bioscript-assay-classifier.git
cd bioscript-assay-classifier

# (Optional) Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Command Line Interface

```bash
python src/classify.py <dataset_root> [options]
```

### Options

| Flag | Argument | Default | Description |
|------|----------|---------|-------------|
| `<dataset_root>` | `PATH` | *(Required)* | Root directory containing protocol subfolders |
| `-c`, `--config` | `PATH` | `config/categories.yaml` | Path to category configuration YAML |
| `-o`, `--output-dir` | `PATH` | `output` | Directory where CSV reports will be saved |
| `-v`, `--verbose` | | `False` | Print real-time classification per folder |

### Example

```bash
python src/classify.py ../OpenBioSet/Dataset --verbose --output-dir output/
```

**Console Output:**
```
Found 180 protocol folder(s) in '../OpenBioSet/Dataset'.
  ELISA_Sandwich_Assay -> ELISA_Immunoassay [keyword]
  Zika_PCR_Detection -> PCR_NucleicAcid [metadata]
  Caspase3_Apoptosis -> Cell_Based_Assay [keyword]
  Custom_Synthetic_Mix -> Other [unmatched]

Classification complete.
Exported summary to:     output/summary.csv
Exported audit trail to: output/audit_trail.csv
```

---

## Category Configuration

Category rules are configured in [`config/categories.yaml`](config/categories.yaml):

```yaml
ELISA_Immunoassay:
  - elisa
  - immunoassay
  - tsh
  - hemagglutination
Immunoprecipitation:
  - immunoprecipitation
  - magnetic_particle
PCR_NucleicAcid:
  - pcr
  - nucleic_acid
  - zika
  - rubella
Extraction_Purification:
  - extraction
  - precipitation
  - monolith
Cell_Based_Assay:
  - cell_culture
  - apoptosis
  - caspase
Small_Molecule_Drug:
  - ciprofloxacin
  - fentanyl
  - glucose
  - estradiol
Omics_Proteomics:
  - omics
  - proteomic
  - oxidoreductase
Aerosol_Environmental:
  - aerosol
  - environmental
Dilution:
  - dilution
  - titration
Other: []
```

---

## Output CSV Formats

### 1. `output/summary.csv`
Summary statistics of all categories across the dataset:
```csv
category,count,percent
ELISA_Immunoassay,45,25.00%
PCR_NucleicAcid,38,21.11%
Cell_Based_Assay,28,15.56%
...
Other,12,6.67%
```

### 2. `output/audit_trail.csv`
Per-folder classification audit log with provenance tracking:
```csv
folder_name,category,source
ELISA_Sandwich_Assay,ELISA_Immunoassay,keyword
Zika_PCR_Detection,PCR_NucleicAcid,metadata
Custom_Synthetic_Mix,Other,unmatched
```

---

## Results (Dataset Statistics)

*Classification distribution across the 180-folder BioScript dataset:*

| Category | Count | Percentage |
|---|---|---|
| **Cell_Based_Assay** | 35 | 19.44% |
| **PCR_NucleicAcid** | 26 | 14.44% |
| **ELISA_Immunoassay** | 19 | 10.56% |
| **Extraction_Purification** | 13 | 7.22% |
| **Small_Molecule_Drug** | 7 | 3.89% |
| **Omics_Proteomics** | 6 | 3.33% |
| **Aerosol_Environmental** | 2 | 1.11% |
| **Immunoprecipitation** | 2 | 1.11% |
| **Dilution** | 1 | 0.56% |
| **Other** | 69 | 38.33% |
| **Total** | **180** | **100.0%** |

---

## Running Tests

Run the test suite with pytest:

```bash
pytest -v
```

---

## License

This project is licensed under the [MIT License](LICENSE).
