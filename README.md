# Igbo ASR Tonal Evaluation

[![Dataset](https://img.shields.io/badge/🤗%20Dataset-omniASR--igbo--blindspots-blue)](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots)
[![Docs](https://img.shields.io/badge/docs-Methodology%20%26%20References-blue)](docs/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Colab to GitHub Notebook Metadata Sanitizer](https://github.com/chizkidd/igbo-asr-tonal-evaluation/actions/workflows/clean-notebooks.yml/badge.svg)](https://github.com/chizkidd/igbo-asr-tonal-evaluation/actions/workflows/clean-notebooks.yml)
![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.igbo-asr-tonal-evaluation)
![Hugging Face Downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fhuggingface.co%2Fapi%2Fdatasets%2FChiz%2FomniASR-igbo-blindspots%3Fexpand%255B%255D%3Ddownloads%26expand%255B%255D%3DdownloadsAllTime&query=%24.downloadsAllTime&label=HuggingFace%20Downloads&color=blue)

A diagnostic evaluation of tone and diacritic fidelity in `facebook/omniASR-CTC-1B` when transcribing Igbo, a tonal Niger-Congo language with ~45 million speakers ([source](https://celt.indiana.edu/portal/Igbo/index.html)). The data are 21 clips from one speaker, with single-annotator references. This is a blind-spot probe, not a measurement of prevalence, and it says nothing about Igbo ASR in general.

## Overview

**Headline result.** In the four Igbo tonal clips the references carry 32 tone-marked letters. The model output carries 3 tone marks, all of them in clip 09, whose reference has none. Aligning reference and output on base letters and checking each reference mark, **0 of the 32 reference tone marks are reproduced**: 28 are missing on a correctly aligned letter, 4 sit on a letter the model got wrong or dropped, and none is missing because the letter itself was deleted. The optimal alignment is unique for each of these clips, and the totals do not change under five alternative scoring schemes.

What the numbers also show:

- **Marks are dropped in bulk.** Over all 21 clips the references carry 97 marked letters and 51 are dropped (drop rate 52.6%); in the tonal category 37 of 49 are dropped. Those tone-category counts are historical: they pool four Igbo clips with two Yoruba clips and count dot-below letters as well as tone marks.
- **Marks are also added.** 25 marks appear where the reference has none or fewer (added rate 25.8%), so net loss (26.8%) understates how often the output disagrees with the reference. Pooled DER is 78.4%.
- **Transcription is imperfect independently of marks.** Strict CER is 0.287 pooled and 0.305 as a mean over clips; with every mark ignored, base-letter CER is 0.180 pooled. For the four tonal pilot clips: strict 0.416 pooled, 0.197 when tone marks are ignored, 0.121 when every mark is ignored.
- **The output does not vary with the written tone patterns.** Clips 06 and 07 repeat one word under four and three written patterns; the output carries no tone marks in either clip and does not differ by pattern.

**What can be said, conditional on the author's references:** the output text of the four Igbo tonal clips contains far fewer tone marks than the references, and none of the reference tone marks is reproduced under the implemented alignment rule. **What cannot be said:** why the model behaves this way, whether it responds to acoustic tone, anything about other speakers, dialects or Igbo ASR in general, or that any reference tone mark, word meaning or spelling is correct.

Everything below is conditional on one speaker's references. They were written by the speaker, who is also the only annotator, and no independent fluent-Igbo reviewer has checked them. A protocol for that review has been written but not executed. All figures compare the model output with those references; none of them measures acoustic tone perception.

## Dataset

**21 audio samples** across 4 error categories:

1. Cross-lingual Orthographic Interference (5 samples)
2. Phonemic Tone Sensitivity (6 samples)
3. Language Boundary Effects (5 samples)
4. Domain-Specific Lexical Coverage (5 samples)

The categories are task labels and contain mixed languages: the tonal category has 4 Igbo and 2 Yoruba clips, the language-boundary category has 1 Nigerian Pidgin clip, and the domain category has 1 French clip. Language, not task category, is therefore the grouping the corrected analysis uses.

**[View Dataset on HuggingFace](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots)**

### Listen to Examples

Audio files are included in this repository (M4A format). Click to play directly on GitHub:

**Repeated word with four written tone patterns:**
- [06_tonal_akwa.m4a](data/audio/06_tonal_akwa.m4a) - four written tone patterns on one word; the output does not differ by pattern (the patterns are the author's, not independently verified as distinct words)

**Flatter-intonation clip:**
- [09_tonal_flat.m4a](data/audio/09_tonal_flat.m4a) - the same sentence as clip 08, spoken with the intention of flatter intonation. Measured pitch variation is lower (F0 standard deviation 1.6 versus 2.7 semitones, one production each), so it is flatter but not shown to be monotone. The output has 3 tone marks and 4 dot-below letters that the reference does not have; whether any of them correspond to pitch in the recording, or whether the dot-below letters are correct spelling, was not checked

**Code-switching:**
- [11_codeswitch_en2ig.m4a](data/audio/11_codeswitch_en2ig.m4a) - English mostly transcribed, with errors; the adjacent Igbo loses marks

## Quick Start

### Installation

```bash
git clone https://github.com/chizkidd/igbo-asr-tonal-evaluation.git
cd igbo-asr-tonal-evaluation
python3 -m pip install -r requirements-analysis.txt   # CPU-only analysis
```

`requirements.txt` is only needed to re-run model inference (`analysis.ipynb`), which needs a GPU and `omnilingual-asr`.

### Run Analysis

```bash
python3 src/evaluate.py data/metadata.csv
jupyter notebook analysis-2.ipynb
```

Or open the corrected analysis in Google Colab (it clones the repository in its first cell):
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chizkidd/igbo-asr-tonal-evaluation/blob/main/analysis-2.ipynb)

The original inference run is [analysis.ipynb](analysis.ipynb); its metric cells predate the corrections described in [CHANGELOG.md](CHANGELOG.md).

## Repository Structure

```
igbo-asr-tonal-evaluation/
├── .github/
│   └── workflows/
│       └── clean-notebooks.yml          # Strips stored notebook outputs
├── data/
│   ├── audio/
│   │   ├── 01_script_names.m4a          # Cross-lingual interference samples
│   │   ├── 02_script_formal.m4a
│   │   ├── 03_script_numbers.m4a
│   │   ├── 04_script_proverb.m4a
│   │   ├── 05_script_slow.m4a
│   │   ├── 06_tonal_akwa.m4a            # Repeated word, four written patterns
│   │   ├── 07_tonal_oke.m4a
│   │   ├── 08_tonal_dense.m4a
│   │   ├── 09_tonal_flat.m4a            # Flatter intonation (same sentence as 08)
│   │   ├── 10_tonal_yoruba.m4a
│   │   ├── 11_codeswitch_en2ig.m4a      # Code-switching samples
│   │   ├── 12_codeswitch_ig2en.m4a
│   │   ├── 13_codeswitch_alternate.m4a
│   │   ├── 14_codeswitch_embedded.m4a
│   │   ├── 15_codeswitch_pidgin.m4a
│   │   ├── 16_context_places.m4a        # Domain-specific samples
│   │   ├── 17_context_food.m4a
│   │   ├── 18_context_proverb.m4a
│   │   ├── 19_context_french.m4a
│   │   ├── 20_context_noise.m4a
│   │   ├── 21_tonal_yoruba_formal.m4a
│   │   ├── igbo_clean.m4a               # Test samples
│   │   ├── igbo_codeswitch.m4a
│   │   └── igbo_tonal.m4a
│   └── metadata.csv                     # References (ground_truth), model outputs, metrics
├── docs/
│   ├── METHODOLOGY.md                   # Detailed research methodology
│   └── REFERENCES.md                    # Full list of academic citations
├── results/
│   └── visualizations/
│       ├── fig1_drop_rate_by_category.png
│       ├── fig2_cer_vs_drop_rate.png
│       ├── fig3_drop_rate_intervals.png
│       ├── fig3_bootstrap_95_ci.png      # Kept from earlier versions; no interval is reported now
│       └── old/                          # Superseded figures, kept for the record
│           ├── fig1_loss_by_category.png
│           ├── fig2_cer_vs_diacritic_loss.png
│           └── fig3_bootstrap_ci.png
├── src/
│   ├── evaluate.py                      # Count-based metrics, legacy alignment, CER
│   ├── utils.py                         # Helper functions
│   └── visualize.py                     # Plotting functions
├── .gitignore
├── analysis-2.ipynb                     # Corrected, offline re-analysis (CPU only)
├── analysis.ipynb                       # Original Colab run (inference + first analysis)
├── CHANGELOG.md
├── LICENSE
├── README.md                            # This file
├── requirements-analysis.txt            # CPU-only analysis dependencies
└── requirements.txt                     # Inference dependencies (GPU, omnilingual-asr)
```

## Documentation

- [**Methodology**](docs/METHODOLOGY.md): research design, metric definitions, error taxonomy, recording protocol and the limits of each metric.
- [**References**](docs/REFERENCES.md): the academic works cited in this project, including ASR fairness, low-resource ASR and Igbo diacritic restoration.
- [**Changelog**](CHANGELOG.md): every correction to the metrics, the statistics and the published claims, with the reason for each one.

The data, the evaluation code and the published claims were audited after the first release: the reported numbers were recalculated, the metric layer was repaired (tone marks and dot-below letters kept apart, language-based groups, base-letter-aware alignment, documented CER normalisation), and each claim was rewritten to stay within what the data can support. The changelog records what changed. The audits check code, artifacts and documents; they are not independent linguistic validation.

## Key Results

### Quantitative Summary

The table below is the original pooled analysis, kept as the historical record. Read it with the headline result above: it pools languages within each task category, it counts dot-below letters as marks, and its position-aware figures come from the legacy alignment rule.

* E = expected marks (in the reference)
* P = marks present in the model output
* D = dropped (counted per clip, then summed)
* H = added (counted per clip, then summed)
* Net = (E - P) / E
* Drop = D / E
* Added = H / E
* DER = (D + H) / E

| Category | Clips | E | Dropped | Added | Net loss | Drop rate | Added rate | DER | Mean CER |
|---|---|---|---|---|---|---|---|---|---|
| **Phonemic Tone Sensitivity** (`tonal_diacritics`) | 6 | 49 | 37 | 7 | 61.2% | **75.5%** | 14.3% | 89.8% | 51.6% |
| Cross-lingual Interference (`script_hallucination`) | 5 | 18 | 2 | 9 | -38.9% | 11.1% | 50.0% | 61.1% | 28.5% |
| Language Boundary (`code_switching`) | 5 | 14 | 7 | 5 | 14.3% | 50.0% | 35.7% | 85.7% | 25.7% |
| Domain-Specific Coverage (`cultural_context`) | 5 | 16 | 5 | 4 | 6.3% | 31.2% | 25.0% | 56.2% | 37.4% |
| **Overall** | **21** | **97** | **51** | **25** | 26.8% | 52.6% | 25.8% | 78.4% | 36.5% |

Those category rates mix languages and two recording chains, and the Igbo and Yoruba clips separate as follows: Igbo clips only (06 to 09) drop 30 of 36 expected marks; Yoruba clips only (10 and 21) drop 7 of 13. With 4 and 2 clips those are descriptive counts, not estimates for a population.

CER in this table is Levenshtein distance over lowercased NFC text with punctuation kept, averaged over clips (36.5%). The `character_error_rate` column in the CSV is `1 - difflib ratio` (33.3% mean); earlier versions of this repository reported that score as CER. The corrected analysis reports CER and WER under stated normalisation profiles, pooled and as a mean over clips, and the values differ by profile (overall strict CER 0.287 pooled, 0.305 mean; base-letters-only 0.180 pooled; Igbo tonal pilot strict 0.416 pooled, 0.121 when every mark is ignored).

Why net loss alone misleads: in the language-boundary category the net loss is 14.3%, but 7 of 14 expected marks were dropped and 5 others were added elsewhere.

### Position-aware Estimate

Count-based metrics cannot tell a correct mark from a wrong mark, because a clip with the right number of marks on the wrong letters scores as no change. Aligning reference and output on base letters and classifying each mark gives a position-aware estimate.

**Historical result (legacy rule, pooled languages, all marks):** overall 33 correct, 7 wrong, 57 missing and 31 inserted; tonal-category clips 4 correct, 7 wrong, 38 missing, 8 inserted. The legacy rule does not check that the aligned base letters agree, so it can credit a mark sitting on a mis-heard letter, and it treats tone marks and dot-below letters as one mark set. Its missing count (57) differs from the per-clip dropped count (51) because the two methods count differently.

**Repaired result (base-letter-aware, tone marks only, Igbo tonal pilot clips 06 to 09):** of 32 reference tone marks, 0 correct, 0 wrong, 28 missing on a matching base letter, 4 on a base letter the model got wrong, 0 on a deleted letter; 3 tone marks inserted, all in clip 09, whose reference has no marks. This is still an estimate: if the model mis-hears a letter, a mark can look missing because of the letter error rather than the tone.

### Uncertainty: no interval is reported

The unit of independent data is the clip, so any resampling is over clips, not individual marks. A rate can carry an interval only when the group is a reporting unit (a language-based analysis group, not a pooled task category and not the overall row) **and** at least 10 of its clips carry an expected mark. No group here qualifies: the largest has 8 clips, 7 of them with marks. Each rate is therefore published as a count and a pooled rate.

Earlier versions of this repository quoted clip-level bootstrap intervals (tonal 75.5% [57.1%, 89.7%]) and paired bootstrap differences between categories. Both are withdrawn: they resampled 5 or 6 clips, they compared aggregates that mix languages and recording chains, and they read as tests where none was pre-specified. The interval figure in `results/visualizations/` is kept from those earlier versions and is no longer a reported result. `CHANGELOG.md` records the withdrawal.

### Caveats on the "added" marks

Dot-below letters (ọ, ị, ụ) are counted as marks. Some references omit dot-below marks that standard orthography would normally include (for example clips 04 and 09), and clips 08 and 09, which are the same sentence, are written under different conventions. No documented standard source was consulted for the references, so an output with ọ or ị where the reference has none is not necessarily an error. Tone-only counts avoid this: the model wrote 4 tone marks in the cross-lingual clips and 5 in the tonal-category clips (3 in the Igbo clips, 2 in the Yoruba clips).

## Example: Repeated Word With Four Written Tone Patterns

**Reference (the author's written patterns):** "akwa, akwa, akwa. Akwà, akwà, akwà. Àkwà, àkwà, àkwà. Ákwá, ákwá, ákwá."
(Four written tone patterns on one base string. They have not been independently verified as distinct words.)

**Model Output:** "akua akua akua akua akwa akwa akwa akua akwa ọkua ọkua ọkua"

**Observation:** the reference carries 15 marked letters, the output 3, and all 3 in the output are dot-below letters (`ọ`); the output has no tone marks and does not differ by written pattern. A pitch check on the recording (exploratory, one production) did not show four distinct contours, which neither confirms nor refutes the written marks. Word glosses were removed because no independent check of the tone-to-meaning assignment is available.

## Methodology

### Model Evaluated

- **Model:** [facebook/omniASR-CTC-1B](https://huggingface.co/facebook/omniASR-CTC-1B)
- **Parameters:** 975M
- **Architecture:** CTC-based ASR (wav2vec2-style)
- **Languages:** 1,600+ (including Igbo)

### Recording Details

- **Speaker:** Author, native speaker of Afikpo Igbo (Ebonyi State); single speaker, not independently verified
- **Device:** iPhone SE 2nd Generation
- **Format:** M4A (AAC codec). Two export chains are present: clips 01 to 05 are 16 kHz with digital-silence gaps (about 36 to 39% exactly-zero samples), clips 06 to 21 are 48 kHz. The cause of the difference is unverified, and it is confounded with category, because clips 01 to 05 are the whole cross-lingual category
- **Duration:** 3.9 to 16.7 seconds per sample
- **References:** written by the speaker, who is also the only annotator. Tone and dot-below placement were not independently verified and were not checked against a documented standard source. No inter-annotator agreement exists

### Metrics

- **Marks counted:** letters carrying grave, acute, macron or dot-below (one count per letter, even with dot plus tone); tone-only and dot-below counts are reported separately in the corrected analysis
- **Net loss, drop rate, added rate, DER:** defined in the table above, with D and H computed per clip. These are count-based
- **Position-aware classification:** base-letter-aware alignment for the corrected analysis; the legacy rule for the historical figures, which does not check base letters
- **Uncertainty:** a rate carries an interval only for a reporting unit with at least 10 informative clips, so none of the rates here carries one; each is published as a count and a pooled rate
- **CER:** Levenshtein distance divided by reference length. The historical table uses lowercased NFC text with punctuation kept; the corrected analysis states its normalisation profiles (`strict`, `tone_stripped`, `base_letters`)

Five things are easy to confuse and are kept apart here: count-based mark metrics, position-aware alignment, transcription accuracy (CER and WER), annotation validity (whether each reference mark is right), and acoustic tonal sensitivity (whether the model responds to pitch). Only the first three are measured, and none of them tests the last two.

### Provenance and Environment

- **Original inference run:** Google Colab, NVIDIA T4, Python 3.12, omnilingual-asr 0.1.0, torch 2.8.0, pandas 2.2.2, 2026-03-01, as recorded in the executed notebook output. The notebook also contains a `torch==2.1.0` install command; that install did not succeed and the recorded run used `torch 2.8.0`.
- **Executed notebook:** `analysis.ipynb` is the original run. Its metric cells keep the original definitions and are not the corrected analysis; `analysis-2.ipynb` is the corrected, offline re-analysis.
- **`lang` argument:** the inference call passed a language code per clip, but `omnilingual-asr` 0.1.0 ignores `lang` for CTC models, so it did not affect decoding.
- **Not stored:** the raw model outputs, inference logs and model revision are not in the repository (`data/metadata.csv` is the only record of the outputs), and the exact waveform the model received cannot be reproduced bit for bit (the Hugging Face WAV files are the same recordings but not bit-identical to a fresh conversion for clips 06 to 21).
- **Reproducibility of the headline count:** the base-letter-aware recount behind the 0 of 32 result is not yet part of `analysis-2.ipynb` or `src/evaluate.py`; those reproduce the count-based metrics and the legacy alignment. Until the recount is committed, treat 0 of 32 as a reported result rather than a value regenerated by the commands below.

### Limits that will not be resolved

No independent fluent-Igbo reviewer is available for this project. As a result, the correctness of every reference tone mark, whether the written tone patterns in clips 06 and 07 are distinct words, whether dot-below letters missing from some references are errors or a convention, and whether any mark the model added corresponds to the audio all remain unknown. Every figure in this repository is conditional on the author's references.

See [METHODOLOGY.md](docs/METHODOLOGY.md) for the detailed research design.

## Usage

### Run the Full Analysis

```bash
jupyter notebook analysis-2.ipynb   # corrected, offline, CPU only
```

### Use the Evaluation Library

```python
from src.evaluate import compute_all_metrics, calculate_der, aligned_table
from src.visualize import plot_loss_by_category
from src.utils import load_metadata

df = compute_all_metrics(load_metadata("data/metadata.csv"))

print(calculate_der(df))          # net, drop, added, DER (per-clip D and H)
print(aligned_table(df))          # correct / wrong / missing / inserted (legacy alignment)

plot_loss_by_category(df, output_path="results/visualizations/fig1.png")
```

### Reproduce Results

```bash
python src/evaluate.py data/metadata.csv      # metrics and aligned counts from the CSV
python src/visualize.py data/metadata.csv results/visualizations
```

Both commands read `data/metadata.csv`; no GPU is needed. They reproduce the count-based and legacy alignment figures in the table above, not the base-letter-aware recount described under Provenance. `data/metadata.csv` is the only record of the model outputs, since the raw outputs were not stored.

## Citation

If you use the dataset, please cite:

```bibtex
@misc{obasi2026igbo,
  title={Igbo Blind Spot Dataset for omniASR-CTC-1B: Systematic Evaluation of Tonal Diacritic Loss},
  author={Obasi, Chizoba},
  year={2026},
  publisher={HuggingFace},
  howpublished={\url{https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots}},
  note={Model evaluated: facebook/omniASR-CTC-1B (975M parameters)}
}
```

## Related Work

- **Dataset:** [HuggingFace Hub](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots)
- **Model:** [omniASR-CTC-1B](https://huggingface.co/facebook/omniASR-CTC-1B)
- **Paper:** [Meta AI - Omnilingual ASR (arXiv:2511.09690)](https://arxiv.org/abs/2511.09690)

For the works cited by this project, see [**References**](docs/REFERENCES.md).

## Future Work

1. **Independent review of the references.** Every reference was written by the speaker and has not been checked by a second fluent speaker. The review protocol is written but not executed, so the results stay conditional on those references.
2. **Multi-speaker evaluation** (10+ speakers across dialects), since clips from one speaker are not independent of each other.
3. **Comparative model audit** (Whisper, MMS, USM, Azure Speech) on the same clips.
4. **Acoustic test of the "text prior" reading.** A preregistered design exists: matched tone pairs plus pitch-manipulated and monotone controls, with references written to a fixed orthography convention. It has not been run.
5. **A second recording set** from a written script with fixed orthography, so that the same sentence and the same word forms are recorded under controlled pitch conditions. The script is written and nothing has been recorded from it yet.
6. **Fine-tuning intervention** with tone-annotated data.

## License

- **Code:** MIT License, see [LICENSE](LICENSE). MIT covers code only.
- **Dataset (audio, transcripts, annotations, metadata, model outputs):** CC BY 4.0 (attribution required), as on the [dataset card](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots).
- **Model evaluated:** `facebook/omniASR-CTC-1B`, Apache License 2.0.

## Author

**Chizoba Obasi**
[HuggingFace](https://huggingface.co/Chiz) | [GitHub](https://github.com/chizkidd)

---
