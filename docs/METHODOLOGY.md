# Methodology

## Research Design

This study uses a **controlled diagnostic evaluation** approach to identify systematic blind spots in multilingual ASR systems.

### Why This Approach?

Traditional ASR benchmarks use large-scale datasets (1000s of hours) that:
- Measure aggregate performance (WER/CER)
- May miss systematic failures on linguistically meaningful distinctions
- Lack native speaker validation

Our approach:
- **21 carefully designed samples** targeting specific failure modes
- **Native speaker ground truth** for tonal accuracy
- **Minimal pairs** to test phonemic distinctions
- **Control conditions** (monotone speech, code-switching, other languages)

This follows methodological frameworks from:
- Koenecke et al. (2020): Demographic ASR fairness evaluation
- EMNLP 2024: Dialect bias in ASR (controlled single-speaker designs)

---

## Sample Design

### Category 1: Cross-lingual Orthographic Interference (5 samples)

**Hypothesis:** Model applies incorrect orthographic conventions from other languages.

**Design:**
- Utterances with NO diacritics in ground truth
- Test if model adds incorrect tone marks

**Samples:**
1. Personal names (Nigerian names without tones)
2. Formal greetings (standard phrases)
3. Numeric sequences (numbers in Igbo)
4. Proverbs (well-known sayings)
5. Slow prosody (testing if speech rate affects hallucination)

**Expected:** 0% diacritic loss (nothing to lose)  
**Observed:** -38.9% (model added diacritics that don't exist)

---

### Category 2: Phonemic Tone Sensitivity (6 samples)

**Hypothesis:** Model cannot distinguish phonemically contrastive tones.

**Design:**
- Tonal minimal pairs (same phonemes, different tones = different words)
- Dense tone marking (high diacritic density)
- **Monotone control** (flat intonation, no tonal variation)
- Yoruba controls (closely related tonal language)

**Samples:**
1. akwa/akwà/àkwà/ákwá (crying/cloth/egg/bridge)
2. oke/òkè/ọkè (big/rat/portion)
3. Dense tone marks (multiple tones per word)
4. **Monotone speech** (diagnostic for orthographic bias)
5-6. Yoruba (control language)

**Key Test (File 09 - Monotone):**
- Spoke "O na-eri oji n'ututu" with deliberately FLAT intonation
- If model uses acoustics → should produce few/no diacritics
- **Result:** Model ADDED tone marks → evidence of orthographic bias

**Expected:** Low loss if model uses acoustic information  
**Observed:** 75.5% loss + hallucination on monotone

---

### Category 3: Language Boundary Effects (5 samples)

**Hypothesis:** Code-switching disrupts language-specific processing.

**Design:**
- English-Igbo code-switching (common in Nigerian speech)
- Different switching patterns (embedded vs. alternation)
- Nigerian Pidgin control

**Samples:**
1. English → Igbo embedding
2. Igbo → English embedding
3. Sentence-level alternation
4. Diacritics in English context
5. Nigerian Pidgin

**Expected:** Boundary effects where languages switch  
**Observed:** English perfect, adjacent Igbo loses tones (14.3%)

---

### Category 4: Domain-Specific Lexical Coverage (5 samples)

**Hypothesis:** Model struggles with culturally specific terms outside training distribution.

**Design:**
- Nigerian place names
- Igbo food terms
- Idiomatic expressions
- High-resource language control (French)
- Noise robustness test

**Expected:** Higher errors on out-of-distribution terms  
**Observed:** 6.3% loss (best preservation) but 30% CER (word-level errors)

---

## Recording Protocol

### Equipment
- **Device:** iPhone SE 2nd Generation (Voice Memos app)
- **Format:** M4A (AAC codec) → converted to 16kHz mono WAV
- **Environment:** Quiet indoor setting
- **Duration:** 4-15 seconds per sample

### Speaker Details
- **Native speaker:** Igbo (Nigerian)
- **Dialect:** Afikpo Igbo (Ebonyi State)
- **Background:** Grew up in multilingual Northern Nigerian environment
- **Both parents:** From Afikpo

### Quality Control
- All transcriptions verified by speaker
- Diacritics placed according to standard Igbo orthography
- Ambiguous cases resolved via linguistic references

---

## Evaluation Metrics

### 1. Diacritic Error Rate (DER)

$$
\text{DER} = \frac{D + H}{E}
$$

Where:
- E = expected diacritics (ground truth)
- D = dropped diacritics = max(0, E - P)
- H = hallucinated diacritics = max(0, P - E)
- P = produced diacritics (model output)

**Why this metric?**
- Standard CER conflates spacing, capitalization, and tonal errors
- DER isolates tone-related failures
- Normalized by expected (E) to reflect departure from target system

**Note:** DER can exceed 100% when hallucinations are substantial.

### 2. Raw Diacritic Drop Rate (RDD)

$$
\text{RDD} = \frac{D}{E}
$$

Simple proportion of expected tone marks not produced.

### 3. Bootstrap Confidence Intervals

**Why bootstrap?**
- Small sample size (N=21)
- Accounts for sampling variability
- Provides uncertainty quantification

**Method:**
- 10,000 resampling iterations
- **Utterance-level resampling** (not event-level)
- Percentile method for 95% CI

**Implication:** Bootstrap estimates may differ from raw counts due to unequal diacritic distribution across samples.

Example:
- Raw count: 30/49 = 61.2%
- Bootstrap mean: 75.5%
- 95% CI: [57.1%, 89.7%]

The bootstrap mean can exceed the raw percentage because resampling at utterance level gives more weight to samples with extreme loss rates.

### 4. Character Error Rate (CER)

Standard metric for comparison:

$$
\text{CER} = \frac{\text{Levenshtein distance}(\text{ref}, \text{hyp})}{\text{length}(\text{ref})}
$$

Computed using `difflib.SequenceMatcher` for character-level similarity.

---

## Statistical Analysis

### Hypothesis Testing

**Null hypothesis:** Diacritic loss in tonal category ≤ other categories  
**Alternative:** Tonal category shows higher loss

**Test:** Bootstrap confidence intervals  
**Result:** Tonal CI [57.1%, 89.7%] does not overlap with other categories  
**Conclusion:** Tonal degradation is statistically distinguishable

### Robustness Check

Even under worst-case assumptions (lower bound of CI):
- Tonal loss: 57.1% (still >50%)
- Overall loss: 30.3% (still substantial)

This suggests effects are unlikely to be sampling artifacts.

---

## Limitations

### Sample Size
- **N=21** is small for prevalence estimation
- Sufficient for blind spot discovery (proof-of-concept)
- Future work requires 100+ samples across multiple speakers

### Single Speaker
- Limits generalizability across dialects
- Controls for speaker variability (methodological choice)
- Allows unambiguous ground truth

### Dialectal Coverage
- Afikpo Igbo only
- Does not test: Owerri, Onitsha, Enugu, Nsukka varieties
- Igbo has dialectal variation in tone patterns

### Clean Audio
- Primarily quiet recordings
- Limited noise robustness testing (1 sample only)
- Real-world performance may differ

### What This Study Does NOT Claim
- Universal failure on all Igbo speech
- Absence of tone modeling in architecture
- Unique disadvantage of Igbo vs. other low-resource languages
- Generalizability to all speakers/dialects

---

## Reproducibility

All code, data, and analysis available at:
- **Code:** https://github.com/chizkidd/igbo-asr-tonal-evaluation
- **Dataset:** https://huggingface.co/datasets/chiz/omniASR-igbo-blindspots

### Environment
- Google Colab (NVIDIA Tesla T4, 15GB VRAM)
- omnilingual-asr==0.1.0
- torch==2.1.0
- Python 3.12

### Model Inference
```python
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
pipeline = ASRInferencePipeline(model_card="omniASR_CTC_1B")
transcription = pipeline.transcribe(inp=[audio_path], lang=["ibo_Latn"])
```

---

## Ethical Considerations

### Privacy
- All recordings self-made by author
- No third-party identifiable information

### Cultural Sensitivity
- Proverbs and idioms are common knowledge
- No sacred or restricted content
- Community benefit: Open-source release for Igbo NLP research

### Labor
- No exploitation (self-recorded)
- Future work will compensate speakers appropriately ($15-20/hour)

Follows ACM Code of Ethics and Professional Conduct for responsible AI research.
