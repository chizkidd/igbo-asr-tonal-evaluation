"""
Visualization functions for ASR tonal fidelity analysis.

Generates publication-quality figures for:
- Diacritic drop rate by category (drops counted per clip, never netted)
- CER vs drop rate scatter (per clip)
- Bootstrap confidence intervals (clip-level resampling)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


# Set publication-quality defaults
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12


CATEGORY_COLORS = {
    'tonal_diacritics': '#d62728',
    'code_switching': '#ff7f0e',
    'cultural_context': '#1f77b4',
    'script_hallucination': '#2ca02c',
}
DROPPED_COLOR = '#d62728'
ADDED_COLOR = '#7f7f7f'


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
    ax.barh(y + h / 2, s['drop_rate'], height=h, color=DROPPED_COLOR, label='Dropped (% of expected marks)')
    ax.barh(y - h / 2, s['added_rate'], height=h, color=ADDED_COLOR, label='Added (% of expected marks)')

    for i, (_, row) in enumerate(s.iterrows()):
        ax.text(row['drop_rate'] + 1.5, i + h / 2, f"{row['drop_rate']:.1f}%  ({int(row['dropped'])}/{int(row['expected'])})",
                va='center', ha='left', fontsize=9, fontweight='bold')
        ax.text(row['added_rate'] + 1.5, i - h / 2, f"{row['added_rate']:.1f}%  (+{int(row['added'])})",
                va='center', ha='left', fontsize=9, color='#444444')

    ax.set_yticks(y)
    ax.set_yticklabels([c.replace('_', ' ').title() for c in s.index])
    ax.set_xlim(0, max(100, float(s[['drop_rate', 'added_rate']].values.max()) + 30))
    ax.set_xlabel('% of expected marks', fontweight='bold')
    ax.set_title('Marks dropped vs. marks added, by category', fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3)
    ax.grid(axis='y', visible=False)
    ax.legend(loc='lower right', framealpha=0.9)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    plt.close(fig) if output_path else plt.show()


def plot_cer_vs_loss(
    df: pd.DataFrame,
    output_path: Optional[str] = None,
    figsize: tuple = (10, 6)
):
    """
    Scatter plot of CER vs diacritic loss.
    
    Args:
        df: DataFrame with 'cer' (or 'character_error_rate'), expected/produced counts, 'category'
        output_path: Where to save figure (optional)
        figsize: Figure size in inches
    """
    # Per-clip drop rate; clips with no expected marks have no defined rate
    df = df[df['diacritics_expected'] > 0].copy()
    df['dropped'] = (df['diacritics_expected'] - df['diacritics_produced']).clip(lower=0)
    df['loss_rate'] = df['dropped'] / df['diacritics_expected'] * 100
    cer_col = 'cer' if 'cer' in df.columns else 'character_error_rate'
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color by category
    categories = df['category'].unique()
    fallback = sns.color_palette("husl", len(categories))
    colors = [CATEGORY_COLORS.get(c, fallback[i]) for i, c in enumerate(categories)]
    
    for i, cat in enumerate(categories):
        cat_data = df[df['category'] == cat]
        ax.scatter(
            cat_data[cer_col] * 100,
            cat_data['loss_rate'],
            label=cat.replace('_', ' ').title(),
            alpha=0.7,
            s=100,
            color=colors[i]
        )
    
    # Formatting
    ax.set_xlabel('Character error rate (%)', fontweight='bold')
    ax.set_ylabel('Diacritic drop rate (%)', fontweight='bold')
    ax.set_title('CER vs. Drop Rate (clips with expected marks)', fontweight='bold', pad=15)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close(fig) if output_path else plt.show()


def plot_bootstrap_ci(
    bootstrap_results: dict,
    output_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    show_threshold: bool = False
):
    """
    Forest plot of bootstrap confidence intervals.
    
    Args:
        bootstrap_results: Dict mapping category -> (point, lo, hi), or the dict
            returned by evaluate.bootstrap_ci (keys point, lo, hi)
        output_path: Where to save figure (optional)
        figsize: Figure size in inches
    """
    # Prepare data
    def _t(v):
        return (v['point'], v['lo'], v['hi']) if isinstance(v, dict) else tuple(v)
    vals = {k: _t(v) for k, v in bootstrap_results.items()}
    categories = list(vals.keys())
    points = [v[0] * 100 for v in vals.values()]
    lows = [v[1] * 100 for v in vals.values()]
    highs = [v[2] * 100 for v in vals.values()]
    errors = [[p - l for p, l in zip(points, lows)],
              [h - p for h, p in zip(highs, points)]]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot error bars
    y_pos = np.arange(len(categories))
    ax.errorbar(
        points, y_pos, xerr=errors,
        fmt='o', markersize=8, capsize=5, capthick=2,
        color='#1f77b4', ecolor='#1f77b4', alpha=0.8
    )
    
    # Optional 50% reference line (a convention, not a statistical threshold)
    if show_threshold:
        ax.axvline(50, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='50% reference')
    
    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c.replace('_', ' ').title() for c in categories])
    ax.set_xlabel('Diacritic drop rate (%)', fontweight='bold')
    ax.set_title('Drop rate, 95% bootstrap CI (clip-level resampling)', fontweight='bold', pad=15)
    if show_threshold:
        ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close(fig) if output_path else plt.show()


def generate_all_figures(
    df: pd.DataFrame,
    bootstrap_results: dict,
    output_dir: str = "visualizations"
):
    """
    Generate all figures and save to output directory.
    
    Args:
        df: DataFrame with analysis results
        bootstrap_results: Bootstrap CI results
        output_dir: Directory to save figures
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    print("Generating figures...")
    
    # Figure 1: Loss by category
    plot_loss_by_category(
        df,
        output_path=output_path / "fig1_drop_rate_by_category.png"
    )
    
    # Figure 2: CER vs loss
    plot_cer_vs_loss(
        df,
        output_path=output_path / "fig2_cer_vs_drop_rate.png"
    )
    
    # Figure 3: Bootstrap CIs
    plot_bootstrap_ci(
        bootstrap_results,
        output_path=output_path / "fig3_bootstrap_95_ci.png"
    )
    
    print(f"\nAll figures saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <metadata_analyzed.csv>")
        sys.exit(1)
    
    from evaluate import add_clip_columns, bootstrap_ci, stat_drop_rate

    # Load data and compute everything from the data (no hard-coded results)
    df = add_clip_columns(pd.read_csv(sys.argv[1]))
    bootstrap_results = {'overall': bootstrap_ci(df, stat_drop_rate)}
    for cat, g in df.groupby('category'):
        bootstrap_results[cat] = bootstrap_ci(g, stat_drop_rate)

    # Generate all figures
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "visualizations"
    generate_all_figures(df, bootstrap_results, output_dir)