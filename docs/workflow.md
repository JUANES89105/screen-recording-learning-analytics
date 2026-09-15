# Reproducible workflow

## Scope

The repository separates three reproducibility layers:

1. **Evidence extraction** from restricted screen recordings: screenshots,
   segmentation, and OCR.
2. **Historical corpus construction**: original `palabra_base`, updated-OCR
   refinement, temporal resolution, and expert episode decisions.
3. **Public downstream reproduction** from privacy-safe derived evidence and
   expert decisions.

The classifier is not intended to discover every possible website automatically. Researchers define the sites relevant to their context in `config/sites.yaml`. Records that do not match any configured rule are labelled `Otro sitio` and exported separately for focused human review.

## Operational flow

```text
restricted screen recordings
      |
      v
segments + first OCR + historical palabra_base
      |
      v
uniformly updated OCR
      |
      v
palabra_base-gated nine-category refinement
      |
      v
candidate episodes (maximum 3-s gap between candidates)
      |
      +--> <=30 s and same category on both sides: temporal assignment
      |
      +--> otherwise: expert episode decision
      |
      v
authoritative final nine-category labels
```

The updated-OCR five-category summary produced with
`config/sites_initial.yaml` is a later reproducibility reconstruction. It is
not the historical input to the final-label route above.

## Public downstream command

The public input replaces restricted OCR text with Boolean category-level
evidence and matched mathematical terms. It preserves the decisions made by
the frozen rules without releasing screen content:

```bash
python -m src.reproduce_final_classification \
  --output /tmp/corpus_100_videos_reproduced.csv
```

The command applies the historical gates, candidate-episode grouping,
30-second context rule, and privacy-safe expert episode decisions, then checks
the result against `corpus_100_videos_public_final.csv`.

## Why `Otro sitio` is retained

`Otro sitio` is an explicit residual category. It can contain OCR failures,
platforms not declared in the YAML, or ambiguous screenshots requiring visual
interpretation. Expert decisions are inputs to reproduction, not outputs
claimed to have been regenerated automatically.

## Applying the pipeline to a new study

Copy `config/sites_example.yaml`, rename it, and replace/add categories and patterns that correspond to the digital environments of interest. Do not modify the classifier source code simply to change the study context.
