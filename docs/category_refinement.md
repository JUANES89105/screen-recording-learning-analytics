# Exploratory category refinement

## Purpose

The initial OCR-based classifier assigns screen segments to five categories:

- Quinan
- Google
- ChatGPT
- GeoGebra
- Otro sitio

The subsequent refinement stage was not based on a fully predefined
taxonomy. Instead, OCR outputs and recurrent digital contexts were
inspected iteratively to identify environments that were not adequately
represented by the initial classification.

This stage therefore represents a human-guided, data-informed refinement
of the classification rules rather than an automatic discovery of
categories.

## Historical exploratory categories

During refinement, the historical notebook considered additional
digital contexts including:

- Wikipedia
- YouTube
- Juegos
- Screen Recorder
- Symbolab
- Gemini
- Desmos
- Claude

These exploratory categories should not be interpreted as the final
analytical taxonomy.

## Final analytical taxonomy

The final taxonomy used for human validation consists of nine categories:

1. Quinan
2. Google
3. Google (Mat)
4. GeoGebra
5. Juegos
6. YouTube
7. Wikipedia
8. Screen Recorder
9. Otro sitio

## Reproducibility principle

The historical exploratory notebook is preserved unchanged.

The reproducible implementation will distinguish between:

1. the exploratory process through which recurrent contexts and
   classification rules were identified; and
2. the frozen nine-category classifier subsequently used for analysis
   and human validation.

No historical classification columns will be used as input when
regenerating classifications from OCR text.