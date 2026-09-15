# Human-validation provenance

The manuscript uses the definitive second-round validation responses. The
authoritative internal workbook has two sheets, `EV01` and `EV02`, with 450
unique image responses each. Its SHA-256 is:

`89d9d219f7abd4b2c905c45aa409c54fabf0c7514adce292d4b201964dd1eeb9`

An ID-based audit found 450/450 EV01 and 450/450 EV02 label matches between
that workbook and the public analysis input:

`data/processed/human_validation_annotations.csv`

The public CSV is authoritative for reproducible metric calculation. It has
SHA-256:

`00946971b052882f2a40eeba333b8bbd3fdac82c46db9158756033b27905abf8`

`src/evaluate_human_validation.py` uses this CSV to reproduce 424 agreements,
26 disagreements, 94.22% observed agreement, Cohen's kappa 0.9338, all three
pipeline-human comparisons, category metrics, and confusion matrices.

## Privacy boundary

The raw workbook is intentionally excluded from the public package. Its
pseudonymous evaluator codes are not direct identities, but its response
timestamps are unnecessary for reproducing the published analyses and create
avoidable linkage risk. The public annotations CSV retains only stable image
IDs, pipeline labels, evaluator labels, and agreement status.

Discarded validation rounds belong only in a clearly named private
`historical/discarded` location and must never use the authoritative workbook
name. Derived local files that retain private paths or working metadata must
also remain outside the public release.
