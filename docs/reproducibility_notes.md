# Reproducibility notes

The historical project included an automatic classification followed by manual review of OCR text and screenshots. The manually reviewed labels therefore should not be represented as if they were produced entirely by code.

The clean pipeline published here makes the automated component explicit and reproducible:

- category definitions live outside the code in YAML;
- the matching order is deterministic;
- every automated decision records the pattern that triggered it;
- unmatched cases are labelled `Otro sitio`;
- `Otro sitio` cases are exported for explicit human refinement;
- technical recording overlays can be stored as auxiliary markers rather than forced into the site taxonomy.

Researchers reproducing the original study can use the frozen study YAML. Researchers applying the method in another context should adapt the YAML and report those changes.
