# Reproducible workflow

## Scope

The pipeline separates two tasks:

1. **Evidence extraction** from screen recordings (screenshots + OCR), performed by the extraction notebook/script used by the project.
2. **Site classification** from the resulting OCR Excel files, implemented here as a deterministic YAML-configured classifier.

The classifier is not intended to discover every possible website automatically. Researchers define the sites relevant to their context in `config/sites.yaml`. Records that do not match any configured rule are labelled `Otro sitio` and exported separately for focused human review.

## Operational flow

```text
screen recordings
      |
      v
screenshots + OCR (per-video Excel)
      |
      v
merge Excel files
      |
      v
configure config/sites.yaml
      |
      v
rule-based classifier
      |
      +--> classified records
      +--> category summary
      +--> Otro sitio review file
```

## Why `Otro sitio` is retained

`Otro sitio` is an explicit residual category. It can contain OCR failures, platforms not declared in the YAML, or ambiguous screenshots requiring visual interpretation. This preserves reproducibility: the automatic rules remain explicit while the remaining manual work is identifiable and auditable.

## Applying the pipeline to a new study

Copy `config/sites_example.yaml`, rename it, and replace/add categories and patterns that correspond to the digital environments of interest. Do not modify the classifier source code simply to change the study context.
