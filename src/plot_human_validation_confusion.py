from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT
    / "data"
    / "processed"
    / "confusion_matrix_pipeline_vs_human_agreement.csv"
)

OUTPUT_PDF = ROOT / "matriz_confusion.pdf"
OUTPUT_PNG = ROOT / "matriz_confusion.png"


# ---------------------------------------------------------
# Load confusion matrix
# ---------------------------------------------------------

df = pd.read_csv(INPUT, index_col=0)


def clean_label(label):
    label = label.replace("human_", "")
    label = label.replace("pipeline_", "")
    return label


row_labels = [clean_label(label) for label in df.index]
column_labels = [clean_label(label) for label in df.columns]

matrix = df.to_numpy()


# ---------------------------------------------------------
# Publication style
# ---------------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})


# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(8.8, 7.2))

im = ax.imshow(
    matrix,
    cmap="Blues",
    vmin=0,
    vmax=matrix.max(),
    aspect="equal"
)

# Color bar
cbar = fig.colorbar(
    im,
    ax=ax,
    fraction=0.046,
    pad=0.04
)
cbar.set_label("Number of screenshots")


# ---------------------------------------------------------
# Axis labels
# ---------------------------------------------------------

ax.set_xticks(np.arange(len(column_labels)))
ax.set_yticks(np.arange(len(row_labels)))

ax.set_xticklabels(column_labels)
ax.set_yticklabels(row_labels)

plt.setp(
    ax.get_xticklabels(),
    rotation=45,
    ha="right",
    rotation_mode="anchor"
)

ax.set_xlabel("Pipeline classification")
ax.set_ylabel("Human classification")

# No internal title.
# The figure title and explanation are provided by the LaTeX caption.


# ---------------------------------------------------------
# Cell values
# ---------------------------------------------------------

threshold = matrix.max() * 0.55

for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):

        value = matrix[i, j]

        ax.text(
            j,
            i,
            str(value),
            ha="center",
            va="center",
            color="white" if value > threshold else "black",
            fontsize=9,
            fontweight="bold" if i == j else "normal",
        )


# ---------------------------------------------------------
# Cell grid
# ---------------------------------------------------------

ax.set_xticks(
    np.arange(matrix.shape[1] + 1) - 0.5,
    minor=True
)

ax.set_yticks(
    np.arange(matrix.shape[0] + 1) - 0.5,
    minor=True
)

ax.grid(
    which="minor",
    color="white",
    linewidth=0.8
)

ax.tick_params(
    which="minor",
    bottom=False,
    left=False
)

for spine in ax.spines.values():
    spine.set_linewidth(0.6)


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_PDF,
    bbox_inches="tight"
)

fig.savefig(
    OUTPUT_PNG,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print(f"PDF saved to: {OUTPUT_PDF}")
print(f"PNG saved to: {OUTPUT_PNG}")
