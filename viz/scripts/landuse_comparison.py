#!/usr/bin/env python3
"""
Land Use Comparison
Compares distance and temporal lag characteristics across agricultural land use types
Top: Box/violin plots showing distributions
Bottom: Scatter plot showing relationship between distance and temporal lag
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path

# Set publication-quality style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

def load_data():
    """Load matched sites with distances and temporal information"""
    print("Loading data...")

    with open("data/major_tom/predicts_s2_matches_fixed.json") as f:
        matches = json.load(f)

    matches_df = pd.DataFrame(matches)
    matches_df = matches_df[matches_df["product_id"].notna()]
    matches_df["Sample_midpoint"] = pd.to_datetime(matches_df["Sample_midpoint"])
    matches_df["eo_timestamp"] = pd.to_datetime(matches_df["eo_timestamp"])

    # Calculate temporal lag in years
    matches_df["temporal_lag_years"] = abs(
        (matches_df["eo_timestamp"] - matches_df["Sample_midpoint"]).dt.days / 365.25
    )

    return matches_df

def create_figure(matches_df):
    """Create land use comparison with box/violin plots (top) and scatter (bottom)"""
    print("Creating land use comparison figure...")

    # Create figure with 3 rows: top row split (violin plots), bottom row full (scatter)
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(3, 2, figure=fig, height_ratios=[1, 1, 1.2],
                          width_ratios=[1, 1], hspace=0.35, wspace=0.35)

    land_uses = ['Cropland', 'Pasture', 'Plantation\nforest']
    land_uses_filter = ['Cropland', 'Pasture', 'Plantation forest']
    colors = ['#1D3557', '#F77F00', '#9D4EDD']  # Blue, Orange, Purple

    # Top Left: Distance distributions by land use
    ax1 = fig.add_subplot(gs[0, 0])

    data_distance = [matches_df[matches_df['Predominant_land_use']==lu]['distance_km'].values
                     for lu in land_uses_filter]

    parts1 = ax1.violinplot(data_distance, positions=[0, 1, 2],
                            showmedians=True, widths=0.7)

    # Color the violin bodies
    for i, pc in enumerate(parts1['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
        pc.set_linewidth(1)

    # Style the median lines
    parts1['cmedians'].set_edgecolor('black')
    parts1['cmedians'].set_linewidth(2)

    # Add box plots on top for quartiles
    bp1 = ax1.boxplot(data_distance, positions=[0, 1, 2], widths=0.15,
                      patch_artist=True, showfliers=False,
                      boxprops=dict(facecolor='white', alpha=0.7, linewidth=1.5),
                      medianprops=dict(color='black', linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5))

    ax1.set_xticks([0, 1, 2])
    ax1.set_xticklabels(land_uses, fontsize=10, rotation=0)
    ax1.set_ylabel('Distance (km)', fontsize=11, fontweight='bold')
    ax1.set_title('(A) Distance Distribution by Land Use Type',
                  fontsize=11, fontweight='bold', loc='left', pad=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 12)

    # Top Right: Temporal lag distributions by land use
    ax2 = fig.add_subplot(gs[0, 1])

    data_lag = [matches_df[matches_df['Predominant_land_use']==lu]['temporal_lag_years'].values
                for lu in land_uses_filter]

    parts2 = ax2.violinplot(data_lag, positions=[0, 1, 2],
                            showmedians=True, widths=0.7)

    # Color the violin bodies
    for i, pc in enumerate(parts2['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
        pc.set_linewidth(1)

    # Style the median lines
    parts2['cmedians'].set_edgecolor('black')
    parts2['cmedians'].set_linewidth(2)

    # Add box plots on top for quartiles
    bp2 = ax2.boxplot(data_lag, positions=[0, 1, 2], widths=0.15,
                      patch_artist=True, showfliers=False,
                      boxprops=dict(facecolor='white', alpha=0.7, linewidth=1.5),
                      medianprops=dict(color='black', linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5))

    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(land_uses, fontsize=10, rotation=0)
    ax2.set_ylabel('Temporal Lag (years)', fontsize=11, fontweight='bold')
    ax2.set_title('(B) Temporal Lag Distribution by Land Use Type',
                  fontsize=11, fontweight='bold', loc='left', pad=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Add median lag reference line
    median_lag = matches_df["temporal_lag_years"].median()
    ax2.axhline(median_lag, color='red', linestyle=':', linewidth=1.5, alpha=0.6, zorder=0)
    ax2.text(2.3, median_lag, f'Overall median: {median_lag:.1f} yr',
            fontsize=8, va='center', style='italic', color='red',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

    # Bottom: Scatter plot spanning both columns
    ax3 = fig.add_subplot(gs[1:, :])

    # Scatter plot colors - highly distinct
    scatter_colors = {
        'Cropland': '#E63946',           # Red
        'Pasture': '#1D3557',            # Dark Blue
        'Plantation forest': '#2A9D8F'   # Teal
    }

    # Plot in reverse order so Cropland (most common) is on top
    land_use_order = ['Plantation forest', 'Pasture', 'Cropland']

    for land_use in land_use_order:
        color = scatter_colors[land_use]
        mask = matches_df["Predominant_land_use"] == land_use
        count = mask.sum()
        ax3.scatter(matches_df.loc[mask, "distance_km"],
                   matches_df.loc[mask, "temporal_lag_years"],
                   c=color, alpha=0.6, s=25, label=f'{land_use} (n={count:,})',
                   edgecolor='white', linewidth=0.5)

    ax3.set_xlabel('Distance to Major TOM Patch (km)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Temporal Lag (years)', fontsize=11, fontweight='bold')
    ax3.set_title('(C) Distance vs Temporal Lag by Land Use Type',
                  fontsize=11, fontweight='bold', loc='left', pad=10)

    # Enhanced legend
    ax3.legend(loc='upper right', fontsize=10, markerscale=2.0,
              framealpha=0.95, edgecolor='black', fancybox=False,
              borderpad=0.9, labelspacing=0.9, title='Land Use Type',
              title_fontsize=10)

    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xlim(0, 10)

    # Add median lag reference line
    ax3.axhline(median_lag, color='#D62828', linestyle=':', linewidth=2, alpha=0.7, zorder=0)
    ax3.text(9.5, median_lag + 0.4, f'Median lag: {median_lag:.1f} yrs',
            fontsize=9, ha='right', style='italic', color='#D62828',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9,
                     edgecolor='#D62828', linewidth=1))

    # Add statistics text box
    stats_text = f'Total Sites: {len(matches_df):,}\n'
    stats_text += f'Distance: mean={matches_df["distance_km"].mean():.1f} km, '
    stats_text += f'median={matches_df["distance_km"].median():.1f} km\n'
    stats_text += f'Temporal Lag: mean={matches_df["temporal_lag_years"].mean():.1f} yr, '
    stats_text += f'median={median_lag:.1f} yr'

    ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.85,
                     edgecolor='black', linewidth=1.5),
            family='monospace')

    return fig

def main():
    # Load data
    matches_df = load_data()

    # Create figure
    fig = create_figure(matches_df)

    # Save outputs
    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)

    print("Saving PDF...")
    fig.savefig(output_dir / "landuse_comparison.pdf",
                dpi=300, bbox_inches='tight', format='pdf')

    print("Saving PNG...")
    fig.savefig(output_dir / "landuse_comparison.png",
                dpi=300, bbox_inches='tight', format='png')

    print("Land use comparison complete!")
    print(f"  PDF: {output_dir / 'landuse_comparison.pdf'}")
    print(f"  PNG: {output_dir / 'landuse_comparison.png'}")

    # Print summary statistics by land use
    print("\nSummary Statistics by Land Use:")
    for land_use in ['Cropland', 'Pasture', 'Plantation forest']:
        subset = matches_df[matches_df['Predominant_land_use'] == land_use]
        dist = subset['distance_km'].values
        lag = subset['temporal_lag_years'].values
        print(f"\n  {land_use} (n={len(subset):,}):")
        print(f"    Distance: mean={dist.mean():.1f} km, median={np.median(dist):.1f} km")
        print(f"    Temporal lag: mean={lag.mean():.1f} yr, median={np.median(lag):.1f} yr")

if __name__ == "__main__":
    main()
