# Human validation metrics

## Purpose

This document reports the statistical analysis used to evaluate the
correspondence between the final nine-category classification and independent
human judgments.

The values reported here are generated automatically by:

`src/evaluate_human_validation.py`

using:

`data/processed/human_validation_annotations.csv`

The validation analysis contains three complementary comparisons:

1. agreement between the two independent evaluators (`EV01` vs `EV02`);
2. correspondence between the final pipeline classification and each evaluator;
3. correspondence between the final pipeline classification and the subset of
   images for which both evaluators independently assigned the same category.

---

## 1. Validation design

The validation sample contains 450 screenshots.

The sample was stratified according to the nine final pipeline categories, with
50 screenshots sampled from each category.

The final taxonomy comprises:

- Quinan
- Google
- Google (Mat)
- GeoGebra
- Wikipedia
- YouTube
- Juegos
- Screen Recorder
- Otro sitio

Two evaluators independently classified all screenshots while blinded to the
final pipeline labels and to each other's decisions.

---

## 2. Inter-rater reliability

The two evaluators agreed on 424 of 450 screenshots and
disagreed on 26.

| Metric | Value |
|---|---:|
| Validation images | 450 |
| Agreements | 424 |
| Disagreements | 26 |
| Observed agreement | 0.9422 |
| Cohen's kappa | 0.9338 |

Observed agreement is calculated as the proportion of screenshots for which
both evaluators assigned exactly the same category.

Cohen's kappa additionally accounts for agreement expected from the evaluators'
marginal category distributions.

---

## 3. Pipeline correspondence with EV01

The final pipeline classification was compared with EV01 across all
450 screenshots.

| Metric | Value |
|---|---:|
| N | 450 |
| Accuracy | 0.7267 |
| Cohen's kappa | 0.6925 |
| Macro F1 | 0.7205 |
| Weighted F1 | 0.7328 |

---

## 4. Pipeline correspondence with EV02

The final pipeline classification was compared with EV02 across all
450 screenshots.

| Metric | Value |
|---|---:|
| N | 450 |
| Accuracy | 0.7156 |
| Cohen's kappa | 0.6800 |
| Macro F1 | 0.7108 |
| Weighted F1 | 0.7203 |

---

## 5. Human-agreement subset

A complementary analysis was conducted using only screenshots for which EV01
and EV02 independently assigned the same category.

This subset contains 424 screenshots.

The common human category is used as a descriptive reference for comparison
with the final pipeline classification.

| Metric | Value |
|---|---:|
| N | 424 |
| Accuracy | 0.7406 |
| Cohen's kappa | 0.7082 |
| Macro F1 | 0.7309 |
| Weighted F1 | 0.7471 |

The human-agreement subset is not treated as an infallible ground truth.
The 26 human disagreement cases remain part of the complete
validation analysis and are retained in the individual EV01 and EV02
comparisons.

---

## 6. Category-level metrics

For each category, the analysis calculates:

- precision;
- recall;
- F1-score;
- support.

Precision measures the proportion of pipeline assignments to a category that
correspond to the human reference.

Recall measures the proportion of human-reference instances of a category
recovered by the pipeline.

F1 is the harmonic mean of precision and recall.

Complete category-level results are stored in:

`data/processed/human_validation_per_category.csv`

---

## 7. Confusion matrices

Four confusion matrices are generated:

- `data/processed/confusion_matrix_EV01_vs_EV02.csv`
- `data/processed/confusion_matrix_pipeline_vs_EV01.csv`
- `data/processed/confusion_matrix_pipeline_vs_EV02.csv`
- `data/processed/confusion_matrix_pipeline_vs_human_agreement.csv`

For pipeline comparisons, rows represent the human reference category and
columns represent the pipeline category.

These matrices permit identification of systematic category-specific
disagreements that are not visible from global metrics alone.

---

## 8. Interpretation

The validation distinguishes two different questions.

First, inter-rater reliability evaluates whether independent human evaluators
can apply the nine-category taxonomy consistently.

Second, pipeline-human correspondence evaluates the extent to which the final
classification corresponds with independent human judgments.

High human-human agreement does not imply perfect pipeline-human
correspondence. Consequently, agreement, Cohen's kappa, accuracy, precision,
recall and F1 are interpreted jointly rather than relying on a single metric.

---

## 9. Reproducibility

The validation analysis can be reproduced by running:

`python src/evaluate_human_validation.py`

The script reads:

`data/processed/human_validation_annotations.csv`

and generates:

- `data/processed/human_validation_summary.csv`
- `data/processed/human_validation_per_category.csv`
- `data/processed/confusion_matrix_EV01_vs_EV02.csv`
- `data/processed/confusion_matrix_pipeline_vs_EV01.csv`
- `data/processed/confusion_matrix_pipeline_vs_EV02.csv`
- `data/processed/confusion_matrix_pipeline_vs_human_agreement.csv`
- `docs/human_validation_metrics.md`

Rounded values in this document are reporting values. The CSV outputs generated
by the script constitute the computational results used for subsequent
analysis and manuscript reporting.
