#!/usr/bin/env python3
"""
PREDICTS Database Exploration Script
Analyzes geographic coverage, biodiversity metrics, and land-use patterns.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point

DATA_DIR = Path("data")
PREDICTS_2016_DIR = DATA_DIR / "predicts_2016"
PREDICTS_2022_DIR = DATA_DIR / "predicts_2022"

print("PREDICTS DATABASE EXPLORATION\n")

print("Loading PREDICTS 2016 site-level summaries...")
sites_2016 = pd.read_csv(PREDICTS_2016_DIR / "site-level-summaries.csv", low_memory=False)
print(f"Loaded {len(sites_2016):,} sites from 2016 release")

print("\nLoading PREDICTS 2022 site-level summaries...")
sites_2022 = pd.read_csv(PREDICTS_2022_DIR / "site-level-summary.csv", low_memory=False)
print(f"Loaded {len(sites_2022):,} sites from 2022 addition")

print("\nCombining datasets...")
sites_2016['source_dataset'] = '2016'
sites_2022['source_dataset'] = '2022'
sites_all = pd.concat([sites_2016, sites_2022], ignore_index=True)
print(f"Total sites: {len(sites_all):,}")

print("\nBASIC STATISTICS\n")

print(f"Geographic Coverage:")
print(f"  Countries: {sites_all['Country'].nunique()}")
print(f"  Latitude range: {sites_all['Latitude'].min():.2f} to {sites_all['Latitude'].max():.2f}")
print(f"  Longitude range: {sites_all['Longitude'].min():.2f} to {sites_all['Longitude'].max():.2f}")

print(f"\nTop 10 Countries by Site Count:")
country_counts = sites_all['Country'].value_counts().head(10)
for country, count in country_counts.items():
    print(f"  {country:30s}: {count:6,} sites")

print(f"\nPredominant Land Use Types:")
landuse_counts = sites_all['Predominant_land_use'].value_counts()
for landuse, count in landuse_counts.items():
    print(f"  {landuse:40s}: {count:6,} sites")

print(f"\nUse Intensity Distribution:")
intensity_counts = sites_all['Use_intensity'].value_counts()
for intensity, count in intensity_counts.items():
    print(f"  {intensity:30s}: {count:6,} sites")

print(f"\nBiodiversity Metrics:")
metric_counts = sites_all['Diversity_metric'].value_counts()
for metric, count in metric_counts.items():
    print(f"  {metric:40s}: {count:6,} sites")

print("\nAGRICULTURAL LANDSCAPES (GBF Target 10 Focus)\n")

ag_landuses = ['Cropland', 'Pasture', 'Plantation forest']
ag_sites = sites_all[sites_all['Predominant_land_use'].isin(ag_landuses)]
print(f"Agricultural sites: {len(ag_sites):,} ({len(ag_sites)/len(sites_all)*100:.1f}%)")

print(f"\n  By land use type:")
for landuse in ag_landuses:
    count = len(sites_all[sites_all['Predominant_land_use'] == landuse])
    print(f"  {landuse:30s}: {count:6,} sites")

print(f"\n  Top 10 countries for agricultural sites:")
ag_country_counts = ag_sites['Country'].value_counts().head(10)
for country, count in ag_country_counts.items():
    print(f"  {country:30s}: {count:6,} sites")

print("\nTEMPORAL COVERAGE ANALYSIS\n")

print("Checking for sites sampled multiple times...")
sites_with_coords = sites_all.dropna(subset=['Latitude', 'Longitude'])
coord_groups = sites_with_coords.groupby(['Latitude', 'Longitude']).size()
multi_sampled = coord_groups[coord_groups > 1]

print(f"  Total unique coordinate pairs: {len(coord_groups):,}")
print(f"  Coordinate pairs with multiple samples: {len(multi_sampled):,}")
print(f"  Percentage with temporal data: {len(multi_sampled)/len(coord_groups)*100:.2f}%")

if len(multi_sampled) > 0:
    print(f"\n  Distribution of samples per location:")
    sample_dist = coord_groups.value_counts().sort_index()
    for num_samples, count in sample_dist.items():
        if num_samples > 1:
            print(f"  {num_samples} samples: {count:,} locations")

print("\nSampling date coverage:")
sites_with_dates = sites_all.dropna(subset=['Sample_midpoint'])
print(f"  Sites with date information: {len(sites_with_dates):,} ({len(sites_with_dates)/len(sites_all)*100:.1f}%)")

if len(sites_with_dates) > 0:
    sites_with_dates_copy = sites_with_dates.copy()
    sites_with_dates_copy['year'] = pd.to_datetime(sites_with_dates_copy['Sample_midpoint'], errors='coerce').dt.year
    year_range = sites_with_dates_copy['year'].dropna()
    if len(year_range) > 0:
        print(f"  Year range: {int(year_range.min())} to {int(year_range.max())}")

print("\nGEOGRAPHIC HOTSPOTS FOR BIODIVERSITY DATA\n")

print("Creating geographic analysis...")
sites_geo = sites_all.dropna(subset=['Latitude', 'Longitude']).copy()
geometry = [Point(xy) for xy in zip(sites_geo['Longitude'], sites_geo['Latitude'])]
sites_gdf = gpd.GeoDataFrame(sites_geo, geometry=geometry, crs='EPSG:4326')

print("  Creating 10 x 10 degree grid analysis...")
sites_gdf['lat_bin'] = (sites_gdf['Latitude'] // 10) * 10
sites_gdf['lon_bin'] = (sites_gdf['Longitude'] // 10) * 10
grid_counts = sites_gdf.groupby(['lat_bin', 'lon_bin']).size().sort_values(ascending=False)

print(f"\n  Top 10 densest 10x10 degree grid cells:")
for (lat, lon), count in grid_counts.head(10).items():
    print(f"  Lat {lat:+5.0f} to {lat+10:+5.0f}, Lon {lon:+6.0f} to {lon+10:+6.0f}: {count:5,} sites")

print("\n  Top 10 agricultural hotspots (10x10 degree grid):")
ag_gdf = sites_gdf[sites_gdf['Predominant_land_use'].isin(ag_landuses)]
ag_grid_counts = ag_gdf.groupby(['lat_bin', 'lon_bin']).size().sort_values(ascending=False)

for (lat, lon), count in ag_grid_counts.head(10).items():
    print(f"  Lat {lat:+5.0f} to {lat+10:+5.0f}, Lon {lon:+6.0f} to {lon+10:+6.0f}: {count:5,} sites")

print("\nEXPORTING ANALYSIS\n")

summary = {
    'total_sites': len(sites_all),
    'countries': sites_all['Country'].nunique(),
    'agricultural_sites': len(ag_sites),
    'temporal_locations': len(multi_sampled),
    'sites_with_dates': len(sites_with_dates),
}

print(f"Summary statistics:")
for key, value in summary.items():
    print(f"  {key}: {value:,}")

print(f"\nSaving geographic data...")
output_file = DATA_DIR / "processed" / "predicts_sites_geo.gpkg"
output_file.parent.mkdir(parents=True, exist_ok=True)
sites_gdf.to_file(output_file, driver='GPKG')
print(f"Saved to {output_file}")

print("\nEXPLORATION COMPLETE\n")
print(f"Key Findings:")
print(f"1. Total sites: {len(sites_all):,}")
print(f"2. Agricultural sites: {len(ag_sites):,} ({len(ag_sites)/len(sites_all)*100:.1f}%)")
print(f"3. Temporal coverage: {len(multi_sampled)/len(coord_groups)*100:.2f}% of locations have repeat samples")
print(f"4. Geographic spread: {sites_all['Country'].nunique()} countries")
print(f"\nRecommendation: Focus on regions with dense agricultural site coverage for Major TOM matching")
