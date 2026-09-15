# Data schema

## Authoritative final public dataset

`data/processed/corpus_100_videos_public_final.csv` contains one row per
temporal segment and these columns:

- `video_id`: anonymized video identifier;
- `start_time_s`, `end_time_s`, `duration_s`: segment times in seconds;
- `category`: authoritative final nine-category label;
- `classification_method`: automatic, temporal, or expert-review source of the
  final label;
- `ocr_mode`: OCR mode retained during uniform reprocessing;
- `temporal_interpolation`: whether the 30-second context rule assigned the
  final label;
- `manual_review`: whether expert episode review assigned the final label.

The public dataset intentionally excludes screenshot names, paths, OCR text,
participant information, and review notes.

## Privacy-safe refinement input

`data/processed/refinement_input_public.csv` is the public starting point for
reproducing the downstream nine-category classification. It contains:

- `segment_id`: stable identifier derived from anonymized video and segment
  order;
- the same anonymized video and temporal fields as the final dataset;
- `palabra_base`: the historical five-category label produced from the first
  OCR pass;
- `ocr_mode`: the final OCR mode;
- `matched_math_terms`: at most the first ten configured mathematical terms
  found in updated OCR;
- Boolean evidence columns for Wikipedia, YouTube, Juegos, GeoGebra, Quinan,
  and Screen Recorder.

The matched terms and Boolean fields are derived features. They preserve the
decisions required by the frozen historical rules without releasing the
underlying OCR text.

## Historical role of `palabra_base`

`palabra_detectada` was the original notebook's five-category output, including
an asterisk when repeated lexical evidence was present. `palabra_base` removed
that asterisk and retained the category. In the analysis that generated the
authoritative final labels, `palabra_base` was an input to refinement: it gated
which updated-OCR rules were applied. It must not be ignored or replaced by the
later reconstructed updated-OCR initial classification.

## Expert decisions

`data/processed/manual_review_decisions_public.csv` contains one row for each
of the 378 unresolved episodes: anonymized video, within-video episode number,
episode boundaries, number of candidate segments, and expert category. Review
notes, screenshot references, OCR text, and private paths are excluded.

## Restricted inputs

Original recordings, screenshots, raw OCR text, local paths, and detailed
review material are restricted educational research data. Their absence means
that extraction and evidence-feature derivation require authorized access. The
public derived inputs are sufficient to reproduce all downstream automatic,
temporal, and expert-decision applications and to verify the authoritative
final labels exactly.
