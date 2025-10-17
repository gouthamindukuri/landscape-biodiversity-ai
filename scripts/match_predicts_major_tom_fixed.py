#!/usr/bin/env python3
"""
Match PREDICTS sites to nearest Major TOM patches using proper haversine distance.
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

AG_LAND_USES = {"Cropland", "Pasture", "Plantation forest"}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate haversine distance in km between two points.
    Vectorized for numpy arrays.
    """
    R = 6371  # Earth radius in km

    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)

    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c

def load_predicts_sites(paths):
    """Load agricultural PREDICTS sites."""
    cols = [
        "Site_number", "Source_ID", "Latitude", "Longitude",
        "Predominant_land_use", "Sample_midpoint", "Country", "Use_intensity"
    ]
    frames = []
    for path in paths:
        df = pd.read_csv(path, usecols=cols)
        df["source_file"] = path.name
        frames.append(df)

    sites = pd.concat(frames, ignore_index=True)
    sites = sites[sites["Predominant_land_use"].isin(AG_LAND_USES)].copy()
    sites = sites.dropna(subset=["Latitude", "Longitude", "Sample_midpoint"])
    sites["Sample_midpoint"] = pd.to_datetime(sites["Sample_midpoint"], errors="coerce")
    sites = sites.dropna(subset=["Sample_midpoint"])
    sites["site_uid"] = sites["Source_ID"].astype(str) + "::" + sites["Site_number"].astype(str)
    return sites.reset_index(drop=True)

def match_nearest_patches(sites, metadata_path, search_radius_deg=1.0, max_candidates=1000, max_cloud_cover=50):
    """
    Match each PREDICTS site to nearest Major TOM patch.
    Use spatial filtering first, then exact haversine distance.
    """

    print(f"Loading Major TOM metadata...")
    meta_cols = ["grid_cell", "product_id", "timestamp", "cloud_cover",
                 "centre_lat", "centre_lon", "parquet_url", "parquet_row"]
    meta = pd.read_parquet(metadata_path, columns=meta_cols)
    meta["timestamp_dt"] = pd.to_datetime(meta["timestamp"], format="%Y%m%dT%H%M%S", errors="coerce")

    print(f"Loaded {len(meta):,} Major TOM patches")

    matches = []

    print(f"Matching {len(sites):,} sites...")
    for idx, site_row in sites.iterrows():
        if idx % 1000 == 0:
            print(f"  Processed {idx}/{len(sites)} sites...")

        site_lat = site_row["Latitude"]
        site_lon = site_row["Longitude"]

        # Find candidate patches within bounding box
        candidates = meta[
            (meta['centre_lat'] >= site_lat - search_radius_deg) &
            (meta['centre_lat'] <= site_lat + search_radius_deg) &
            (meta['centre_lon'] >= site_lon - search_radius_deg) &
            (meta['centre_lon'] <= site_lon + search_radius_deg)
        ].copy()

        if len(candidates) == 0:
            # No patches nearby
            matches.append({
                **site_row.to_dict(),
                "product_id": None,
                "eo_timestamp": None,
                "lag_days": None,
                "cloud_cover": None,
                "distance_km": None,
                "parquet_url": None,
                "parquet_row": None,
                "grid_cell": None
            })
            continue

        # Calculate exact haversine distance for candidates
        candidates["distance_km"] = haversine_distance(
            site_lat, site_lon,
            candidates["centre_lat"].values,
            candidates["centre_lon"].values
        )

        # Filter by cloud cover threshold
        candidates = candidates[candidates["cloud_cover"] <= max_cloud_cover]

        if len(candidates) == 0:
            # No patches with acceptable cloud cover
            matches.append({
                **site_row.to_dict(),
                "product_id": None,
                "eo_timestamp": None,
                "lag_days": None,
                "cloud_cover": None,
                "distance_km": None,
                "parquet_url": None,
                "parquet_row": None,
                "grid_cell": None
            })
            continue

        # Take top candidates by distance
        candidates = candidates.nsmallest(max_candidates, "distance_km")

        # Calculate temporal lag
        candidates["lag_days"] = (candidates["timestamp_dt"] - site_row["Sample_midpoint"]).abs().dt.days

        # Sort by distance first (spatial proximity most important), then temporal lag, then cloud cover
        candidates = candidates.sort_values(["distance_km", "lag_days", "cloud_cover"])

        # Take best match
        best = candidates.iloc[0]

        matches.append({
            **site_row.to_dict(),
            "product_id": best["product_id"],
            "eo_timestamp": best["timestamp_dt"],
            "lag_days": int(best["lag_days"]),
            "cloud_cover": float(best["cloud_cover"]),
            "distance_km": float(best["distance_km"]),
            "parquet_url": best["parquet_url"],
            "parquet_row": int(best["parquet_row"]),
            "grid_cell": best["grid_cell"]
        })

    return pd.DataFrame(matches)

def main():
    predicts_2016 = Path("data/predicts_2016/site-level-summaries.csv")
    predicts_2022 = Path("data/predicts_2022/site-level-summary.csv")
    metadata = Path("data/major_tom/core_s2l1c_metadata.parquet")
    output = Path("data/major_tom/predicts_s2_matches_fixed.json")

    sites = load_predicts_sites([predicts_2016, predicts_2022])
    print(f"Loaded {len(sites):,} agricultural sites from PREDICTS")

    matches = match_nearest_patches(sites, metadata, search_radius_deg=1.0, max_cloud_cover=50)

    matched = matches["product_id"].notna().sum()
    unmatched = matches["product_id"].isna().sum()

    print(f"\nMatched {matched:,} sites to Major TOM patches")
    print(f"Unmatched: {unmatched:,} sites")

    if matched > 0:
        matched_df = matches[matches["product_id"].notna()]
        print(f"\nDistance statistics (km):")
        print(matched_df["distance_km"].describe())

        print(f"\nDistance bins:")
        print(f"  < 1 km: {(matched_df['distance_km'] < 1).sum():,}")
        print(f"  < 5 km: {(matched_df['distance_km'] < 5).sum():,}")
        print(f"  < 10 km: {(matched_df['distance_km'] < 10).sum():,}")
        print(f"  < 20 km: {(matched_df['distance_km'] < 20).sum():,}")

        print(f"\nTemporal lag statistics (days):")
        print(matched_df["lag_days"].describe())

    # Save
    output.parent.mkdir(parents=True, exist_ok=True)
    records = matches.to_dict(orient="records")
    with output.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    print(f"\nSaved {len(records):,} matches to {output}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
