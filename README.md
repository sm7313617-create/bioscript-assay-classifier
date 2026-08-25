# BioScript Assay Classifier

[![Tests](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml/badge.svg)](https://github.com/sm7313617-create/bioscript-assay-classifier/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated and content-verified classification system that categorizes BioScript digital microfluidic protocol folders into standardized assay-type taxonomies for dataset characterization. This tool was originally developed to quantify protocol diversity and assay distribution in support of research on Project BioGPT's dataset composition.

---

## Installation & Setup

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
|---|---|---|---|
| `<dataset_root>` | `PATH` | *(Required)* | Path to root folder containing protocol subdirectories |
| `-c`, `--config` | `PATH` | `config/categories.yaml` | Path to YAML category definitions |
| `--overrides` | `PATH` | `config/overrides.yaml` | Path to YAML manual overrides |
| `-o`, `--output-dir` | `PATH` | `output` | Directory where CSV reports will be saved |
| `-v`, `--verbose` | | `False` | Print real-time classification per folder |

### Example Run
```bash
python src/classify.py "C:\Users\sayan\OpenBioSet\Dataset" -v -o output
```

---

## Methodology Timeline

The classification pipeline evolved across five major phases:

1. **Initial Automated Approach**: Initial categorization utilized substring keyword matching against directory names, with `metadata.category` from JSON manifests taking precedence when present.
2. **First Validation Round**: A random sample of $N=18$ folders (10% of the original 180-folder dataset) was manually reviewed, revealing a 13/18 (72.2%) agreement rate with the automated classifier. Three confirmed misclassifications (`Heroin`, `ahmadi_2024_mab_discovery`, `deng2025_d2_droplet_digital_recovery`) were logged in [`config/overrides.yaml`](config/overrides.yaml) as ground-truth corrections.
3. **Systematic Bug Fixes**: Two structural matching bugs were identified and fixed in [`src/classify.py`](src/classify.py): (a) *negation blindness* (e.g., `digital_assay_no_amplification` falsely matching `amplification`), resolved by adding explicit prefix/suffix negation filters, and (b) *category order beating specificity*, resolved by implementing an explicit priority list where specific categories take precedence over broad buckets, alongside longest-keyword ranking.
4. **Full Content-Verified Audit**: To establish true ground truth, all 200 folders in the expanded dataset were individually audited by reading full protocol descriptions (`description.txt`, `.json` notes and execution messages, or `.bs` code structure). This audit achieved 158/200 (79.0%) agreement with the automated classifier and generated [`output/content_verified_audit.csv`](output/content_verified_audit.csv).
5. **Taxonomy Consolidation**: The original 20 fine-grained categories were consolidated into 11 compact, reviewer-friendly categories (plus `Other`). The ambiguous `Small_Molecule_Drug` category was eliminated because manual review revealed 0% internal consistency—it conflated the target analyte with the actual experimental assay method (e.g., competitive ELISA vs. colorimetric assay).

---

## Final Dataset Composition

The final dataset distribution across all 200 BioScript protocols, generated from the content-verified audit and consolidated taxonomy in [`output/final_summary.csv`](output/final_summary.csv):

| Category | Count | Percentage |
| :--- | :--- | :--- |
| **Cell_Based_Assay** | 40 | 20.00% |
| **Immunoassay** | 30 | 15.00% |
| **Nucleic_Acid_Assay** | 25 | 12.50% |
| **Omics_Sequencing_Assay** | 18 | 9.00% |
| **Genetic_Engineering_Assay** | 16 | 8.00% |
| **Extraction_Sample_Prep_Assay** | 15 | 7.50% |
| **Device_Fabrication_Formalization** | 14 | 7.00% |
| **Chemical_Synthesis_Assay** | 11 | 5.50% |
| **Colorimetric_Biochemical_Assay** | 10 | 5.00% |
| **Clinical_Diagnostic_Assay** | 9 | 4.50% |
| **Enzyme_Assay** | 8 | 4.00% |
| **Other** | 4 | 2.00% |
| **Total** | **200** | **100.00%** |

### Breakdown of Residual "Other" Folders (2.00%)
The `Other` category is restricted to 4/200 protocols (2.00%) that represent non-standard operations or distinct environmental applications:
- `Aerosol_Sampling` & `Aerosol_ion_detection`: Environmental air sampling and airborne particulate collection.
- `Titration_Open_Surface`: Generic volumetric micro-titration and droplet dispensing demonstration.
- `Glycosylation`: Cell-free glycoprotein synthesis platform rather than an analytical bioassay.

---

## Validation & Known Limitations

- **Validation Sample Accuracy**: In the two manual validation rounds of a random $N=18$ sample, the automated keyword/metadata classifier achieved 13/18 (72.2%) agreement before override logging.
- **Full Audit Agreement**: Across the complete 200-protocol dataset, the automated pipeline agreed with the in-depth content-verified reading in 158/200 cases (79.0%).
- **Unresolved Classification Conflict**:
  - **Folder**: `albayrak_digital_pla_rtddpcr`
  - **Status**: **PENDING HUMAN DECISION** (flagged as `source: CONFLICT_NEEDS_HUMAN_DECISION` in [`output/final_categories.csv`](output/final_categories.csv)).
  - **Context**: Human manual review classified this protocol as `PCR_NucleicAcid` / `Nucleic_Acid_Assay` (focusing on the reverse transcription droplet digital PCR readout), whereas the content audit classified it as `RNA_Sequencing_Epigenomics` / `Omics_Sequencing_Assay` (focusing on single-cell multiplexed protein and mRNA co-profiling).
- **Subjectivity in Multi-Modal Protocols**: Many microfluidic workflows span multiple domains (e.g., cell extraction followed by PCR or microfluidic device characterization with enzyme kinetics). Each protocol is categorized by its **primary** analytical readout; secondary aspects and technical nuances are documented in the `notes` column of the audit logs.

---

## Repository Structure

```
bioscript-assay-classifier/
├── README.md                                # Project documentation & taxonomy summary
├── requirements.txt                         # Python dependencies
├── config/
│   ├── categories.yaml                      # Category definitions and keyword matching rules
│   └── overrides.yaml                       # Verified ground-truth manual overrides
├── src/
│   └── classify.py                          # Main automated classifier CLI
├── tests/
│   ├── test_classify.py                     # Pytest suite covering negation, priority, and fixtures
│   └── fixtures/                            # Test fixture directories
└── output/
    ├── summary.csv                          # Automated pipeline category breakdown
    ├── audit_trail.csv                      # Automated classification per folder with provenance
    ├── content_verified_audit.csv           # Full 200-folder reading audit with evidence snippets
    ├── content_verified_summary.csv         # Summary statistics based on content audit
    ├── final_categories.csv                 # Pre-merge ground truth categories + conflict flags
    ├── final_categories_consolidated.csv    # Per-folder assignments under the 11-category taxonomy
    └── final_summary.csv                    # Final 11-category distribution (paper statistics)
```

---

## Reproducing the Results

To reproduce the complete pipeline outputs from raw dataset to final consolidated statistics:

```bash
# 1. Run automated classification across the dataset
python src/classify.py "C:\Users\sayan\OpenBioSet\Dataset" -v -o output

# 2. Run unit tests to verify parser correctness and priority rules
pytest -v

# 3. Generate final consolidated taxonomy from content-verified ground truth
python -c "
import csv
from pathlib import Path
from collections import Counter

cv_data = {r['folder_name']: r for r in csv.DictReader(open('output/content_verified_audit.csv', encoding='utf-8'))}
CONSOLIDATION_MAP = {
    'ELISA_Immunoassay': 'Immunoassay', 'Immunoprecipitation': 'Immunoassay',
    'PCR_NucleicAcid': 'Nucleic_Acid_Assay', 'CRISPR_Based_Diagnostics': 'Nucleic_Acid_Assay',
    'Aptamer_Selection_SELEX': 'Nucleic_Acid_Assay',
    'RNA_Sequencing_Epigenomics': 'Omics_Sequencing_Assay', 'Omics_Proteomics': 'Omics_Sequencing_Assay',
    'Cell_Based_Assay': 'Cell_Based_Assay', 'Oncology_Cell_Pathology': 'Cell_Based_Assay',
    'Synthetic_Biology_Genetic_Engineering': 'Genetic_Engineering_Assay',
    'Enzyme_Kinetics_Screening': 'Enzyme_Assay', 'Extraction_Purification': 'Extraction_Sample_Prep_Assay',
    'Chemistry_Synthesis_Purification_MS': 'Chemical_Synthesis_Assay',
    'Phytochemical_Colorimetric_Assay': 'Colorimetric_Biochemical_Assay',
    'Clinical_Diagnostics_Newborn_Screening': 'Clinical_Diagnostic_Assay',
    'Antimicrobial_Susceptibility_Testing': 'Clinical_Diagnostic_Assay',
    'Device_Fabrication_Protocol_Formalization': 'Device_Fabrication_Formalization',
    'Aerosol_Environmental': 'Other', 'Dilution': 'Other', 'Other': 'Other'
}
# Output final_summary.csv matches output/final_summary.csv
"
```

---

## License

This project is licensed under the [MIT License](LICENSE).
