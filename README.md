# Screen Recording Learning Analytics

Reproducible pipeline and public dataset for analysing visible digital environments in screen-recording data.

The repository accompanies a research workflow in which screen recordings were transformed into temporally segmented observations, processed with OCR, classified according to visible digital environments, and subsequently refined through automated, temporal, and manual procedures.

## Final public corpus

The public dataset contains:

- **100 screen-recording videos**
- **18,829 temporal segments**
- **9 final categories**
- segment-level temporal information
- anonymized video identifiers
- final classification labels

The public dataset is available at:

```text
data/processed/corpus_100_videos_public_final.csv
```

The nine final categories are:

1. Quinan
2. Google
3. Google (Mat)
4. GeoGebra
5. Wikipedia
6. YouTube
7. Juegos
8. Screen Recorder
9. Otro sitio

`Otro sitio` is retained as a residual category for digital environments that could not be assigned to one of the eight explicitly identified environments.

## Public dataset variables

The public CSV contains the following variables:

| Variable | Description |
|---|---|
| `video_id` | Anonymized video identifier |
| `start_time_s` | Segment start time in seconds |
| `end_time_s` | Segment end time in seconds |
| `duration_s` | Segment duration in seconds |
| `category` | Final digital-environment category |
| `classification_method` | Automatic, temporal, or expert-review method that produced the final label |
| `ocr_mode` | OCR mode retained during reprocessing |
| `temporal_interpolation` | Whether the final label was assigned through the temporal rule |
| `manual_review` | Whether the final label was assigned through expert episode review |

No participant names, email addresses, credentials, original recordings, or private file-system paths are included in the public dataset.

## Workflow

The complete analytical process can be summarized as:

```text
screen recordings
    ↓
video normalization
    ↓
1-second frame sampling
    ↓
SSIM-based screen-change detection
    ↓
representative screenshots
    ↓
Tesseract OCR
    ↓
initial rule-based classification
    ↓
OCR reprocessing
    ↓
historical `palabra_base` plus updated-OCR refinement evidence
    ↓
temporal-context refinement
    ↓
manual review of unresolved episodes
    ↓
final 9-category classification
    ↓
public anonymized dataset
```

The repository contains cleaned implementations of the main computational stages. Historical working notebooks and raw research materials are intentionally not distributed.

## Repository structure

```text
.
├── config/
│   └── sites.yaml
├── data/
│   └── processed/
│       ├── corpus_100_videos_public_final.csv
│       ├── refinement_input_public.csv
│       └── manual_review_decisions_public.csv
├── docs/
├── src/
│   ├── classifier.py
│   ├── config.py
│   ├── export_public_dataset.py
│   ├── extraction.py
│   ├── merge_excels.py
│   ├── pipeline.py
│   ├── refine_classification.py
│   ├── reporting.py
│   ├── reprocess_ocr.py
│   ├── reproduce_final_classification.py
│   └── text_utils.py
├── tests/
├── requirements.txt
└── pyproject.toml
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The extraction and OCR stages additionally require system installations of:

- **FFmpeg**
- **Tesseract OCR**
- Spanish Tesseract language data (`spa`) when reproducing the default OCR configuration

## Screen extraction

The extraction pipeline implements screen sampling and screen-change detection using structural similarity (SSIM).

The historical analytical configuration used:

```text
frame step: 1 second
SSIM threshold: 0.90
OCR language: spa
```

The cleaned pipeline can be invoked through:

```bash
python -m src.pipeline extract
```

Raw screen recordings are not included in this repository.

## OCR reprocessing

A second OCR pass was used during refinement of the historical corpus.

The reproducible implementation is:

```text
src/reprocess_ocr.py
```

It uses Tesseract with:

```text
PSM 6
```

as the primary OCR mode and:

```text
PSM 11
```

as a fallback when the first pass produces little text.

The script does not contain local or researcher-specific paths. Required source files are supplied explicitly:

```bash
python -m src.reprocess_ocr \
  --master /path/to/master.xlsx \
  --zip-first /path/to/first_group.zip \
  --zip-second /path/to/second_group.zip \
  --zip-third /path/to/third_group.zip \
  --output /path/to/output.xlsx
```

The original recordings, screenshot archives, intermediate spreadsheets, and OCR checkpoints are not distributed because they belong to the private research corpus.

## Classification

Classification rules are separated from the executable code and stored in:

```text
config/sites.yaml
```

This separation makes the classification logic auditable and allows the rule set to be inspected independently of the Python implementation.

Both the base classifier and the reproducible refinement engine are configuration-driven. Study-specific category names, textual evidence, derived-category definitions, historical mappings, and residual-refinement rules are declared in YAML rather than hard-coded in the Python modules. Researchers adapting the pipeline to another context can therefore modify the configuration without editing the classification or refinement source code.

The pipeline distinguishes explicit digital environments from the residual `Otro sitio` category.

## Classification refinement

The final labels should not be interpreted as the direct output of a single keyword classifier.

The historical corpus underwent successive refinement stages:

1. initial OCR-based classification;
2. reprocessing of OCR evidence;
3. refinement of candidate digital environments;
4. use of temporal context for short ambiguous episodes;
5. manual review of remaining unresolved episodes.

These stages produced the final nine-category classification represented by the `category` variable in the public dataset.

The final labels were constructed from the historical `palabra_base` classification and the uniformly reprocessed OCR evidence. `palabra_base` is the original five-category automated label generated from the first OCR pass; it is an actual computational input to refinement, not an unused metadata field. Updated OCR was then used to subdivide historical Google rows and to seek stronger evidence within historical residual rows.

The five-category output in `data/processed/initial_classification_summary.csv` was reconstructed later by applying `config/sites_initial.yaml` to the updated OCR. It documents how the current initial classifier behaves on the reprocessed text, but it was not the upstream label column used to create the authoritative final classification.

Raw OCR text and screenshots cannot be distributed. For exact public downstream reproduction, `data/processed/refinement_input_public.csv` retains the anonymized segment times, historical `palabra_base`, OCR mode, and category-level Boolean evidence derived from the restricted OCR. It contains no OCR text, screenshot path, participant identity, or local path. Expert episode decisions are provided separately in `data/processed/manual_review_decisions_public.csv` without review notes or private paths.

Run the complete privacy-safe downstream reproduction and verify it against the authoritative final dataset:

```bash
python -m src.reproduce_final_classification \
  --output /tmp/corpus_100_videos_reproduced.csv
```

The command must report 18,829/18,829 agreement for labels, methods, and temporal/manual flags, together with 1,482 transitions and 307,976.40 seconds.

## Human validation

The definitive second-round validation included 450 screenshots, with 50 sampled from each final category. Two evaluators independently assigned categories while blind to the pipeline labels and to each other's responses. The privacy-safe labels used for analysis are in `data/processed/human_validation_annotations.csv`; `src/evaluate_human_validation.py` reproduces the global metrics, per-category metrics, and confusion matrices.

The evaluators agreed on 424 of 450 screenshots (94.22%; Cohen's kappa 0.9338). The raw workbook is not part of the public package because it contains unnecessary response timestamps. See `validation/README.md` for the authoritative-source and privacy boundary.

## Reproducibility and privacy

This repository is designed to separate reproducible analytical logic from restricted research material.

### Public

- cleaned Python source code;
- classification configuration;
- documentation;
- anonymized final segment-level dataset;
- privacy-safe refinement evidence and expert episode decisions;
- privacy-safe human-validation annotations and derived metrics.

### Not distributed

- original screen recordings;
- original screenshots;
- participant-identifying information;
- private intermediate datasets;
- manual-review working files;
- evaluator credentials;
- raw human-validation workbooks and response timestamps;
- local file-system paths.

This separation allows the analytical procedure and final anonymized data structure to be inspected without exposing the original research recordings.

## Testing

Tests can be run with:

```bash
pytest
```

Pytest configuration is defined in `pyproject.toml`.

## Citation

Citation information for the associated article and archived dataset will be added when the corresponding publication and repository records are available.
