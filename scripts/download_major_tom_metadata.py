#!/usr/bin/env python3
"""
Download Major TOM metadata parquet files required for scene matching.
Currently supports Sentinel-2 Level-1C (Core-S2L1C) metadata.
"""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

S2L1C_METADATA_URL = (
    "https://huggingface.co/datasets/Major-TOM/Core-S2L1C/"
    "resolve/main/metadata.parquet?download=1"
)


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[download] {url} → {dest}")
    urllib.request.urlretrieve(url, dest)
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download Major TOM metadata parquet files."
    )
    parser.add_argument(
        "--s2l1c",
        metavar="PATH",
        type=Path,
        default=Path("data/major_tom/core_s2l1c_metadata.parquet"),
        help="Destination path for Sentinel-2 L1C metadata parquet.",
    )
    args = parser.parse_args()

    download(S2L1C_METADATA_URL, args.s2l1c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
