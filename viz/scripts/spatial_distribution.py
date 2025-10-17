#!/usr/bin/env python3
"""
Spatial Distribution
Shows global distribution of PREDICTS agricultural sites with UK inset for detail
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import json

# Set publication-quality style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

def load_data():
    """Load matched PREDICTS sites"""
    print("Loading data...")

    with open("data/major_tom/predicts_s2_matches_fixed.json") as f:
        matches = json.load(f)

    matches_df = pd.DataFrame(matches)
    matches_df = matches_df[matches_df["product_id"].notna()]
    matches_df["Sample_midpoint"] = pd.to_datetime(matches_df["Sample_midpoint"])
    matches_df["year"] = matches_df["Sample_midpoint"].dt.year

    return matches_df

def create_figure(matches_df):
    """Create spatial distribution map with UK inset"""
    print("Creating figure with UK inset...")

    fig = plt.figure(figsize=(14, 8))

    # Main global map
    ax_main = plt.subplot(1, 1, 1, projection=ccrs.Robinson())

    # Add features
    ax_main.add_feature(cfeature.LAND, facecolor='#f0f0f0', edgecolor='none')
    ax_main.add_feature(cfeature.OCEAN, facecolor='#d9f0ff', edgecolor='none')
    ax_main.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#666666')
    ax_main.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#999999', linestyle=':')

    # Plot PREDICTS sites colored by year
    years = matches_df["year"].values
    year_min, year_max = years.min(), years.max()

    # Plot sites on main map
    scatter_main = ax_main.scatter(
        matches_df["Longitude"].values,
        matches_df["Latitude"].values,
        c=years,
        cmap='RdYlGn',
        s=5,
        alpha=0.6,
        transform=ccrs.PlateCarree(),
        edgecolor='none',
        vmin=year_min,
        vmax=year_max,
        zorder=3
    )

    # Add colorbar right below the globe (no padding)
    cbar = plt.colorbar(scatter_main, ax=ax_main, orientation='horizontal',
                       pad=0.0, aspect=40, shrink=0.6, anchor=(0.8, 0.5))
    cbar.set_label('PREDICTS Sample Year', fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    # Title
    ax_main.set_title('Global Distribution: PREDICTS Agricultural Sites (with UK Detail)',
                     fontsize=13, fontweight='bold', pad=15)

    # Add statistics text
    stats_text = f'n = {len(matches_df):,} sites\n'
    stats_text += f'Years: {int(year_min)}-{int(year_max)}\n'
    stats_text += f'Mean distance: {matches_df["distance_km"].mean():.1f} km'

    ax_main.text(0.02, 0.98, stats_text,
                transform=ax_main.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         alpha=0.9, edgecolor='black', linewidth=1))

    # Land use legend removed for cleaner visualization

    # Global extent
    ax_main.set_global()

    # Grid lines
    gl = ax_main.gridlines(draw_labels=False, linewidth=0.5,
                          color='gray', alpha=0.3, linestyle='--')

    # Create UK inset
    # Position: [left, bottom, width, height] in figure coordinates
    ax_inset = fig.add_axes([0.08, 0.20, 0.30, 0.35], projection=ccrs.PlateCarree())

    # Filter UK sites ONLY (using Country column, not geographic bounds)
    uk_sites = matches_df[matches_df["Country"] == "United Kingdom"].copy()

    # Calculate UK bounding box from actual UK site coordinates
    if len(uk_sites) > 0:
        uk_lon = [uk_sites["Longitude"].min() - 1, uk_sites["Longitude"].max() + 1]
        uk_lat = [uk_sites["Latitude"].min() - 0.5, uk_sites["Latitude"].max() + 0.5]
    else:
        uk_lon = [-11, 3]
        uk_lat = [49.5, 61]

    # Add features to inset
    ax_inset.add_feature(cfeature.LAND, facecolor='#f0f0f0', edgecolor='none')
    ax_inset.add_feature(cfeature.OCEAN, facecolor='#d9f0ff', edgecolor='none')
    ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#333333')
    ax_inset.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='#666666')

    # Plot UK sites with larger markers
    if len(uk_sites) > 0:
        scatter_uk = ax_inset.scatter(
            uk_sites["Longitude"].values,
            uk_sites["Latitude"].values,
            c=uk_sites["year"].values,
            cmap='RdYlGn',
            s=25,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.3,
            vmin=year_min,
            vmax=year_max,
            zorder=3
        )

    # Set UK extent
    ax_inset.set_extent([uk_lon[0], uk_lon[1], uk_lat[0], uk_lat[1]], crs=ccrs.PlateCarree())

    # Add gridlines to inset
    gl_inset = ax_inset.gridlines(draw_labels=True, linewidth=0.5,
                                   color='gray', alpha=0.4, linestyle='--')
    gl_inset.top_labels = False
    gl_inset.right_labels = False
    gl_inset.xlabel_style = {'size': 7}
    gl_inset.ylabel_style = {'size': 7}

    # Inset title and border
    ax_inset.set_title('UK Detail', fontsize=10, fontweight='bold', pad=8)
    ax_inset.spines['geo'].set_edgecolor('black')
    ax_inset.spines['geo'].set_linewidth(1.5)

    # Add UK site count annotation
    uk_count_text = f'UK: {len(uk_sites):,} sites'
    ax_inset.text(0.5, -0.12, uk_count_text,
                 transform=ax_inset.transAxes,
                 fontsize=8, ha='center', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          alpha=0.9, edgecolor='black', linewidth=1))

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
    fig.savefig(output_dir / "spatial_distribution.pdf",
                dpi=300, bbox_inches='tight', format='pdf')

    print("Saving PNG...")
    fig.savefig(output_dir / "spatial_distribution.png",
                dpi=300, bbox_inches='tight', format='png')

    print("Spatial distribution figure complete!")
    print(f"  PDF: {output_dir / 'spatial_distribution.pdf'}")
    print(f"  PNG: {output_dir / 'spatial_distribution.png'}")

if __name__ == "__main__":
    main()
