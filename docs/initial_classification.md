# Initial classification logic

The first classification stage operates on the OCR text associated with each screen segment.

## Initial categories

The original implementation defines four explicit categories:

- `quinan`
- `google`
- `chatgpt`
- `geogebra`

If no rule is matched, the segment is assigned to:

- `otro sitio`

## Initial keywords

The original classifier uses the following keyword sets:

### quinan
- `quinan`
- `aulavirtual`

### google
- `google`

### chatgpt
- `chatgpt`

### geogebra
- `geogebra`

## Text normalization

Before classification:

1. OCR text is converted to lowercase.
2. Keyword matching is performed using regular expressions with word boundaries.

## Classification rule

For each category, the classifier counts the number of keyword occurrences in the OCR text.

The category with the highest number of matches is assigned.

If no category has any match, the segment is assigned to `otro sitio`.

## Historical tie-breaking behavior

The historical Python implementation used:

`max(conteos, key=conteos.get)`

Therefore, in the case of an exact tie, Python preserves the category order defined in the dictionary.

The historical priority order was:

1. `quinan`
2. `google`
3. `chatgpt`
4. `geogebra`

This behavior must initially be reproduced exactly for historical reproducibility.

## Additional marker

The historical implementation appended `*` to the detected category when more than one keyword occurrence was found.

Example:

`quinan*`

This marker represents repeated lexical evidence only. It is not a confidence score or probability.

The reproducible pipeline will preserve this behavior as a historical output field, while keeping the base category in a separate field.