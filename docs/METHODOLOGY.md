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
- Utterances whose reference carries few or no tone marks (4 of the 5 reference transcripts carry at least one counted mark, 18 in total, mostly dot-below letters such as ọ, ị, ụ)
- Test if the model adds marks that the reference does not have

**Samples:**
1. Personal names (Nigerian names without tones)
2. Formal greetings (standard phrases)
3. Numeric sequences (numbers in Igbo)
4. Proverbs (well-known sayings)
5. Slow prosody (testing if speech rate affects hallucination)

**Expected:** few marks to lose, so any added marks stand out  
**Observed:** 18 expected, 25 produced; 2 dropped and 9 added (net loss -38.9%, drop rate 11.1%, added rate 50.0%). Of the produced marks, 4 are tone marks and the rest dot-below letters, so part of the "addition" is orthographic convention rather than tone.

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
- Reference is written with no marks at all (standard orthography would normally include dot-below on ọ, ị, ụ)
- **Result:** the output has 7 counted marks, of which 3 are tone marks (acute on jí, tú, tú) and 4 are dot-below letters

**Reading:** consistent with the model adding marks from text priors, but this is one clip, and the dot-below additions may simply be correct orthography. It is a lead, not evidence of "orthographic bias".

**Category observed:** drop rate 75.5% (37 of 49 expected marks), added rate 14.3% (7 marks), net loss 61.2%, DER 89.8%.

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
**Observed:** net loss 14.3%, but 7 of 14 expected marks dropped (drop rate 50.0%) and 5 added (added rate 35.7%); the net figure hides both.

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
**Observed:** net loss 6.3%, but 5 of 16 expected marks dropped (31.2%) and 4 added (25.0%); mean CER 37.4% (word-level errors)

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
- DER isolates mark-related disagreement
- Normalized by expected (E) to reflect departure from the reference

**Important:** D and H are computed **per clip** and then summed. (An earlier version of `calculate_der` netted E and P over the whole pool, so additions in one clip cancelled drops in another and the "DER" it printed was really net loss.)

**Note:** DER can exceed 100% when additions are substantial. DER counts a mark in the wrong place the same as an extra mark; see the aligned estimate below.

### What counts as a mark

One NFD grapheme cluster (letter plus combining marks) carrying grave (U+0300), acute (U+0301), macron (U+0304) or dot-below (U+0323). A letter with dot-below and a tone counts once. This reproduces `diacritics_expected` and `diacritics_produced` for all 21 rows of `metadata.csv`. Tone-only counts (grave, acute, macron) are reported separately because dot-below letters are partly an orthography choice.

### Net loss, drop rate, added rate

- Net loss = (E - P) / E, can be negative
- Drop rate (RDD) = D / E
- Added rate = H / E

Report all of them together; any one alone can mislead.

### 2. Raw Diacritic Drop Rate (RDD)

(Defined above; kept as its own heading for continuity.)

$$
\text{RDD} = \frac{D}{E}
$$

Simple proportion of expected tone marks not produced.

### 3. Bootstrap Confidence Intervals

**Why bootstrap?**
- Small sample size (N=21)
- Makes the sampling uncertainty visible without assuming a distribution

**Method:**
- 10,000 resamples, **resampling clips** (the independent unit). Resampling individual marks would treat the marks within one clip as independent and give intervals that are far too narrow.
- Percentile method for the 95% CI
- Resamples where the statistic is undefined (zero expected marks, common with 5 clips and several zero-mark clips) are dropped and counted (`n_undefined`)
- More resamples do not add information; only more independent clips (and speakers) do

**The headline number is the point estimate on the original data**, not the bootstrap mean. The tonal drop rate is 37/49 = 75.5% and its bootstrap interval is [57.1%, 89.7%].

**Reconciling the numbers that appear in earlier drafts:** 30/49 = 61.2% is the *net* loss (37 dropped minus 7 added). 75.5% is the *drop rate* (37/49). They are different metrics, not a raw count versus a bootstrap mean, and resampling clips does not push a rate "toward extreme loss rates". The bootstrap interval was always an interval for the drop rate.

### 4. Character Error Rate (CER)

$$
\text{CER} = \frac{\text{Levenshtein distance}(\text{ref}, \text{hyp})}{\text{length}(\text{ref})}
$$

Computed on lowercased NFC text (`evaluate.character_error_rate`). The `character_error_rate` column in `metadata.csv` and in the original notebook is actually `1 - difflib.SequenceMatcher.ratio()`, a similarity-based score that is correlated with CER (r = 0.85 on these clips) but is not CER. The corrected mean CER is 0.365 on lowercased text (0.333 for the legacy column). `evaluate.sequence_dissimilarity` keeps the old score under an honest name.

### 5. Position-aware mark estimate

Counting cannot separate a correct mark from a mark on the wrong letter. `evaluate.align_marks` aligns reference and output on base letters (marks stripped, lowercased; global alignment, match +2, mismatch -1, gap -1) and classifies each mark as correct, wrong (different mark on the aligned letter), missing, or inserted. Invariants: correct + wrong + missing = E; correct + wrong + inserted = P. Overall: 33 / 7 / 57 / 31. Limitation: a mis-heard letter can make a mark look missing, so this separates "mark absent" from "mark wrong" only as far as the alignment is right.

---

## Statistical Analysis

### Comparing categories

**Question:** is the tonal category's drop rate higher than the others'?

Overlap of two separate confidence intervals is not a test, and intervals that do not overlap are not needed for a difference to be real either way. The comparison that answers the question is a paired bootstrap of the difference (`evaluate.paired_diff_ci`), resampling clips within each category:

| Tonal minus | Difference in drop rate | 95% CI |
|---|---|---|
| cross-lingual | 64.4 points | [40.5, 85.7] |
| domain | 44.3 points | [-9.4, 80.6] |
| language boundary | 25.5 points | [-18.9, 78.6] |

Only the cross-lingual contrast excludes zero. The tonal interval [57.1%, 89.7%] does overlap the language-boundary and domain intervals, so the earlier statement that it "does not overlap with other categories" was incorrect.

### Descriptive, not inferential

The lower bound of the tonal interval (57.1%) says that, if these 6 clips were a random sample from a larger population of similar clips, drop rates far below 57% would be unlikely. Six clips from one speaker are not such a sample, so the interval is a description of this dataset's noise, not a guarantee about Igbo speech.

### CER versus drop rate

Across the 18 clips with at least one expected mark, drop rate and (true) CER correlate at r = 0.36 (r = 0.26 using the legacy difflib score). With 18 points this is weak evidence either way; it is noted because mark loss and general transcription errors cannot be cleanly separated here.

---

## Limitations

### Sample Size
- **N=21** is small for prevalence estimation
- Sufficient for blind spot discovery (proof-of-concept)
- Future work requires 100+ samples across multiple speakers

### Single Annotator
- All reference transcripts, including the placement of tone marks, were produced by one person (the speaker)
- No inter-annotator agreement was measured; a second annotator would show how stable the expected-mark counts are
- Some references omit dot-below marks that standard orthography would include, which affects "added" counts

### Clip Independence
- Clips from one speaker, one device and one session share conditions, so they are not fully independent draws; clip-level bootstrap intervals are still optimistic

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
- **Dataset:** https://huggingface.co/datasets/Chiz/omniASR-igbo-blindspots

### Environment
- Google Colab (NVIDIA Tesla T4, 15GB VRAM)
- omnilingual-asr==0.1.0
- torch==2.1.0
- Python 3.12
- The corrected analysis (`analysis-2.ipynb`, `src/`) needs only pandas, numpy, matplotlib, seaborn and runs on CPU from `data/metadata.csv`

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
