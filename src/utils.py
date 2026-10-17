"""
Utility functions for ASR evaluation.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict


def load_metadata(filepath: str) -> pd.DataFrame:
    """
    Load and validate metadata CSV.
    
    Args:
        filepath: Path to metadata.csv
        
    Returns:
        Validated DataFrame
    """
    df = pd.read_csv(filepath)
    
    # Validate required columns
    required = [
        'file_name', 'ground_truth', 'model_output',
        'category', 'language'
    ]
    
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df


def print_summary(df: pd.DataFrame):
    """
    Print dataset summary statistics.
    
    Args:
        df: DataFrame with analysis results
    """
    print("="*70)
    print("DATASET SUMMARY")
    print("="*70)
    print(f"Total samples: {len(df)}")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Languages: {', '.join(df['language'].unique())}")
    
    print("\nSamples by category:")
    for cat, count in df['category'].value_counts().items():
        print(f"  {cat}: {count}")
    
    if 'diacritics_expected' in df.columns:
        E = df['diacritics_expected'].sum()
        P = df['diacritics_produced'].sum()
        D = (df['diacritics_expected'] - df['diacritics_produced']).clip(lower=0).sum()
        H = (df['diacritics_produced'] - df['diacritics_expected']).clip(lower=0).sum()
        print(f"\nExpected marks: {E}   Produced marks: {P}")
        print(f"Dropped (per clip): {D}   Added (per clip): {H}")
        print(f"Net loss {(E-P)/E:.1%} | drop rate {D/E:.1%} | added rate {H/E:.1%} | DER {(D+H)/E:.1%}")
    
    if 'character_error_rate' in df.columns:
        print(f"\nAverage CER: {df['character_error_rate'].mean():.3f}")
        print(f"  Min: {df['character_error_rate'].min():.3f}")
        print(f"  Max: {df['character_error_rate'].max():.3f}")


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate category-level statistics.
    
    Args:
        df: DataFrame with analysis results
        
    Returns:
        DataFrame with category statistics
    """
    df = df.copy()
    E, P = df['diacritics_expected'], df['diacritics_produced']
    df['dropped'] = (E - P).clip(lower=0)
    df['added'] = (P - E).clip(lower=0)
    cer_col = 'cer' if 'cer' in df.columns else 'character_error_rate'

    stats = df.groupby('category').agg(
        samples=('file_name', 'count'),
        expected=('diacritics_expected', 'sum'),
        produced=('diacritics_produced', 'sum'),
        dropped=('dropped', 'sum'),
        added=('added', 'sum'),
        avg_cer=(cer_col, 'mean'),
    )
    stats['net_loss'] = (stats['expected'] - stats['produced']) / stats['expected']
    stats['drop_rate'] = stats['dropped'] / stats['expected']
    stats['added_rate'] = stats['added'] / stats['expected']
    stats['DER'] = (stats['dropped'] + stats['added']) / stats['expected']
    return stats


def export_results(
    df: pd.DataFrame,
    category_stats: pd.DataFrame,
    output_dir: str = "results"
):
    """
    Export analysis results to CSV files.
    
    Args:
        df: Full analysis DataFrame
        category_stats: Category-level statistics
        output_dir: Directory to save results
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Save full results
    df.to_csv(output_path / "full_analysis.csv", index=False)
    
    # Save category summary
    category_stats.to_csv(output_path / "category_summary.csv")
    
    print(f"\nResults exported to: {output_path}")
    print(f"  - full_analysis.csv")
    print(f"  - category_summary.csv")


def validate_audio_files(
    metadata_path: str,
    audio_dir: str = "data",
    extensions: tuple = (".wav", ".m4a")
) -> List[str]:
    """
    Check if all audio files referenced in metadata exist.

    metadata.csv lists paths like "audio/01_script_names.wav" (relative to
    data/), while the raw recordings in this repo may be .m4a. A file counts as
    present if it exists under any of `extensions`.

    Args:
        metadata_path: Path to metadata CSV
        audio_dir: Directory that file_name is relative to (default "data")
        extensions: Extensions to try, in order

    Returns:
        List of missing files (empty if all present)
    """
    df = pd.read_csv(metadata_path)
    audio_path = Path(audio_dir)
    
    missing = []
    for filename in df['file_name']:
        stem = (audio_path / filename).with_suffix('')
        if not any(stem.with_suffix(ext).exists() for ext in extensions):
            missing.append(filename)
    
    if missing:
        print(f"WARNING: Missing {len(missing)} audio files:")
        for f in missing:
            print(f"  - {f}")
    else:
        print(f"OK: All {len(df)} audio files present")
    
    return missing


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python utils.py <metadata.csv>")
        sys.exit(1)
    
    # Load and summarize
    df = load_metadata(sys.argv[1])
    print_summary(df)
    
    # Category breakdown
    print("\n" + "="*70)
    print("CATEGORY BREAKDOWN")
    print("="*70)
    stats = category_breakdown(df)
    print(stats.to_string())
