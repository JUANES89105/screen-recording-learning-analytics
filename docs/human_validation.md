# Human validation of the final classification

## Purpose

Human validation was conducted to evaluate the correspondence between the
final classification produced by the complete screen-recording processing
pipeline and independent human judgments.

The validation therefore evaluates the **final classification**, rather than
only the output of the initial rule-based classifier.

The final labels evaluated in this stage may have been obtained through
different components of the complete procedure, including:

1. rule-based classification;
2. taxonomy refinement;
3. temporal-context resolution; and
4. expert review of unresolved episodes.

Human validation was performed independently after this final classification
had been established.

---

## Final taxonomy

The final taxonomy contains nine categories:

- Quinan
- Google
- Google (Mat)
- GeoGebra
- Wikipedia
- YouTube
- Juegos
- Screen Recorder
- Otro sitio

These are the same nine categories used in the final public corpus.

---

## Validation sample

A stratified random sample of 450 screenshots was selected from the final
classified corpus.

The sampling design included:

- 450 screenshots in total;
- 50 screenshots from each of the nine final categories;
- random seed: `20260826`;
- 85 source videos represented in the sample;
- 450 unique screenshots;
- no duplicated image hashes.

Stratification was based on the final pipeline classification. The purpose of
the balanced design was to ensure that every category was represented with the
same number of validation instances, independently of its prevalence in the
complete corpus.

Consequently, classification metrics calculated on this validation sample
should be interpreted as performance on a balanced validation design rather
than as prevalence-weighted estimates of the complete corpus.

---

## Blinding and annotation procedure

Each validation image was assigned an anonymous identifier of the form:

```text
IMG_0001
IMG_0002
...
IMG_0450
