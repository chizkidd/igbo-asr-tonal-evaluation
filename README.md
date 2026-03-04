# Igbo ASR Tonal Evaluation

[![Dataset](https://img.shields.io/badge/🤗%20Dataset-omniASR--igbo--blindspots-blue)](https://huggingface.co/datasets/chiz/omniASR-igbo-blindspots)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

Systematic evaluation of tonal fidelity in facebook/omniASR-CTC-1B when processing Igbo, a tonal Niger-Congo language with ~45 million speakers.

## Overview

This project reveals systematic tonal diacritic loss in a state-of-the-art multilingual ASR model:
- **75.5% diacritic loss** on tonal markers (bootstrap 95% CI: [57.1%, 89.7%])
- **Minimal pair collapse**: Model cannot distinguish phonemically contrastive tones
- **Orthographic bias**: Model hallucinates tone marks on monotone speech

**Key Insight:** The model appears to generate diacritics probabilistically based on lexical priors rather than acoustic conditioning.

## Dataset

**21 audio samples** across 4 error categories:
1. Cross-lingual Orthographic Interference (5 samples)
2. Phonemic Tone Sensitivity (6 samples)
3. Language Boundary Effects (5 samples)
4. Domain-Specific Lexical Coverage (5 samples)

**[View Dataset on HuggingFace](https://huggingface.co/datasets/chiz/omniASR-igbo-blindspots)**

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
│   └── METHODOLOGY.md                    # Detailed research methodology
├── results/
│   └── visualizations/
│       ├── fig1_loss_by_category.png
│       ├── fig2_cer_vs_diacritic_loss.png
│       └── fig3_bootstrap_ci.png
├── src/
│   ├── evaluate.py                       # Evaluation metrics (DER, bootstrap CIs)
│   ├── visualize.py                      # Plotting functions
│   └── utils.py                          # Helper functions
├── .gitignore
├── analysis.ipynb                        # Full analysis notebook
├── LICENSE
├── README.md                             # This file
└── requirements.txt                      # Python dependencies
```



## Key Results

### Quantitative Summary

| Category | Samples | Diacritic Loss | Avg CER |
|----------|---------|----------------|---------|
| **Phonemic Tone Sensitivity** | 6 | **75.5%** | 50.6% |
| Cross-lingual Interference | 5 | -38.9% (hallucination) | 28.8% |
| Domain-Specific Coverage | 5 | 6.3% | 30.1% |
| Language Boundary Effects | 5 | 14.3% | 20.0% |
| **Overall** | **21** | **26.8%** | **32.5%** |

### Bootstrap Confidence Intervals

- **Tonal category:** 75.5% (95% CI: [57.1%, 89.7%])
- **Overall:** 52.6% (95% CI: [30.3%, 69.7%])

Even the worst-case lower bound (57.1%) indicates severe tonal degradation.

## Example: Tonal Minimal Pairs

**Input:** "akwa, akwa, akwa. Akwà, akwà, akwà. Àkwà, àkwà, àkwà. Ákwá, ákwá, ákwá."  
(4 distinct Igbo words with different meanings)

**Model Output:** "akua akua akua akua akwa akwa akwa akua akwa ọkua ọkua ọkua"  
(Random variations, semantic distinctions lost)

**Impact:** 
- akwà (cloth) → akwa (could mean "crying")
- àkwà (egg) → akwa (meaning lost)
- ákwá (bridge) → akua (wrong word)

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
- **DER (Diacritic Error Rate):** Captures dropped + hallucinated tone marks
- **Bootstrap CIs:** 10,000 iterations at utterance level
- **CER (Character Error Rate):** Standard transcription accuracy

See [METHODOLOGY.md](docs/METHODOLOGY.md) for detailed research design.

## Usage

### Run the Full Analysis
```bash
jupyter notebook analysis.ipynb
```

### Use the Evaluation Library
```python
from src.evaluate import compute_all_metrics, bootstrap_ci
from src.visualize import plot_loss_by_category
from src.utils import load_metadata

# Load data
df = load_metadata("data/metadata.csv")

# Compute metrics
df = compute_all_metrics(df)

# Generate visualizations
plot_loss_by_category(df, output_path="results/visualizations/fig1.png")
```

### Reproduce Results
To regenerate all results from scratch:
```bash
jupyter notebook analysis.ipynb  # Run all cells
# Results will be saved to results/
```

## Citation

If you use this dataset or code, please cite:

```bibtex
@misc{obasi2026igbo,
  title={Igbo Blind Spot Dataset for omniASR-CTC-1B: Systematic Evaluation of Tonal Diacritic Loss},
  author={Obasi, Chizoba},
  year={2026},
  publisher={HuggingFace},
  howpublished={\url{https://huggingface.co/datasets/chiz/omniASR-igbo-blindspots}},
  note={Model evaluated: facebook/omniASR-CTC-1B (975M parameters)}
}
```

## Related Work

- **Dataset:** [HuggingFace Hub](https://huggingface.co/datasets/chiz/omniASR-igbo-blindspots)
- **Model:** [omniASR-CTC-1B](https://huggingface.co/facebook/omniASR-CTC-1B)
- **Paper:** [Meta AI - Omnilingual ASR (arXiv:2511.09690)](https://arxiv.org/abs/2511.09690)

## Future Work

1. **Scale to multi-speaker evaluation** (10+ speakers across dialects)
2. **Comparative model audit** (Whisper, MMS, USM, Azure Speech)
3. **Fine-tuning intervention** with tone-annotated data
4. **Downstream impact studies** in voice assistants

## License

- **Code:** MIT License
- **Audio recordings:** CC-BY-4.0 (attribution required)
- **Metadata/annotations:** CC0 (public domain)

See [LICENSE](LICENSE) for details.

## Author

**Chizoba Obasi**  
[HuggingFace](https://huggingface.co/chiz) | [GitHub](https://github.com/chizkidd)

---

*Systematic evaluation of ML model blind spots using native speaker expertise.*