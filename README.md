# BioScript Assay Classifier

[![Tests](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml/badge.svg)](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated classification and statistics generation tool for BioScript protocol datasets.

## Overview

In biological laboratory automation and domain-specific language research (such as BioScript), datasets frequently consist of hundreds of diverse protocol directories containing assay definitions, execution logs, and configuration manifests.

**BioScript Assay Classifier** parses and categorizes protocol directories into standardized assay categories (e.g., ELISA, PCR, Immunoprecipitation, Cell-based assays, Microfluidic fabrication). It produces statistical summaries and granular audit trails with provenance tracking to quantify dataset distribution and research domain coverage.

### Classification Strategy & Priority

The classifier executes a strict 4-tier decision hierarchy:
1. **Manual Overrides (`source: override`)**: Exact folder match against [`config/overrides.yaml`](config/overrides.yaml). Takes highest priority as human-verified ground truth.
2. **Metadata Manifest (`source: metadata`)**: If a protocol directory contains a `.json` manifest with a `metadata.category` field, that category is normalized to canonical categories.
3. **Keyword Matching (`source: keyword`)**: Substring matching against keyword rules configured in [`config/categories.yaml`](config/categories.yaml). If a folder name matches keywords in multiple categories, the **first match in file order** is assigned.
4. **Fallback (`source: unmatched`)**: Any protocol folder that does not match an override, metadata entry, or keyword rule is assigned to the `Other` category.

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
│   ├── categories.yaml           # Externalized category & keyword rules
│   └── overrides.yaml            # Verified ground-truth folder overrides
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
| `--overrides` | `PATH` | `config/overrides.yaml` | Path to manual overrides YAML |
| `-o`, `--output-dir` | `PATH` | `output` | Directory where CSV reports will be saved |
| `-v`, `--verbose` | | `False` | Print real-time classification per folder |

### Example

```bash
python src/classify.py "C:\Users\sayan\OpenBioSet\Dataset" --verbose --output-dir output/
```

**Console Output:**
```
Found 180 protocol folder(s) in 'C:\Users\sayan\OpenBioSet\Dataset'.
  Heroin -> ELISA_Immunoassay [override]
  Zika_PCR_Detection -> PCR_NucleicAcid [metadata]
  Caspase3_Apoptosis -> Cell_Based_Assay [keyword]
  Exact2_TCA_Incubate -> Other [unmatched]

Classification complete.
Exported summary to:     output/summary.csv
Exported audit trail to: output/audit_trail.csv
```

---

## Category Configuration

Category rules and precedence are configured in [`config/categories.yaml`](config/categories.yaml). The classifier evaluates categories in the order they are defined:

1. `ELISA_Immunoassay`
2. `Immunoprecipitation`
3. `PCR_NucleicAcid`
4. `Extraction_Purification`
5. `Cell_Based_Assay`
6. `Small_Molecule_Drug`
7. `Omics_Proteomics`
8. `Aerosol_Environmental`
9. `Dilution`
10. `Phytochemical_Colorimetric_Assay`
11. `Clinical_Diagnostics_Newborn_Screening`
12. `Enzyme_Kinetics_Screening`
13. `Synthetic_Biology_Genetic_Engineering`
14. `Oncology_Cell_Pathology`
15. `Device_Fabrication_Protocol_Formalization`
16. `RNA_Sequencing_Epigenomics`
17. `Chemistry_Synthesis_Purification_MS`
18. `Other`

Ground-truth manual overrides are configured in [`config/overrides.yaml`](config/overrides.yaml):
```yaml
ahmadi_2024_mab_discovery: Cell_Based_Assay
deng2025_d2_droplet_digital_recovery: Cell_Based_Assay
Heroin: ELISA_Immunoassay
```

---

## Output CSV Formats

### 1. `output/summary.csv`
Summary statistics of all 18 categories across the dataset:
```csv
category,count,percent
Cell_Based_Assay,37,20.56%
PCR_NucleicAcid,26,14.44%
ELISA_Immunoassay,20,11.11%
...
Other,9,5.00%
```

### 2. `output/audit_trail.csv`
Per-folder classification audit log with provenance tracking:
```csv
folder_name,category,source
ahmadi_2024_mab_discovery,Cell_Based_Assay,override
Aerosol_ion_detection,Aerosol_Environmental,metadata
abasiyanik2021_sars_cov2_saliva_detection,Clinical_Diagnostics_Newborn_Screening,keyword
Exact2_TCA_Incubate,Other,unmatched
```

---

## Results & Methodology

### Dataset Classification Breakdown

*Classification distribution across the 180-folder BioScript dataset (18 total categories):*

| Category | Count | Percentage |
|---|---|---|
| **Cell_Based_Assay** | 37 | 20.56% |
| **PCR_NucleicAcid** | 26 | 14.44% |
| **ELISA_Immunoassay** | 20 | 11.11% |
| **Extraction_Purification** | 13 | 7.22% |
| **Chemistry_Synthesis_Purification_MS** | 12 | 6.67% |
| **Device_Fabrication_Protocol_Formalization** | 11 | 6.11% |
| **Phytochemical_Colorimetric_Assay** | 8 | 4.44% |
| **Clinical_Diagnostics_Newborn_Screening** | 8 | 4.44% |
| **Synthetic_Biology_Genetic_Engineering** | 7 | 3.89% |
| **Small_Molecule_Drug** | 6 | 3.33% |
| **Omics_Proteomics** | 6 | 3.33% |
| **Enzyme_Kinetics_Screening** | 4 | 2.22% |
| **Oncology_Cell_Pathology** | 4 | 2.22% |
| **RNA_Sequencing_Epigenomics** | 4 | 2.22% |
| **Immunoprecipitation** | 2 | 1.11% |
| **Aerosol_Environmental** | 2 | 1.11% |
| **Dilution** | 1 | 0.56% |
| **Other** | 9 | 5.00% |
| **Total** | **180** | **100.00%** |

### Classification Provenance Breakdown
- **Keyword Matching (`keyword`)**: 140 / 180 (77.78%)
- **Metadata Manifest (`metadata`)**: 28 / 180 (15.56%)
- **Manual Override (`override`)**: 3 / 180 (1.67%)
- **Unmatched Residual (`unmatched`)**: 9 / 180 (5.00%)

### Residual "Other" Category (5.00%)
The "Other" bucket was reduced from 69/180 (38.33%) down to 9/180 (5.00%). Rather than artificially forcing ambiguous protocols into ill-fitting buckets, these 9 folders remain cleanly isolated for transparent review:
1. `Ahmadi_ML_DMF_18FFDG_ofat`
2. `Exact2_TCA_Incubate`
3. `FDG_Radiosynthesis_ofat`
4. `fobel_paper_dmf_digital_microfluidics`
5. `hou_margination_pathogen_removal_blood`
6. `Peptidisc_MSBA`
7. `Shih_Algae_Lipid_DMF_Screen`
8. `Shih_DBS_DMF_Nesi_MS`
9. `watterson_anaerobic_droplet_cultivation`

### Validation Methodology & Accuracy

Manual validation on a random N=18 sample (10%) found the automated classifier (metadata + keyword rules only, before any manual overrides) correct in 13/18 cases (72.2% agreement). The 3 confirmed errors found during this review (`ahmadi_2024_mab_discovery`, `deng2025_d2_droplet_digital_recovery`, `Heroin`) were added to `config/overrides.yaml` as verified corrections; overrides account for 3/180 (1.7%) of final category assignments. The 72.2% figure, not a post-override number, represents the automated classifier's true accuracy.

---

## Running Tests

Run the test suite with pytest:

```bash
pytest -v
```

---

## License

This project is licensed under the [MIT License](LICENSE).
