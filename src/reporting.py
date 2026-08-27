from pathlib import Path
import pandas as pd


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "categoria_automatica" not in df.columns:
        raise ValueError("Missing 'categoria_automatica'. Run classification first.")

    counts = df["categoria_automatica"].value_counts(dropna=False)
    summary = counts.rename_axis("categoria").reset_index(name="n")
    summary["porcentaje"] = (summary["n"] / len(df) * 100).round(2)
    return summary


def export_results(df: pd.DataFrame, output_dir: str | Path) -> tuple[Path, Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    classified_path = output_dir / "classification_results.xlsx"
    summary_path = output_dir / "category_summary.xlsx"
    residual_path = output_dir / "otro_sitio_review.xlsx"

    df.to_excel(classified_path, index=False)
    build_summary(df).to_excel(summary_path, index=False)
    df.loc[df["requiere_revision"]].to_excel(residual_path, index=False)

    return classified_path, summary_path, residual_path
