"""
Evaluation metrics for ASR tonal fidelity analysis.

Metric definitions (per clip i: E_i expected marks, P_i produced marks,
D_i = max(0, E_i - P_i) dropped, H_i = max(0, P_i - E_i) added):

    net_loss           = (sum E - sum P) / sum E        can be negative
    drop_rate  (RDD)   = sum D / sum E                  "how many expected marks vanished"
    added_rate         = sum H / sum E                  "extra marks per expected mark"
    DER                = (sum D + sum H) / sum E        can exceed 1

D and H are computed PER CLIP and then summed. Netting at the pooled level
(max(0, sum E - sum P)) lets additions in one clip cancel drops in another
and is NOT what these functions do.

A "mark" is one NFD grapheme cluster (base letter plus its combining marks)
that carries a grave (U+0300), acute (U+0301), macron (U+0304) or dot-below
(U+0323). A letter with dot-below AND a tone counts once. This rule
reproduces diacritics_expected / diacritics_produced in data/metadata.csv for
all 21 clips.

Count-based metrics cannot tell a correct mark from a wrong mark on the wrong
letter. `align_marks` adds a position-aware estimate.
"""

import unicodedata
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from difflib import SequenceMatcher

GRAVE, ACUTE, MACRON, DOT_BELOW = 0x300, 0x301, 0x304, 0x323
COUNTED = {GRAVE, ACUTE, MACRON, DOT_BELOW}
TONE = {GRAVE, ACUTE, MACRON}
MARK_NAME = {GRAVE: "grave", ACUTE: "acute", MACRON: "macron", DOT_BELOW: "dot"}


# --------------------------------------------------------------------------
# Counting
# --------------------------------------------------------------------------

def _clusters(text: str) -> List[str]:
    """Split NFD text into base+combining-mark clusters."""
    out: List[str] = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch) and out:
            out[-1] += ch
        else:
            out.append(ch)
    return out


def _counted_marks(cluster: str) -> Tuple[int, ...]:
    return tuple(sorted({ord(c) for c in cluster[1:]} & COUNTED))


def count_diacritics(text: str) -> int:
    """Number of letters carrying a counted mark (grave, acute, macron, dot-below)."""
    return sum(1 for c in _clusters(text) if _counted_marks(c))


def count_tone_marks(text: str) -> int:
    """Letters carrying a tone mark (grave, acute, macron), dot-below ignored."""
    return sum(1 for c in _clusters(text) if set(_counted_marks(c)) & TONE)


# --------------------------------------------------------------------------
# Character error rate
# --------------------------------------------------------------------------

def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def character_error_rate(reference: str, hypothesis: str, lowercase: bool = True) -> float:
    """True CER: Levenshtein distance over NFC characters / reference length."""
    r = unicodedata.normalize("NFC", reference)
    h = unicodedata.normalize("NFC", hypothesis)
    if lowercase:
        r, h = r.lower(), h.lower()
    return levenshtein(r, h) / max(1, len(r))


def sequence_dissimilarity(reference: str, hypothesis: str) -> float:
    """1 - difflib ratio. This is what the 'character_error_rate' column in
    data/metadata.csv actually contains (max difference 0.0005). It is a
    similarity-based score, not Levenshtein CER, so it is kept under its own
    name for backward compatibility."""
    return 1 - SequenceMatcher(None, reference.lower(), hypothesis.lower()).ratio()


# --------------------------------------------------------------------------
# Per-clip and pooled metrics
# --------------------------------------------------------------------------

def add_clip_columns(df: pd.DataFrame, use_dataset_counts: bool = False) -> pd.DataFrame:
    """Add per-clip D, H and net columns (and recompute counts unless told not to)."""
    df = df.copy()
    if not use_dataset_counts or "diacritics_expected" not in df.columns:
        df["diacritics_expected"] = df["ground_truth"].apply(count_diacritics)
        df["diacritics_produced"] = df["model_output"].apply(count_diacritics)
    E, P = df["diacritics_expected"], df["diacritics_produced"]
    df["diacritic_loss"] = E - P                       # net, kept for compatibility
    df["dropped"] = (E - P).clip(lower=0)
    df["added"] = (P - E).clip(lower=0)
    df["cer"] = [character_error_rate(r, h) for r, h in zip(df["ground_truth"], df["model_output"])]
    df["seq_dissimilarity"] = [sequence_dissimilarity(r, h) for r, h in zip(df["ground_truth"], df["model_output"])]
    return df


def compute_all_metrics(df: pd.DataFrame, use_dataset_counts: bool = False) -> pd.DataFrame:
    """Backward-compatible entry point. Returns df with counts, per-clip D/H, CER."""
    return add_clip_columns(df, use_dataset_counts)


def calculate_der(df: pd.DataFrame) -> Dict[str, float]:
    """Pooled metrics with D and H taken per clip (never netted across clips)."""
    if "dropped" not in df.columns:
        E, P = df["diacritics_expected"], df["diacritics_produced"]
        dropped, added = (E - P).clip(lower=0), (P - E).clip(lower=0)
    else:
        dropped, added = df["dropped"], df["added"]
    E_tot = float(df["diacritics_expected"].sum())
    P_tot = float(df["diacritics_produced"].sum())
    D, H = float(dropped.sum()), float(added.sum())
    nan = float("nan")
    return {
        "n_clips": int(len(df)),
        "expected": E_tot, "produced": P_tot, "dropped": D, "added": H,
        "net_loss": (E_tot - P_tot) / E_tot if E_tot else nan,
        "drop_rate": D / E_tot if E_tot else nan,
        "added_rate": H / E_tot if E_tot else nan,
        "DER": (D + H) / E_tot if E_tot else nan,
        # share of produced marks in clips where production exceeded expectation
        "hallucination_rate": H / P_tot if P_tot else nan,
    }


# --------------------------------------------------------------------------
# Bootstrap (resample CLIPS, the independent unit)
# --------------------------------------------------------------------------

def bootstrap_ci(
    data: pd.DataFrame, stat_fn, n_boot: int = 10000, ci: float = 0.95, seed: int = 42
) -> Dict[str, float]:
    """Percentile bootstrap over clips.

    Returns a dict: point (statistic on the original data), boot_mean, lo, hi,
    n_undefined (resamples where the statistic was undefined, e.g. zero
    expected marks; they are dropped from the percentiles and reported).

    The point estimate is the right headline number. The bootstrap mean is
    returned only as a diagnostic: a ratio of sums is a biased estimator, so
    the two differ a little, but a bootstrap mean never equals a different
    metric (e.g. a drop rate vs a net loss).
    """
    n = len(data)
    if n == 0:
        return dict(point=np.nan, boot_mean=np.nan, lo=np.nan, hi=np.nan, n_undefined=0)
    rng = np.random.default_rng(seed)
    point = float(stat_fn(data))
    boots = np.empty(n_boot)
    for i in range(n_boot):
        boots[i] = float(stat_fn(data.iloc[rng.integers(0, n, size=n)]))
    ok = boots[~np.isnan(boots)]
    a = (1 - ci) / 2
    return dict(
        point=point,
        boot_mean=float(ok.mean()) if len(ok) else np.nan,
        lo=float(np.quantile(ok, a)) if len(ok) else np.nan,
        hi=float(np.quantile(ok, 1 - a)) if len(ok) else np.nan,
        n_undefined=int(np.isnan(boots).sum()),
    )


def stat_drop_rate(df: pd.DataFrame) -> float:
    E = df["diacritics_expected"].sum()
    return df["dropped"].sum() / E if E > 0 else np.nan


def stat_added_rate(df: pd.DataFrame) -> float:
    E = df["diacritics_expected"].sum()
    return df["added"].sum() / E if E > 0 else np.nan


def stat_net_loss(df: pd.DataFrame) -> float:
    E = df["diacritics_expected"].sum()
    return (E - df["diacritics_produced"].sum()) / E if E > 0 else np.nan


def stat_der(df: pd.DataFrame) -> float:
    E = df["diacritics_expected"].sum()
    return (df["dropped"].sum() + df["added"].sum()) / E if E > 0 else np.nan


def stat_avg_cer(df: pd.DataFrame) -> float:
    return float(df["cer"].mean())


# Backward-compatible names. stat_loss_rate was always the drop rate.
stat_loss_rate = stat_drop_rate


def stat_halluc_rate(df: pd.DataFrame) -> float:
    P = df["diacritics_produced"].sum()
    return df["added"].sum() / P if P > 0 else np.nan


def paired_diff_ci(
    data: pd.DataFrame, group_col: str, a: str, b: str, stat_fn=stat_drop_rate,
    n_boot: int = 10000, ci: float = 0.95, seed: int = 42,
) -> Dict[str, float]:
    """Bootstrap CI for stat(group a) - stat(group b), resampling clips within each
    group independently. Use this (not 'do the two CIs overlap') to compare groups."""
    A, B = data[data[group_col] == a], data[data[group_col] == b]
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        sa = stat_fn(A.iloc[rng.integers(0, len(A), size=len(A))])
        sb = stat_fn(B.iloc[rng.integers(0, len(B), size=len(B))])
        diffs[i] = sa - sb
    ok = diffs[~np.isnan(diffs)]
    al = (1 - ci) / 2
    return dict(
        diff=float(stat_fn(A) - stat_fn(B)),
        lo=float(np.quantile(ok, al)), hi=float(np.quantile(ok, 1 - al)),
        n_undefined=int(np.isnan(diffs).sum()),
    )


# --------------------------------------------------------------------------
# Position-aware estimate: align on base letters, then classify each mark
# --------------------------------------------------------------------------

def _units(text: str) -> List[dict]:
    """Letters (lowercased base) with their counted marks. Non-letters are skipped."""
    out: List[dict] = []
    cur: Optional[dict] = None
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch):
            if cur is not None:
                cur["marks"].add(ord(ch))
            continue
        if not ch.isalpha():
            cur = None
            continue
        cur = {"base": ch.lower(), "marks": set()}
        out.append(cur)
    for u in out:
        u["m"] = tuple(sorted(u["marks"] & COUNTED))
    return out


def _align(R: List[dict], O: List[dict]):
    """Global alignment on base letters: match +2, mismatch -1, gap -1.
    Ties prefer diagonal, then reference-gap, then hypothesis-gap."""
    n, m = len(R), len(O)
    S = [[0] * (m + 1) for _ in range(n + 1)]
    T = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        S[i][0], T[i][0] = -i, 1
    for j in range(1, m + 1):
        S[0][j], T[0][j] = -j, 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = S[i - 1][j - 1] + (2 if R[i - 1]["base"] == O[j - 1]["base"] else -1)
            u, l = S[i - 1][j] - 1, S[i][j - 1] - 1
            b = max(d, u, l)
            S[i][j] = b
            T[i][j] = 0 if b == d else 1 if b == u else 2
    pairs, i, j = [], n, m
    while i > 0 or j > 0:
        t = T[i][j] if (i > 0 and j > 0) else (1 if i > 0 else 2)
        if t == 0:
            pairs.append((R[i - 1], O[j - 1])); i -= 1; j -= 1
        elif t == 1:
            pairs.append((R[i - 1], None)); i -= 1
        else:
            pairs.append((None, O[j - 1])); j -= 1
    return pairs[::-1]


def align_marks(reference: str, hypothesis: str) -> Dict[str, int]:
    """Classify marks by position. Invariants:
        correct + wrong + missing  == expected marks
        correct + wrong + inserted == produced marks
    correct: aligned letter carries the same mark set in both texts
    wrong:   aligned letter carries a mark in both, but a different one
    missing: expected mark, none on the aligned letter (or letter unaligned)
    inserted: produced mark on a letter that carries none in the reference
    This is an estimate: it depends on the alignment, and a model that
    mis-hears the letters can look 'missing' because of the letter error.
    """
    res = dict(correct=0, wrong=0, missing=0, inserted=0)
    for a, b in _align(_units(reference), _units(hypothesis)):
        am = a["m"] if a else ()
        bm = b["m"] if b else ()
        if am:
            if not bm:
                res["missing"] += 1
            elif am == bm:
                res["correct"] += 1
            else:
                res["wrong"] += 1
        elif bm:
            res["inserted"] += 1
    return res


def aligned_table(df: pd.DataFrame, group_col: Optional[str] = "category") -> pd.DataFrame:
    """Aligned counts per group plus an 'overall' row."""
    rows = [align_marks(r, h) for r, h in zip(df["ground_truth"], df["model_output"])]
    a = pd.DataFrame(rows, index=df.index)
    if group_col is None:
        return a.sum().to_frame("overall").T
    t = a.groupby(df[group_col]).sum()
    t.loc["overall"] = a.sum()
    return t


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for cat, g in df.groupby("category"):
        rows[cat] = calculate_der(g)
    rows["overall"] = calculate_der(df)
    t = pd.DataFrame(rows).T
    t["mean_cer"] = [df[df.category == c]["cer"].mean() for c in t.index[:-1]] + [df["cer"].mean()]
    return t


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <metadata.csv>")
        sys.exit(1)

    df = add_clip_columns(pd.read_csv(sys.argv[1]))
    pd.set_option("display.width", 200)

    print("\nPooled metrics (D and H computed per clip):")
    cols = ["n_clips", "expected", "produced", "dropped", "added",
            "net_loss", "drop_rate", "added_rate", "DER", "mean_cer"]
    print(summarize(df)[cols].round(3).to_string())

    print("\nBootstrap 95% CIs on drop rate (clip-level resampling, 10,000 draws):")
    for cat, g in list(df.groupby("category")) + [("overall", df)]:
        r = bootstrap_ci(g, stat_drop_rate)
        note = f"  ({r['n_undefined']} undefined resamples dropped)" if r["n_undefined"] else ""
        print(f"  {cat:22s} {r['point']:.3f}  [{r['lo']:.3f}, {r['hi']:.3f}]{note}")

    print("\nAligned mark classification:")
    print(aligned_table(df).to_string())

    out = sys.argv[1].replace(".csv", "_analyzed.csv")
    df.to_csv(out, index=False)
    print(f"\nSaved to: {out}")
