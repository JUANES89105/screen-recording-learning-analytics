# Category traceability

> **Historical document — not the current 18,829-segment workflow.** The
> 18,976-record counts, `palabra_base_2` review, expanded exploratory taxonomy,
> and future-tense reconstruction below describe an earlier pipeline version.
> They are retained as historical evidence and must not be used to explain or
> reproduce the manuscript's authoritative final classification. For the
> current provenance, inputs, and exact downstream reproduction, use
> `docs/category_refinement.md`, `docs/data_schema.md`, `docs/workflow.md`, and
> `src/reproduce_final_classification.py`.


This document reconstructs how categories evolved from the initial OCR-based classification to subsequent automated refinement, manual review, validation, refined site detection, and later analytical grouping. It also distinguishes historical classification decisions from the reproducible rule-based pipeline reconstructed for the study.

## Stage 1. Initial classifier

The initial classifier was defined a priori to identify four digital environments considered relevant at the beginning of the study. Records that did not match any explicit rule were assigned to a residual category.

| Initial category | Historical keywords/rules              | Source notebook         |
| ---------------- | -------------------------------------- | ----------------------- |
| Quinan           | `quinan`, `aulavirtual`                | `videos_analisis.ipynb` |
| Google           | `google`                               | `videos_analisis.ipynb` |
| ChatGPT          | `chatgpt`                              | `videos_analisis.ipynb` |
| GeoGebra         | `geogebra`                             | `videos_analisis.ipynb` |
| Otro sitio       | Assigned when no explicit rule matched | `videos_analisis.ipynb` |

This initial rule-based classifier generated the first site labels from the OCR-extracted text.

## Stage 2. Exploratory automated refinement

Inspection of the OCR output showed that the initial categories did not capture all recurrent digital environments. The classification rules were therefore progressively expanded using additional keywords, phrases, and contextual indicators found in the OCR text.

The refinement also incorporated mathematical terms and task-specific expressions to distinguish mathematical from non-mathematical contexts when the site identity alone was insufficient.

| Detected site/context | How it emerged                                           | Historical rule/keyword evidence                               | Subsequent role                                                           |
| --------------------- | -------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Wikipedia             | Recurrent site detected in OCR text                      | `wikipedia` and related OCR patterns                           | Retained as site category                                                 |
| YouTube               | Recurrent site detected in OCR text                      | `youtube` and related OCR patterns                             | Retained as site category                                                 |
| Juegos                | Recurrent game-related environments                      | Game names and game-related textual patterns                   | Retained as contextual category                                           |
| Screen Recorder       | Technical interface detected in screen recordings        | `screen recorder` and related interface/OCR evidence           | Initially treated as a category; later reconsidered as a technical marker |
| Google (Mat)          | Mathematical activity occurring in Google                | Google evidence combined with mathematical terms/context       | Used to distinguish mathematical Google activity                          |
| Otro (Mat)            | Mathematical activity without a recognized specific site | Mathematical terms/context without another specific site match | Used as mathematical residual category                                    |
| Desmos                | Additional mathematical environment detected             | `desmos`                                                       | Retained as mathematical site                                             |
| Mathway               | Additional mathematical environment detected             | `mathway`                                                      | Retained as mathematical site                                             |
| Symbolab              | Additional mathematical environment detected             | `symbolab`                                                     | Retained as mathematical site                                             |
| Gemini                | Additional AI environment detected                       | `gemini`                                                       | Detected during refinement                                                |
| Claude                | Additional AI environment detected                       | `claude`                                                       | Detected during refinement                                                |

The expanded classifier used prioritized phrases, keyword counts, and mathematical terminology. In particular, task-specific mathematical terms were used to identify Quinan-related mathematical activity when sufficient textual evidence was present.

The resulting automated labels were retained as the historical automated classification, subsequently stored as `palabra_base_original`.

## Stage 3. Manual review and correction

Following the expanded automated classification, the records were manually reviewed using both the OCR-extracted text and the corresponding screen capture. This review was conducted to resolve misclassifications and ambiguous cases that could not be reliably distinguished using the automated rules available at that stage.

The automated classification was preserved in `palabra_base_original`, while the manually reviewed classification was stored in `palabra_base_2`.

The manual review modified **2,253 of the 18,976 records (11.87%)**.

The most frequent changes were:

| Automated label (`palabra_base_original`) | Manually reviewed label (`palabra_base_2`) | Records |
| ----------------------------------------- | ------------------------------------------ | ------: |
| Otro sitio                                | Juegos                                     |   1,657 |
| Otro sitio                                | YouTube                                    |     224 |
| Otro sitio                                | Quinan                                     |     151 |
| Screen Recorder                           | Quinan                                     |      47 |
| ChatGPT                                   | YouTube                                    |      45 |
| YouTube                                   | Juegos                                     |      45 |
| Quinan                                    | Juegos                                     |      25 |
| Otro sitio                                | Wikipedia                                  |      20 |
| Screen Recorder                           | YouTube                                    |      19 |
| Otro sitio                                | Screen Recorder                            |       8 |
| Screen Recorder                           | Juegos                                     |       4 |
| Google                                    | Juegos                                     |       3 |
| ChatGPT                                   | Juegos                                     |       2 |
| ChatGPT                                   | Quinan                                     |       1 |
| Google                                    | YouTube                                    |       1 |
| Screen Recorder                           | ChatGPT                                    |       1 |

The largest effect of the manual review concerned the residual category `Otro sitio`. Its frequency decreased from **3,166 to 1,106 records**, primarily because previously unresolved observations were identified as `Juegos`, `YouTube`, or `Quinan`.

Conversely, `Juegos` increased from **40 to 1,776 records**, showing that game-related environments constituted the main source of ambiguity in the preceding automated classification.

This manual review should therefore be understood as a historical quality-control and category-refinement stage rather than as part of the fully reproducible automated pipeline reconstructed subsequently.

## Stage 4. Post-review rule-based refinement

After the manual review, additional rule-based procedures were developed to reassess categories that remained particularly ambiguous.

The procedures used `palabra_base_2` as their input and re-examined the OCR-extracted text, particularly for records labelled as `Screen Recorder` and `Otro sitio`.

For `Screen Recorder`, textual evidence was used to determine whether the underlying environment could instead be identified as Quinan, ChatGPT, or another site. This reflected the recognition that Screen Recorder could represent the recording interface rather than the substantive digital environment being used by the student.

Records remaining in `Otro sitio` were also re-evaluated using the expanded classification rules and OCR evidence.

This stage therefore represents a further automated refinement **after** the historical manual review; it did not generate `palabra_base_2`.

## Stage 5. Validation taxonomy

The nine categories used in human validation were:

1. Quinan
2. Google
3. Google (Mat)
4. GeoGebra
5. Juegos
6. YouTube
7. Wikipedia
8. Screen Recorder
9. Otro sitio

This taxonomy represents the operational categories used for evaluating classification performance and should be distinguished from both the broader exploratory category set and the later analytical grouping.

## Stage 6. Refined site classification

A subsequent classifier revisited the original OCR-derived fields and generated a new variable, `categoria_refinada`.

This stage consolidated the accumulated classification logic and included site-specific and contextual categories such as Quinan, ChatGPT, GeoGebra, Desmos, Symbolab, Mathway, YouTube, Wikipedia, Juegos, Google (Mat), Google, Otro (Mat), and Otro sitio.

At this stage, `Screen Recorder` was no longer treated solely as an analytical site category. Instead, its presence could be represented separately through the technical indicator:

`marca_screen_recorder`

This distinction separated the digital environment inferred from the student's activity from evidence associated with the screen-recording software itself.

## Stage 7. Analytical grouping

The refined site/context categories were subsequently mapped into broader analytical groups through `uso_consolidado`.

| Detected site/context | Analytical group      |
| --------------------- | --------------------- |
| Quinan                | evaluative use        |
| GeoGebra              | mathematical use      |
| Google (Mat)          | mathematical use      |
| ChatGPT               | mathematical use      |
| Desmos                | mathematical use      |
| Mathway               | mathematical use      |
| Symbolab              | mathematical use      |
| Otro (Mat)            | mathematical use      |
| Google                | non-instructional use |
| YouTube               | non-instructional use |
| Wikipedia             | non-instructional use |
| Juegos                | non-instructional use |
| Otro sitio            | other                 |

These analytical groups were introduced to support interpretation at a higher level than individual websites or applications.

## Reproducibility strategy

The historical workflow included a manual review stage that produced `palabra_base_2`. Because this intervention cannot be reproduced automatically from the original data alone, the reconstructed pipeline does not treat the manually reviewed labels as an automated processing step.

Instead, `palabra_base_2` is retained as a **historical manually reviewed reference classification**.

The reproducible pipeline will apply the reconstructed classification and refinement rules directly to the original OCR-derived information and generate a new automated classification independently of `palabra_base_2`.

The resulting automated labels will then be compared with the historical manually reviewed labels. Agreement will be evaluated globally and by category, with particular attention to the **2,253 records whose labels were changed during manual review**.

This comparison will make it possible to determine how closely the reconstructed rule-based pipeline reproduces the historical human decisions and to identify categories for which additional automated rules may be required.
