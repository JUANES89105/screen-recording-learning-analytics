# Category refinement

## Historical refinement

The final taxonomy used in the study was not defined entirely a priori.

The initial OCR-based classification distinguished a small set of digital environments and assigned unmatched observations to a residual category. Inspection of the resulting corpus subsequently revealed recurrent environments and contextual distinctions that were not adequately represented by the initial scheme.

Additional categories and distinctions were therefore introduced through successive automated and human-guided refinement stages.

This historical process should not be interpreted as automatic category discovery. Categories were introduced by the researchers after inspection of the empirical corpus and were subsequently operationalized through explicit classification rules.

## Final study taxonomy

The final public corpus uses nine categories:

1. Quinan
2. Google
3. Google (Mat)
4. GeoGebra
5. Wikipedia
6. YouTube
7. Juegos
8. Screen Recorder
9. Otro sitio

`Otro sitio` is retained as an explicit residual category.

`Google (Mat)` represents a derived contextual category in which Google activity contains configured mathematical evidence.

## Reproducible refinement engine

The public implementation separates the refinement engine from the study-specific taxonomy.

The executable refinement logic is implemented in:

`src/refine_classification.py`

Study-specific categories, OCR patterns, derived-category definitions, historical-label mappings, residual refinement priorities, and review rules are defined externally in:

`config/sites.yaml`

The Python refinement engine does not contain the names of the study categories. It interprets the configuration supplied through YAML.

Consequently, researchers adapting the pipeline to another context can define different categories and refinement rules without modifying the Python refinement source code.

## Historical labels and reproducibility

Historical classification variables and the reproducible pipeline serve different purposes.

Historical labels document intermediate decisions made during construction of the original corpus. When a refinement workflow requires a historical label as input, the relevant column and its interpretation are explicitly declared in the YAML configuration.

This makes the dependency visible rather than embedding it in the executable code.

The final manually reviewed historical labels should not be interpreted as outputs that can necessarily be regenerated automatically from OCR alone.

## Human review

Some ambiguous or residual observations require human interpretation.

The reproducible pipeline therefore preserves an explicit distinction between:

- deterministic classification and refinement rules;
- configured historical dependencies;
- cases flagged for manual review; and
- historical human decisions used during development of the study taxonomy.

This distinction is necessary for accurately representing the reproducibility of the original research workflow.
