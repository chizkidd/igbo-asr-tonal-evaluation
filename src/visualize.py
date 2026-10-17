"""
Visualization functions for ASR tonal fidelity analysis.

Generates figures for:
- Marks dropped vs. marks added by category (D and H counted per clip, never netted)
- CER vs. drop rate scatter (per clip)
- Drop rate with clip-level bootstrap confidence intervals
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional


# Set publication-quality defaults
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

# Category colors are used only where categories are the thing being compared
# (scatter, forest plot labels). The bar chart uses neutral dropped/added colors
# so the two figures never give one color two meanings.
CATEGORY_COLORS = {
    'tonal_diacritics': '#d62728',
    'code_switching': '#ff7f0e',
    'cultural_context': '#1f77b4',
    'script_hallucination': '#2ca02c',
}
DROPPED_COLOR = '#264653'   # dark slate
ADDED_COLOR = '#b8b8b8'     # light grey


def _pretty(name: str) -> str:
    return name.replace('_', ' ').title()


def _finish(fig, output_path):
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close(fig)
    else:
        plt.show()


def plot_loss_by_category(
    df: pd.DataFrame,
    output_path: Optional[str] = None,
    figsize: tuple = (10, 6)
):
    """
    Paired horizontal bars per category: drop rate and added rate, both as a
    percentage of expected marks. D and H are computed per clip, then summed,
    so additions in one clip never cancel drops in another.

    Args:
        df: DataFrame with columns 'category', 'diacritics_expected', 'diacritics_produced'
        output_path: Where to save figure (optional)
        figsize: Figure size in inches
    """
    d = df.copy()
    d['dropped'] = (d['diacritics_expected'] - d['diacritics_produced']).clip(lower=0)
    d['added'] = (d['diacritics_produced'] - d['diacritics_expected']).clip(lower=0)
    s = d.groupby('category').agg(
        dropped=('dropped', 'sum'), added=('added', 'sum'),
        expected=('diacritics_expected', 'sum'))
    s['drop_rate'] = s['dropped'] / s['expected'] * 100
    s['added_rate'] = s['added'] / s['expected'] * 100
    s = s.sort_values('drop_rate')            # largest drop rate ends up on top

    fig, ax = plt.subplots(figsize=figsize)
    y = np.arange(len(s))
    h = 0.38
    ax.barh(y + h / 2, s['drop_rate'], height=h, color=DROPPED_COLOR,
            label='Dropped (% of expected marks)')
    ax.barh(y - h / 2, s['added_rate'], height=h, color=ADDED_COLOR,
            label='Added (% of expected marks)')

    for i, (_, row) in enumerate(s.iterrows()):
        ax.text(row['drop_rate'] + 1.5, i + h / 2,
                f"{row['drop_rate']:.1f}%  ({int(row['dropped'])}/{int(row['expected'])})",
                va='center', ha='left', fontsize=9, fontweight='bold')
        ax.text(row['added_rate'] + 1.5, i - h / 2,
                f"{row['added_rate']:.1f}%  (+{int(row['added'])})",
                va='center', ha='left', fontsize=9, color='#444444')

    ax.set_yticks(y)
    ax.set_yticklabels([_pretty(c) for c in s.index])
    ax.set_xlim(0, max(100, float(s[['drop_rate', 'added_rate']].values.max()) + 30))
    ax.set_xlabel('% of expected marks', fontweight='bold')
    ax.set_title('Marks dropped vs. marks added, by category', fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3)
    ax.grid(axis='y', visible=False)
    ax.legend(loc='lower right', framealpha=0.9)
    _finish(fig, output_path)


def plot_cer_vs_loss(
    df: pd.DataFrame,
    output_path: Optional[str] = None,
    figsize: tuple = (10, 6)
):
    """
    Scatter plot of CER vs. per-clip drop rate.

    Clips with no expected marks have no defined drop rate and are left out
    (the figure says how many). Because clips carry only a handful of marks,
    many drop rates are exactly 0% or 100%. Points are semi-transparent with an
    outline so overlapping clips stay visible.

    Args:
        df: DataFrame with 'cer' (or 'character_error_rate'), expected/produced
            counts and 'category'
        output_path: Where to save figure (optional)
        figsize: Figure size in inches
    """
    cer_col = 'cer' if 'cer' in df.columns else 'character_error_rate'
    n_total = len(df)
    d = df[df['diacritics_expected'] > 0].copy()
    n_excluded = n_total - len(d)
    d['dropped'] = (d['diacritics_expected'] - d['diacritics_produced']).clip(lower=0)
    d['drop_rate'] = d['dropped'] / d['diacritics_expected'] * 100
    d['cer_pct'] = d[cer_col] * 100

    fig, ax = plt.subplots(figsize=figsize)
    categories = list(d['category'].unique())
    fallback = sns.color_palette("husl", len(categories))
    for i, cat in enumerate(categories):
        sub = d[d['category'] == cat]
        color = CATEGORY_COLORS.get(cat, fallback[i])
        ax.scatter(sub['cer_pct'], sub['drop_rate'], label=_pretty(cat), s=110,
                   color=color, alpha=0.6, edgecolor='black', linewidth=0.8, zorder=3)

    r = float(np.corrcoef(d['cer_pct'], d['drop_rate'])[0, 1]) if len(d) > 2 else float('nan')
    ax.text(0.98, 0.16, f"Pearson r = {r:.2f} (n = {len(d)} clips)", transform=ax.transAxes,
            ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='#cccccc', alpha=0.9))

    ax.set_xlabel('Character error rate (%)', fontweight='bold')
    ax.set_ylabel('Diacritic drop rate (%)', fontweight='bold')
    ax.set_title('CER vs. drop rate, by clip', fontweight='bold', pad=15)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(alpha=0.3)
    fig.text(0.01, -0.02,
             f"{n_excluded} of {n_total} clips have no expected marks and are not shown. "
             "Rates sit at 0% or 100% because each clip carries only a few marks.",
             fontsize=8, color='#555555', ha='left', va='top')
    _finish(fig, output_path)


def plot_bootstrap_ci(
    bootstrap_results: Dict[str, object],
    output_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    n_clips: Optional[Dict[str, int]] = None,
    show_threshold: bool = False
):
    """
    Forest plot of drop rate with 95% bootstrap confidence intervals.

    Categories are sorted by drop rate (highest on top); 'overall' is shown
    last, separated by a gap. The axis starts at 0 because a rate cannot be
    negative, which is also why several intervals stop exactly at 0.

    Args:
        bootstrap_results: Dict mapping group -> (point, lo, hi), or the dict
            returned by evaluate.bootstrap_ci (keys point, lo, hi). A group
            named 'overall' is placed last.
        output_path: Where to save figure (optional)
        figsize: Figure size in inches
        n_clips: Optional dict group -> number of clips, shown in the labels
        show_threshold: Draw a 50% reference line (a convention, not a test)
    """
    def _t(v):
        return (v['point'], v['lo'], v['hi']) if isinstance(v, dict) else tuple(v)

    vals = {k: _t(v) for k, v in bootstrap_results.items()}
    cats = sorted([k for k in vals if k != 'overall'], key=lambda k: -vals[k][0])
    rows = cats + (['overall'] if 'overall' in vals else [])
    ypos = list(range(len(cats))) + ([len(cats) + 0.7] if 'overall' in vals else [])

    fig, ax = plt.subplots(figsize=figsize)
    for name, y in zip(rows, ypos):
        p, lo, hi = (x * 100 for x in vals[name])
        color = CATEGORY_COLORS.get(name, '#444444')
        ax.errorbar(p, y, xerr=[[p - lo], [hi - p]], fmt='o', markersize=9, capsize=5,
                    capthick=2, color=color, ecolor=color, alpha=0.85, zorder=3, clip_on=False)
        ax.text(102, y, f"{p:.1f}%  [{lo:.0f}, {hi:.0f}]",
                fontsize=9, color='#333333', va='center', ha='left', clip_on=False)

    labels = []
    for name in rows:
        lab = _pretty(name)
        if n_clips and name in n_clips:
            lab += f"\n(n = {n_clips[name]} clips)"
        labels.append(lab)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 20))
    ax.set_clip_on(False)

    if show_threshold:
        ax.axvline(50, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='50% reference')
        ax.legend(loc='lower right')

    ax.set_xlabel('Diacritic drop rate (%)', fontweight='bold')
    ax.set_title('Drop rate, 95% bootstrap CI (clip-level resampling)', fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3)
    ax.grid(axis='y', visible=False)
    fig.text(0.01, -0.02,
             "Intervals stop at 0% because a rate cannot be negative. With 5 to 6 clips per category "
             "the non-tonal intervals are very wide.",
             fontsize=8, color='#555555', ha='left', va='top')
    _finish(fig, output_path)


def generate_all_figures(
    df: pd.DataFrame,
    bootstrap_results: dict,
    output_dir: str = "visualizations",
    n_clips: Optional[Dict[str, int]] = None
):
    """
    Generate all figures and save to output directory.

    Args:
        df: DataFrame with analysis results
        bootstrap_results: Bootstrap CI results (group -> (point, lo, hi) or dict)
        output_dir: Directory to save figures
        n_clips: Optional group -> clip count for the forest plot labels
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    print("Generating figures...")
    plot_loss_by_category(df, output_path=output_path / "fig1_drop_rate_by_category.png")
    plot_cer_vs_loss(df, output_path=output_path / "fig2_cer_vs_drop_rate.png")
    plot_bootstrap_ci(bootstrap_results, output_path=output_path / "fig3_bootstrap_95_ci.png",
                      n_clips=n_clips)
    print(f"\nAll figures saved to: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visualize.py <metadata.csv> [output_dir]")
        sys.exit(1)

    from evaluate import add_clip_columns, bootstrap_ci, stat_drop_rate

    # Everything is computed from the data (no hard-coded results)
    df = add_clip_columns(pd.read_csv(sys.argv[1]))
    bootstrap_results = {'overall': bootstrap_ci(df, stat_drop_rate)}
    counts = {'overall': len(df)}
    for cat, g in df.groupby('category'):
        bootstrap_results[cat] = bootstrap_ci(g, stat_drop_rate)
        counts[cat] = len(g)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "visualizations"
    generate_all_figures(df, bootstrap_results, output_dir, n_clips=counts)