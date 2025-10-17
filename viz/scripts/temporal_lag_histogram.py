#!/usr/bin/env python3
"""
Temporal Lag Distribution Histogram
Shows temporal matching quality and lag distribution across sites
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

def load_data():
    """Load matched sites with temporal lag information"""
    print("Loading data...")

    with open("data/major_tom/predicts_s2_matches_fixed.json") as f:
        matches = json.load(f)

    matches_df = pd.DataFrame(matches)
    matches_df = matches_df[matches_df["product_id"].notna()]
    matches_df["Sample_midpoint"] = pd.to_datetime(matches_df["Sample_midpoint"])
    matches_df["eo_timestamp"] = pd.to_datetime(matches_df["eo_timestamp"])

    matches_df["lag_years"] = matches_df["lag_days"] / 365.25

    return matches_df

def create_figure(matches_df):
    """Create temporal lag distribution histogram"""
    print("Creating temporal lag histogram...")

    fig, ax = plt.subplots(figsize=(10, 6))

    lag_years = matches_df["lag_years"].values
    n_total = len(lag_years)

    n_5yr = (lag_years < 5).sum()
    n_10yr = (lag_years < 10).sum()
    n_15yr = (lag_years < 15).sum()
    n_20yr = (lag_years < 20).sum()

    # Create histogram with bins every 1 year from 0-30
    counts, bins, patches = ax.hist(lag_years, bins=60, range=(0, 30),
                                    color='#E63946', alpha=0.7, edgecolor='black',
                                    linewidth=0.5)

    # Add threshold lines
    thresholds = [5, 10, 15, 20]
    threshold_colors = ['#06BA63', '#F77F00', '#457B9D', '#D62828']
    threshold_labels = ['5 yr', '10 yr', '15 yr', '20 yr']

    for thresh, color, label in zip(thresholds, threshold_colors, threshold_labels):
        ax.axvline(thresh, color=color, linestyle='--', linewidth=2, alpha=0.8)
        y_pos = ax.get_ylim()[1] * 0.92
        ax.text(thresh, y_pos, label, color=color,
                fontsize=9, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

    ax.set_xlabel('Temporal Lag (years)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Sites', fontsize=11, fontweight='bold')
    ax.set_title('Temporal Lag Distribution of PREDICTS-Major TOM Matches',
                 fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_xlim(0, 30)

    # Add statistics box
    stats_text = f'Total Sites: {n_total:,}\n'
    stats_text += f'Mean: {lag_years.mean():.1f} yr\n'
    stats_text += f'Median: {np.median(lag_years):.1f} yr\n'
    stats_text += f'Std Dev: {lag_years.std():.1f} yr\n\n'
    stats_text += f'<  5 yr: {n_5yr:,} ({n_5yr/n_total*100:.1f}%)\n'
    stats_text += f'< 10 yr: {n_10yr:,} ({n_10yr/n_total*100:.1f}%)\n'
    stats_text += f'< 15 yr: {n_15yr:,} ({n_15yr/n_total*100:.1f}%)\n'
    stats_text += f'< 20 yr: {n_20yr:,} ({n_20yr/n_total*100:.1f}%)'

    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='wheat', alpha=0.85,
                     edgecolor='black', linewidth=1.5),
            family='monospace')

    plt.tight_layout()

    return fig

def main():
    matches_df = load_data()

    fig = create_figure(matches_df)

    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)

    print("Saving PDF...")
    fig.savefig(output_dir / "temporal_lag_histogram.pdf",
                dpi=300, bbox_inches='tight', format='pdf')

    print("Saving PNG...")
    fig.savefig(output_dir / "temporal_lag_histogram.png",
                dpi=300, bbox_inches='tight', format='png')

    print("Temporal lag histogram complete!")
    print(f"  PDF: {output_dir / 'temporal_lag_histogram.pdf'}")
    print(f"  PNG: {output_dir / 'temporal_lag_histogram.png'}")

if __name__ == "__main__":
    main()
