# Reproducibility notes

The historical project included an original OCR-based five-category
classification (`palabra_base`), uniform OCR reprocessing, automatic
nine-category refinement, temporal resolution, and expert review of unresolved
episodes. The expert labels must not be represented as if they were produced
entirely by code.

The clean pipeline published here makes the automated component explicit and reproducible:

- category definitions live outside the code in YAML;
- the matching order is deterministic;
- every automated decision records the pattern that triggered it;
- unmatched cases are labelled `Otro sitio`;
- `palabra_base` is retained as the historical gating input;
- updated OCR is represented publicly through privacy-safe category evidence,
  not raw recognized text;
- the three-second episode grouping and 30-second temporal criterion are
  explicit;
- expert decisions are supplied as a separate, privacy-safe 378-episode input.

`src/reproduce_final_classification.py` reproduces all 18,829 authoritative
labels, classification methods, and temporal/manual flags from the public
derived inputs. Extraction and creation of evidence flags cannot be reproduced
without authorized access to the restricted recordings and OCR text.

The updated-OCR five-category result documented in
`initial_classification_summary.csv` was reconstructed after the authoritative
final classification. It tests the current initial classifier; it is not the
upstream label source for the historical final-label workflow.

Researchers reproducing the original downstream study should use the frozen
study YAML and public refinement inputs. Researchers applying the method in
another context should derive equivalent evidence from their own recordings,
adapt the YAML, and report those changes.
