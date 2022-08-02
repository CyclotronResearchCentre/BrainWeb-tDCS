#!/usr/bin/env python3

from pathlib import Path

import duckdb
import pandas as pd

# Nextflow input parameters
ROI = "${roi}"
DB_PATH = Path("${db}")


if __name__ == "__main__":
    # Connect to DB
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    conn.execute("PRAGMA threads=1")
    conn.execute("PRAGMA memory_limit='8GB'")
    # Fetch data
    df = conn.execute(
        f"""
        SELECT
            subject AS sub,
            x, y, z,
            area,
            volume,
            depth
        FROM full_roi_profiles
        WHERE name = '{ROI}'
        ORDER BY subject
        """
    ).fetchdf()
    # Save CSV file
    df.to_csv(f"roi-{ROI}.csv", sep=";", index=False)
