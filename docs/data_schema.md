# Data schema

The pipeline supports an intermediate tabular input containing
segment-level metadata and OCR output.

## Neutral input columns

- `Segundo entrada`: start time of the segment in seconds.
- `Segundo salida`: end time of the segment in seconds.
- `Tiempo en página (s)`: segment duration in seconds.
- `Captura`: screenshot associated with the segment.
- `archivo`: screenshot/file identifier.
- `texto_extraido`: raw text extracted through OCR.
- `archivo_origen`: source record associated with the segment.

## Historical classification columns

The following columns may exist in historical datasets but are not
used as input when reproducing the classification process:

- `palabra_detectada`
- `palabra_base`

These columns are considered outputs of previous classification runs
and must be ignored when regenerating classifications from OCR data.