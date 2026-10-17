# Changelog

## Corrections after review (applies to README, docs/METHODOLOGY.md, src/, analysis-2.ipynb)

Metric fixes
- `calculate_der` now computes dropped (D) and added (H) per clip and then sums. Before, it netted expected minus produced over the whole pool, so its "DER" was really net loss and `hallucinated` was always 0 on this data. Overall DER is 78.4% (was printed as 26.8%); tonal DER is 89.8%.
- Net loss, drop rate, added rate and DER are reported together. The old README table mixed net loss (three rows) with drop rate (tonal row).
- `character_error_rate` is now Levenshtein CER. The CSV column of the same name is `1 - difflib ratio`; that score is kept as `sequence_dissimilarity`. Mean CER over clips is 0.365 (legacy column 0.333; the old README said 32.5%).
- `count_diacritics` counts NFD letter clusters carrying grave, acute, macron or dot-below instead of a hard-coded precomposed character set. It reproduces all 21 `diacritics_expected` and `diacritics_produced` values.

Statistics
- Bootstrap resamples clips; undefined resamples are reported instead of turning the interval into NaN (the old code returned NaN intervals for two categories).
- `bootstrap_ci` returns a dict (`point`, `boot_mean`, `lo`, `hi`, `n_undefined`).
- The explanation that the bootstrap mean (75.5%) exceeds the raw rate (61.2%) because of "extreme loss rates" was wrong: 61.2% is net loss, 75.5% is drop rate, and both are point estimates on the original data.
- "Tonal CI does not overlap other categories" was wrong. A paired bootstrap shows the tonal drop rate differs from cross-lingual (64.4 points, CI 40.5 to 85.7) but not from domain (44.3, CI -9.4 to 80.6) or language boundary (25.5, CI -18.9 to 78.6).
- New position-aware estimate `align_marks` / `aligned_table`: overall 33 correct, 7 wrong, 57 missing, 31 inserted.

Claims softened or corrected
- Category 1 does not have "NO diacritics": 18 expected marks, mostly dot-below.
- "Orthographic bias" and "generates diacritics probabilistically based on lexical priors" became "consistent with", since one speaker, 21 clips and no comparison model cannot establish the mechanism. The monotone clip's reference has no dot-below marks, so some added ọ and ị there are plausibly correct orthography; tone-only counts are given.
- The akwa/akwà/àkwà/ákwá word glosses were removed from the README pending verification against a standard Igbo reference.
- Single-annotator ground truth added to the limitations.

Housekeeping
- `src/visualize.py` no longer ships hard-coded example bootstrap values (one was invented: script_hallucination 0.360 [0.087, 0.680]); it computes them from the data. Figures renamed `fig1_drop_rate_by_category`, `fig2_cer_vs_drop_rate`.
- `src/utils.py`: `validate_audio_files` resolves `audio/NN_*.wav` metadata paths against `.wav` or `.m4a` files; `category_breakdown` reports all metrics.
- Dataset links use `Chiz/` capitalization.
- New `analysis-2.ipynb` (offline, CPU, executed outputs included except figures).

Still to verify by hand
- `analysis.ipynb` cell 1 title says omniASR-CTC-3B while the model evaluated is CTC-1B.
- Tone-to-meaning glosses for the akwa clip.
- Whether `data/metadata.csv` should point at `.m4a` (the files in the repo) or `.wav`.
