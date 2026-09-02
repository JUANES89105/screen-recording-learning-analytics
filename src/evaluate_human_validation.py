from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    precision_recall_fscore_support,
    f1_score,
)


CATEGORIES = [
    "Quinan",
    "Google",
    "Google (Mat)",
    "GeoGebra",
    "Wikipedia",
    "YouTube",
    "Juegos",
    "Screen Recorder",
    "Otro sitio",
]


def evaluate_pair(reference, prediction, labels=CATEGORIES):
    accuracy = accuracy_score(reference, prediction)
    kappa = cohen_kappa_score(reference, prediction, labels=labels)

    precision, recall, f1, support = precision_recall_fscore_support(
        reference,
        prediction,
        labels=labels,
        zero_division=0,
    )

    per_category = pd.DataFrame(
        {
            "category": labels,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    )

    summary = {
        "n": len(reference),
        "accuracy": accuracy,
        "kappa": kappa,
        "macro_f1": f1_score(
            reference,
            prediction,
            labels=labels,
            average="macro",
            zero_division=0,
        ),
        "weighted_f1": f1_score(
            reference,
            prediction,
            labels=labels,
            average="weighted",
            zero_division=0,
        ),
    }

    matrix = confusion_matrix(
        reference,
        prediction,
        labels=labels,
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=[f"human_{x}" for x in labels],
        columns=[f"pipeline_{x}" for x in labels],
    )

    return summary, per_category, matrix_df


def main():
    root = Path(__file__).resolve().parents[1]

    input_path = (
        root
        / "data"
        / "processed"
        / "human_validation_annotations.csv"
    )

    output_dir = root / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    required = {
        "image_id",
        "pipeline_category",
        "EV01",
        "EV02",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if len(df) != 450:
        print(
            f"WARNING: expected 450 validation rows, "
            f"found {len(df)}"
        )

    # --------------------------------------------------
    # Inter-rater agreement
    # --------------------------------------------------

    human_agreement = df["EV01"] == df["EV02"]

    n_total = len(df)
    n_agreement = int(human_agreement.sum())
    n_disagreement = n_total - n_agreement

    observed_agreement = n_agreement / n_total

    human_kappa = cohen_kappa_score(
        df["EV01"],
        df["EV02"],
        labels=CATEGORIES,
    )

    # --------------------------------------------------
    # Pipeline vs EV01
    # --------------------------------------------------

    ev01_summary, ev01_per_cat, ev01_matrix = evaluate_pair(
        df["EV01"],
        df["pipeline_category"],
    )

    # --------------------------------------------------
    # Pipeline vs EV02
    # --------------------------------------------------

    ev02_summary, ev02_per_cat, ev02_matrix = evaluate_pair(
        df["EV02"],
        df["pipeline_category"],
    )

    # --------------------------------------------------
    # Human-agreement subset
    # --------------------------------------------------

    consensus_df = df.loc[human_agreement].copy()

    consensus_df["human_agreement_category"] = consensus_df[
        "EV01"
    ]

    consensus_summary, consensus_per_cat, consensus_matrix = (
        evaluate_pair(
            consensus_df["human_agreement_category"],
            consensus_df["pipeline_category"],
        )
    )

    # --------------------------------------------------
    # Summary table
    # --------------------------------------------------

    summary_rows = [
        {
            "comparison": "EV01_vs_EV02",
            "n": n_total,
            "agreements": n_agreement,
            "disagreements": n_disagreement,
            "observed_agreement": observed_agreement,
            "accuracy": None,
            "kappa": human_kappa,
            "macro_f1": None,
            "weighted_f1": None,
        },
        {
            "comparison": "pipeline_vs_EV01",
            **ev01_summary,
        },
        {
            "comparison": "pipeline_vs_EV02",
            **ev02_summary,
        },
        {
            "comparison": "pipeline_vs_human_agreement",
            **consensus_summary,
        },
    ]

    summary_df = pd.DataFrame(summary_rows)

    summary_df.to_csv(
        output_dir / "human_validation_summary.csv",
        index=False,
    )

    # --------------------------------------------------
    # Per-category results
    # --------------------------------------------------

    ev01_per_cat.insert(
        0,
        "comparison",
        "pipeline_vs_EV01",
    )

    ev02_per_cat.insert(
        0,
        "comparison",
        "pipeline_vs_EV02",
    )

    consensus_per_cat.insert(
        0,
        "comparison",
        "pipeline_vs_human_agreement",
    )

    per_category_df = pd.concat(
        [
            ev01_per_cat,
            ev02_per_cat,
            consensus_per_cat,
        ],
        ignore_index=True,
    )

    per_category_df.to_csv(
        output_dir / "human_validation_per_category.csv",
        index=False,
    )

    # --------------------------------------------------
    # Confusion matrices
    # --------------------------------------------------

    ev01_matrix.to_csv(
        output_dir / "confusion_matrix_pipeline_vs_EV01.csv"
    )

    ev02_matrix.to_csv(
        output_dir / "confusion_matrix_pipeline_vs_EV02.csv"
    )

    consensus_matrix.to_csv(
        output_dir
        / "confusion_matrix_pipeline_vs_human_agreement.csv"
    )

    # EV01 vs EV02 matrix
    human_matrix = confusion_matrix(
        df["EV01"],
        df["EV02"],
        labels=CATEGORIES,
    )

    human_matrix_df = pd.DataFrame(
        human_matrix,
        index=[f"EV01_{x}" for x in CATEGORIES],
        columns=[f"EV02_{x}" for x in CATEGORIES],
    )

    human_matrix_df.to_csv(
        output_dir / "confusion_matrix_EV01_vs_EV02.csv"
    )

    # --------------------------------------------------
    # Console output
    # --------------------------------------------------

    print("\nHUMAN VALIDATION SUMMARY")
    print("=" * 50)

    print("\nEV01 vs EV02")
    print(f"N: {n_total}")
    print(f"Agreements: {n_agreement}")
    print(f"Disagreements: {n_disagreement}")
    print(f"Observed agreement: {observed_agreement:.4f}")
    print(f"Cohen's kappa: {human_kappa:.4f}")

    for name, values in [
        ("Pipeline vs EV01", ev01_summary),
        ("Pipeline vs EV02", ev02_summary),
        (
            "Pipeline vs human agreement",
            consensus_summary,
        ),
    ]:
        print(f"\n{name}")
        print(f"N: {values['n']}")
        print(f"Accuracy: {values['accuracy']:.4f}")
        print(f"Kappa: {values['kappa']:.4f}")
        print(f"Macro F1: {values['macro_f1']:.4f}")
        print(
            f"Weighted F1: "
            f"{values['weighted_f1']:.4f}"
        )
    # --------------------------------------------------
    # Markdown report
    # --------------------------------------------------

    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = docs_dir / "human_validation_metrics.md"

    report = f"""# Human validation metrics

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

The validation sample contains {n_total} screenshots.

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

The two evaluators agreed on {n_agreement} of {n_total} screenshots and
disagreed on {n_disagreement}.

| Metric | Value |
|---|---:|
| Validation images | {n_total} |
| Agreements | {n_agreement} |
| Disagreements | {n_disagreement} |
| Observed agreement | {observed_agreement:.4f} |
| Cohen's kappa | {human_kappa:.4f} |

Observed agreement is calculated as the proportion of screenshots for which
both evaluators assigned exactly the same category.

Cohen's kappa additionally accounts for agreement expected from the evaluators'
marginal category distributions.

---

## 3. Pipeline correspondence with EV01

The final pipeline classification was compared with EV01 across all
{ev01_summary['n']} screenshots.

| Metric | Value |
|---|---:|
| N | {ev01_summary['n']} |
| Accuracy | {ev01_summary['accuracy']:.4f} |
| Cohen's kappa | {ev01_summary['kappa']:.4f} |
| Macro F1 | {ev01_summary['macro_f1']:.4f} |
| Weighted F1 | {ev01_summary['weighted_f1']:.4f} |

---

## 4. Pipeline correspondence with EV02

The final pipeline classification was compared with EV02 across all
{ev02_summary['n']} screenshots.

| Metric | Value |
|---|---:|
| N | {ev02_summary['n']} |
| Accuracy | {ev02_summary['accuracy']:.4f} |
| Cohen's kappa | {ev02_summary['kappa']:.4f} |
| Macro F1 | {ev02_summary['macro_f1']:.4f} |
| Weighted F1 | {ev02_summary['weighted_f1']:.4f} |

---

## 5. Human-agreement subset

A complementary analysis was conducted using only screenshots for which EV01
and EV02 independently assigned the same category.

This subset contains {consensus_summary['n']} screenshots.

The common human category is used as a descriptive reference for comparison
with the final pipeline classification.

| Metric | Value |
|---|---:|
| N | {consensus_summary['n']} |
| Accuracy | {consensus_summary['accuracy']:.4f} |
| Cohen's kappa | {consensus_summary['kappa']:.4f} |
| Macro F1 | {consensus_summary['macro_f1']:.4f} |
| Weighted F1 | {consensus_summary['weighted_f1']:.4f} |

The human-agreement subset is not treated as an infallible ground truth.
The {n_disagreement} human disagreement cases remain part of the complete
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
"""

    markdown_path.write_text(report, encoding="utf-8")

    print(f"\nMarkdown report written to:")
    print(markdown_path)

if __name__ == "__main__":
    main()
