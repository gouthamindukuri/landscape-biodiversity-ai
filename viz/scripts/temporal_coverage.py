#!/usr/bin/env python3
"""
Temporal Coverage
Shows PREDICTS and Major TOM temporal distributions with color-coded dual y-axes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

def load_data():
    print("Loading data...")

    predicts_2016 = pd.read_csv("data/predicts_2016/site-level-summaries.csv")
    predicts_2022 = pd.read_csv("data/predicts_2022/site-level-summary.csv")
    predicts = pd.concat([predicts_2016, predicts_2022], ignore_index=True)

    ag_land_uses = {"Cropland", "Pasture", "Plantation forest"}
    predicts = predicts[predicts["Predominant_land_use"].isin(ag_land_uses)]
    predicts["Sample_midpoint"] = pd.to_datetime(predicts["Sample_midpoint"], errors="coerce")
    predicts = predicts.dropna(subset=["Sample_midpoint"])
    predicts["year"] = predicts["Sample_midpoint"].dt.year

    major_tom = pd.read_parquet("data/major_tom/core_s2l1c_metadata.parquet")
    major_tom["timestamp"] = pd.to_datetime(major_tom["timestamp"], format="%Y%m%dT%H%M%S")
    major_tom["year"] = major_tom["timestamp"].dt.year

    with open("data/major_tom/predicts_s2_matches_fixed.json") as f:
        matches = json.load(f)
    matches_df = pd.DataFrame(matches)
    matches_df = matches_df[matches_df["product_id"].notna()]
    matches_df["Sample_midpoint"] = pd.to_datetime(matches_df["Sample_midpoint"])
    matches_df["eo_timestamp"] = pd.to_datetime(matches_df["eo_timestamp"])
    matches_df["predicts_year"] = matches_df["Sample_midpoint"].dt.year
    matches_df["major_tom_year"] = matches_df["eo_timestamp"].dt.year

    return predicts, major_tom, matches_df

def create_figure(predicts, major_tom, matches_df):
    print("Creating dual y-axis figure...")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    predicts_counts = predicts.groupby("year").size()
    major_tom_counts = major_tom.groupby("year").size() / 1000

    # Calculate overlap: PREDICTS sites where BOTH predicts_year AND major_tom_year are in 2016-2018
    overlap_sites = len(matches_df[
        (matches_df["predicts_year"] >= 2016) & (matches_df["predicts_year"] <= 2018) &
        (matches_df["major_tom_year"] >= 2016) & (matches_df["major_tom_year"] <= 2018)
    ])
    gap_sites = len(matches_df) - overlap_sites

    overlap_pct = overlap_sites / len(matches_df) * 100
    gap_pct = gap_sites / len(matches_df) * 100

    # Plot PREDICTS on left y-axis
    ax1.fill_between(predicts_counts.index, 0, predicts_counts.values,
                     color='#FF8C00', alpha=0.6, label='PREDICTS Sites')
    ax1.plot(predicts_counts.index, predicts_counts.values,
             color='#FF6500', linewidth=2.5)

    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('PREDICTS Sites per Year', fontsize=11, fontweight='bold', color='#FF6500')
    ax1.tick_params(axis='y', labelcolor='#FF6500', labelsize=10)
    ax1.set_xlim(1990, 2025)
    ax1.set_ylim(0, 1800)

    # Plot Major TOM on right y-axis
    ax2 = ax1.twinx()
    ax2.fill_between(major_tom_counts.index, 0, major_tom_counts.values,
                     color='#1E90FF', alpha=0.5, label='Major TOM Patches')
    ax2.plot(major_tom_counts.index, major_tom_counts.values,
             color='#0066CC', linewidth=2.5, linestyle='--')

    ax2.set_ylabel('Major TOM Patches per Year (thousands)', fontsize=11,
                   fontweight='bold', color='#0066CC')
    ax2.tick_params(axis='y', labelcolor='#0066CC', labelsize=10)
    ax2.set_ylim(0, 550)

    # Overlap region shading
    ax1.axvspan(2016, 2018, alpha=0.2, color='green', zorder=0)

    # Sentinel-2 launch line
    ax1.axvline(2015.5, color='black', linestyle=':', linewidth=2, alpha=0.7)
    ax1.text(2015.5, 1650, 'Sentinel-2\nLaunch', fontsize=9, ha='center',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9))

    # Overlap annotation (higher position)
    ax1.text(2017, 700, f'Overlap\n{overlap_sites} sites', fontsize=9, ha='center',
             fontweight='bold', color='darkgreen',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))

    # Legend (top left corner)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#FF8C00', alpha=0.6, edgecolor='#FF6500',
              linewidth=2, label='PREDICTS Sites'),
        Patch(facecolor='#1E90FF', alpha=0.5, edgecolor='#0066CC',
              linewidth=2, label='Major TOM Patches (thousands)'),
        Patch(facecolor='green', alpha=0.2, label='Overlap Period (2016-2018)')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=10,
              framealpha=0.95, edgecolor='black')

    # Statistics box (below legend, top left)
    stats_text = f'Gap: {gap_sites:,} sites ({gap_pct:.1f}%)\n'
    stats_text += f'Overlap: {overlap_sites:,} sites ({overlap_pct:.1f}%)'
    ax1.text(0.02, 0.70, stats_text, transform=ax1.transAxes,
             fontsize=10, va='top', ha='left', family='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat',
                      alpha=0.85, edgecolor='black', linewidth=1.5))

    ax1.set_title('Temporal Coverage: PREDICTS vs Major TOM',
                  fontsize=13, fontweight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    return fig

def main():
    predicts, major_tom, matches_df = load_data()
    fig = create_figure(predicts, major_tom, matches_df)

    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)

    print("Saving outputs...")
    fig.savefig(output_dir / "temporal_coverage.pdf", dpi=300, bbox_inches='tight')
    fig.savefig(output_dir / "temporal_coverage.png", dpi=300, bbox_inches='tight')

    print("  PDF: viz/temporal_coverage.pdf")
    print("  PNG: viz/temporal_coverage.png")

if __name__ == "__main__":
    main()
