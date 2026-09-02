# Initial rule-based classification

The initial classification stage operates on OCR text extracted from each
segment of the screen-recording corpus.

The purpose of this stage is to identify a small set of digital environments
defined a priori before the subsequent taxonomy-refinement procedure.

## Initial categories

The initial classifier distinguishes four explicit environments:

- Quinan
- Google
- ChatGPT
- GeoGebra

Segments for which none of these environments can be identified from the OCR
evidence are assigned to the residual category:

- Otro sitio

The corresponding configuration is stored in:

`config/sites_initial.yaml`

## Classification rules

The classifier is implemented in:

`src/classifier.py`

The classification engine is independent of the category definitions. The
categories, lexical patterns, residual category, scoring parameters, and tie
priority are provided through the external YAML configuration.

For the initial classification, the relevant lexical evidence is:

| Category | OCR patterns |
|---|---|
| Quinan | `quinan`, `aulavirtual` |
| Google | `google` |
| ChatGPT | `chatgpt` |
| GeoGebra | `geogebra` |
| Otro sitio | residual category |

OCR text is normalized before classification. The classifier counts the
occurrences of the configured patterns and accumulates the corresponding
evidence score for each category.

The category with the highest score is assigned to the segment.

If no category reaches the minimum classification score, the segment is
assigned to `Otro sitio`.

In the event of equal scores, the order of the categories in the YAML file is
used as the priority rule:

1. Quinan
2. Google
3. ChatGPT
4. GeoGebra
5. Otro sitio

## Initial classification output

Applying the initial configuration to the 18,829 segments produced the
following distribution:

| Initial category | Segments | Percentage |
|---|---:|---:|
| Quinan | 13,161 | 69.90% |
| Otro sitio | 4,345 | 23.08% |
| Google | 840 | 4.46% |
| ChatGPT | 250 | 1.33% |
| GeoGebra | 233 | 1.24% |
| **Total** | **18,829** | **100.00%** |

The relatively large residual group, representing approximately one quarter
of the corpus, motivated the subsequent taxonomy-refinement stage.

The machine-readable summary is available at:

`data/processed/initial_classification_summary.csv`

## Position in the analytical workflow

The initial stage is part of the following sequence:

OCR extraction
→ Initial rule-based classification
→ Five-category initial representation
→ Taxonomy refinement
→ Temporal-context resolution
→ Expert review of residual episodes
→ Final nine-category classification

The initial classifier therefore provides the first structured representation
of the OCR evidence, while the subsequent stages refine that representation
using additional lexical, contextual, temporal, and expert evidence.
