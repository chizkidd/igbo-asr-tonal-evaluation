# Igbo ASR Tonal Evaluation

[![Dataset](https://img.shields.io/badge/🤗%20Dataset-omniASR--igbo--blindspots-blue)](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots)
[![Docs](https://img.shields.io/badge/docs-Methodology%20%26%20References-blue)](docs/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Colab to GitHub Notebook Metadata Sanitizer](https://github.com/chizkidd/igbo-asr-tonal-evaluation/actions/workflows/clean-notebooks.yml/badge.svg)](https://github.com/chizkidd/igbo-asr-tonal-evaluation/actions/workflows/clean-notebooks.yml)
![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.igbo-asr-tonal-evaluation)
![Hugging Face Downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fhuggingface.co%2Fapi%2Fdatasets%2FChiz%2FomniASR-igbo-blindspots%3Fexpand%255B%255D%3Ddownloads%26expand%255B%255D%3DdownloadsAllTime&query=%24.downloadsAllTime&label=HuggingFace%20Downloads&color=blue)

Systematic evaluation of tonal fidelity in facebook/omniASR-CTC-1B when processing Igbo, a tonal Niger-Congo language with ~45 million speakers.

## Overview

This is a small diagnostic study (21 clips, one speaker) of how `omniASR-CTC-1B` handles Igbo tone and dot-below marks:
- **Tonal clips drop most marks:** 37 of 49 expected marks are missing (**drop rate 75.5%**, clip-level bootstrap 95% CI [57.1%, 89.7%]).
- **Tone marks nearly vanish in the tonal clips:** the reference has 43 tone-bearing letters, the model output has 5.
- **Marks are also added:** 25 marks appear where the reference has none or fewer (**added rate 25.8%** overall), so net loss (26.8%) understates how often the output disagrees with the reference. Pooled **DER is 78.4%**.
- **Minimal pairs collapse:** on the akwa and oke clips the output carries no tone marks at all.

**Reading these results:** the pattern is *consistent with* the model leaning on text-like priors rather than tone acoustics, but this study cannot show that. It has one speaker, 21 clips, a single annotator, and no comparison model. Treat it as a blind-spot probe, not a measurement of prevalence.

Explore the numbers interactively: **Igbo tone-loss explorer** in [ml-viz](https://github.com/chizkidd/ml-viz).

## Dataset

**21 audio samples** across 4 error categories:
1. Cross-lingual Orthographic Interference (5 samples)
2. Phonemic Tone Sensitivity (6 samples)
3. Language Boundary Effects (5 samples)
4. Domain-Specific Lexical Coverage (5 samples)

**[View Dataset on HuggingFace](https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots)**

### Listen to Examples

Audio files are included in this repository (M4A format). Click to play directly on GitHub:

**Tonal Minimal Pairs:**
- [06_tonal_akwa.m4a](data/audio/06_tonal_akwa.m4a) - 4 different words collapsed to random outputs

**Monotone Hallucination:**
- [09_tonal_flat.m4a](data/audio/09_tonal_flat.m4a) - Flat speech, model ADDED tones that weren't spoken

**Code-Switching:**
- [11_codeswitch_en2ig.m4a](data/audio/11_codeswitch_en2ig.m4a) - English perfect, Igbo loses tones

## Quick Start

### Installation

```bash
git clone https://github.com/chizkidd/igbo-asr-tonal-evaluation.git
cd igbo-asr-tonal-evaluation
pip install -r requirements.txt
```

### Run Analysis

```bash
jupyter notebook analysis.ipynb
```

Or open in Google Colab:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chizkidd/igbo-asr-tonal-evaluation/blob/main/analysis.ipynb)

## Repository Structure

```
igbo-asr-tonal-evaluation/
├── data/
│   ├── audio/
│   │   ├── 01_script_names.m4a           # Cross-lingual interference samples
│   │   ├── 02_script_formal.m4a
│   │   ├── 03_script_numbers.m4a
│   │   ├── 04_script_proverb.m4a
│   │   ├── 05_script_slow.m4a
│   │   ├── 06_tonal_akwa.m4a            # Tonal minimal pairs
│   │   ├── 07_tonal_oke.m4a
│   │   ├── 08_tonal_dense.m4a
│   │   ├── 09_tonal_flat.m4a            # Monotone control (key diagnostic)
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
│   └── metadata.csv                      # Ground truth, model outputs, metrics
├── docs/
│   ├── METHODOLOGY.md                    # Detailed research methodology
│   └── REFERENCES.md                     # Full list of academic citations
├── results/
│   └── visualizations/
│       ├── fig1_drop_rate_by_category.png
│       ├── fig2_cer_vs_drop_rate.png
│       └── fig3_bootstrap_ci.png
├── src/
│   ├── evaluate.py                       # Evaluation metrics (DER, bootstrap CIs)
│   ├── visualize.py                      # Plotting functions
│   └── utils.py                          # Helper functions
├── .gitignore
├── analysis.ipynb                        # Original Colab run (inference + first analysis)
├── analysis-2.ipynb                      # Corrected, offline re-analysis
├── CHANGELOG.md
├── LICENSE
├── README.md                             # This file
└── requirements.txt                      # Python dependencies
```

## Documentation

- [**Methodology**](docs/METHODOLOGY.md) – Detailed research design, metric definitions (DER, bootstrap CIs), error taxonomy, and recording protocol.
- [**References**](docs/REFERENCES.md) – Full list of academic works cited in this project, including papers on ASR fairness, low-resource languages, and Igbo diacritic restoration.

## Key Results

### Quantitative Summary

E = expected marks, D = dropped, H = added (both counted per clip, then summed). Net = (E - P) / E. Drop = D / E. Added = H / E. DER = (D + H) / E.

| Category | Clips | E | Dropped | Added | Net loss | Drop rate | Added rate | DER | Mean CER |
|---|---|---|---|---|---|---|---|---|---|
| **Phonemic Tone Sensitivity** (`tonal_diacritics`) | 6 | 49 | 37 | 7 | 61.2% | **75.5%** | 14.3% | 89.8% | 51.6% |
| Cross-lingual Interference (`script_hallucination`) | 5 | 18 | 2 | 9 | -38.9% | 11.1% | 50.0% | 61.1% | 28.5% |
| Language Boundary (`code_switching`) | 5 | 14 | 7 | 5 | 14.3% | 50.0% | 35.7% | 85.7% | 25.7% |
| Domain-Specific Coverage (`cultural_context`) | 5 | 16 | 5 | 4 | 6.3% | 31.2% | 25.0% | 56.2% | 37.4% |
| **Overall** | **21** | **97** | **51** | **25** | 26.8% | 52.6% | 25.8% | 78.4% | 36.5% |

CER here is true character error rate (Levenshtein, lowercased, NFC), mean over clips. Older versions of this repo reported `1 - difflib ratio` under the name CER; see [CHANGELOG](CHANGELOG.md).

Why net loss alone misleads: in the language-boundary category the net loss is 14.3%, but 7 of 14 expected marks were dropped and 5 others were added elsewhere.

### Bootstrap Confidence Intervals (drop rate, resampling clips)

| Group | Drop rate | 95% CI |
|---|---|---|
| Tonal | 75.5% | [57.1%, 89.7%] |
| Overall | 52.6% | [30.3%, 69.7%] |
| Language boundary | 50.0% | [0%, 91.7%] |
| Domain | 31.2% | [0%, 83.3%] |
| Cross-lingual | 11.1% | [0%, 27.3%] |

The unit of independent data is the clip, so clips are resampled (not individual marks). With 5 or 6 clips per category the intervals for the non-tonal categories are very wide. The tonal interval overlaps the language-boundary and domain intervals, and a paired bootstrap of the difference in drop rate gives tonal minus language boundary 25.5 points [-18.9, 78.6] and tonal minus domain 44.3 points [-9.4, 80.6]. Only the contrast with cross-lingual (64.4 points [40.5, 85.7]) excludes zero. So the data support "tonal clips drop many marks" but not "tonal clips drop more than every other category".

### Position-aware estimate

Counts cannot tell a correct mark from a wrong mark. Aligning reference and output on base letters and classifying each mark gives, overall, 33 correct, 7 wrong, 57 missing and 31 inserted (tonal clips: 4 correct, 7 wrong, 38 missing, 8 inserted). This is an estimate: if the model mis-hears a letter, a mark can look missing because of the letter error, not the tone. See `analysis-2.ipynb`.

### Caveats on the "added" marks

Dot-below letters (ọ, ị, ụ) are counted as marks. In some clips the reference is written without dots that standard orthography would include (for example clip 09, `O na-eri oji n'ututu`), so a model output with ọ or ị there is not necessarily a hallucination. Tone-only counts avoid this: the model wrote 4 tone marks in the cross-lingual clips and 5 in the tonal clips.

## Example: Tonal Minimal Pairs

**Input:** "akwa, akwa, akwa. Akwà, akwà, akwà. Àkwà, àkwà, àkwà. Ákwá, ákwá, ákwá."  
(4 distinct Igbo words with different meanings)

**Model Output:** "akua akua akua akua akwa akwa akwa akua akwa ọkua ọkua ọkua"  
(Random variations, semantic distinctions lost)

**Impact:** the reference carries 15 marked letters, the output 3, and the four tone patterns are not distinguished. (Word glosses were removed from this section pending a check against a standard Igbo reference; the tone-to-meaning assignment previously listed here should be verified before it is cited.)

## Methodology

### Model Evaluated
- **Model:** [facebook/omniASR-CTC-1B](https://huggingface.co/facebook/omniASR-CTC-1B)
- **Parameters:** 975M
- **Architecture:** CTC-based ASR (wav2vec2-style)
- **Languages:** 1,600+ (including Igbo)

### Recording Details
- **Speaker:** Native Igbo speaker (Afikpo dialect, Ebonyi State)
- **Device:** iPhone SE 2nd Generation
- **Format:** M4A (AAC codec, original iPhone Voice Memos format)
- **Duration:** 4-15 seconds per sample

### Metrics
- **Marks counted:** letters carrying grave, acute, macron or dot-below (one count per letter, even with dot plus tone)
- **Net loss, drop rate, added rate, DER:** defined in the table above, D and H per clip
- **Bootstrap CIs:** 10,000 resamples of clips, percentile interval
- **CER:** Levenshtein distance / reference length, lowercased, NFC

See [METHODOLOGY.md](docs/METHODOLOGY.md) for detailed research design.

## Usage

### Run the Full Analysis
```bash
jupyter notebook analysis.ipynb
```

### Use the Evaluation Library
```python
from src.evaluate import (compute_all_metrics, calculate_der, bootstrap_ci,
                          stat_drop_rate, aligned_table)
from src.visualize import plot_loss_by_category
from src.utils import load_metadata

df = compute_all_metrics(load_metadata("data/metadata.csv"))

print(calculate_der(df))                       # net, drop, added, DER (per-clip D and H)
print(bootstrap_ci(df, stat_drop_rate))        # dict: point, boot_mean, lo, hi, n_undefined
print(aligned_table(df))                       # correct / wrong / missing / inserted

plot_loss_by_category(df, output_path="results/visualizations/fig1.png")
```

### Reproduce Results
To regenerate all results from scratch:
```bash
python src/evaluate.py data/metadata.csv      # metrics, CIs, aligned counts from the CSV
python src/visualize.py data/metadata.csv results/visualizations
# or run analysis-2.ipynb (offline, uses data/metadata.csv; no GPU needed)
# analysis.ipynb is the original run that produced the model outputs (needs a GPU)
```

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

For a full bibliography of referenced academic works, see [**References**](docs/REFERENCES.md).

## Future Work

1. **Second annotator** on the reference transcripts (all ground truth is currently one person's)
2. **Multi-speaker evaluation** (10+ speakers across dialects), since clips from one speaker are not independent of each other
3. **Comparative model audit** (Whisper, MMS, USM, Azure Speech) on the same clips
4. **Acoustic test of the "text prior" reading:** matched tone-minimal pairs plus pitch-manipulated and monotone controls, with references written to a fixed orthography convention
5. **Fine-tuning intervention** with tone-annotated data

## License

- **Code:** MIT License
- **Audio recordings:** CC-BY-4.0 (attribution required)
- **Metadata/annotations:** CC0 (public domain)

See [LICENSE](LICENSE) for details.

## Author

**Chizoba Obasi**  
[HuggingFace](https://huggingface.co/Chiz) | [GitHub](https://github.com/chizkidd)

---
