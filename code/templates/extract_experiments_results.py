#!/usr/bin/env python3

from pathlib import Path

import duckdb
import pandas as pd

# Nextflow input parameters
ROI = "${roi}"
ANODE = "${anode}"
CATHODE = "${cathode}"
DB_PATH = Path("${db}")


if __name__ == "__main__":
    # Connect to DB
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    conn.execute("PRAGMA threads=8")
    conn.execute("PRAGMA memory_limit='8GB'")
    # Get mean data
    anodes = ", ".join([f"'{ANODE}{s}'" for s in ("", "A", "P", "C", "L")])
    df = conn.execute(
        f"""
        SELECT
            subject AS sub,
            anode,
            conductivity_profile AS k_id,
            avg(wm) AS k_wm,
            avg(gm) AS k_gm,
            avg(csf) AS k_csf,
            avg(skl) AS k_skl,
            avg(sft) AS k_sft,
            avg(v) * 1000 AS v,
            avg(abs(e)) * 1000 AS e,
            avg(abs(e_x)) * 1000 AS e_x,
            avg(abs(e_y)) * 1000 AS e_y,
            avg(abs(e_z)) * 1000 AS e_z,
            avg(abs(e_r)) * 1000 AS e_r,
            avg(abs(e_t)) * 1000 AS e_t,
            avg(abs(j)) * 1000 AS j,
            avg(abs(j_x)) * 1000 AS j_x,
            avg(abs(j_y)) * 1000 AS j_y,
            avg(abs(j_z)) * 1000 AS j_z,
            avg(abs(j_r)) * 1000 AS j_r,
            avg(abs(j_t)) * 1000 AS j_t
        FROM full_records AS r
        LEFT JOIN
            conductivity_profiles AS c
        ON
            r.conductivity_profile = c.id
        WHERE
            roi = '{ROI}'
            AND anode IN ({anodes})
            AND cathode = '{CATHODE}'
        GROUP BY
            roi,
            subject,
            anode,
            cathode,
            conductivity_profile
        """        
    ).fetchdf()
    # Format conductivity
    df["k_id"] = pd.Categorical(
        df["k_id"].apply(lambda id: (id + 1) % 21),
        categories=list(range(21)),
    )
    df["k"] = pd.Categorical(
        df["k_id"].apply(
            lambda c: "reference" if c == 0 else f"halton_{c}"
        ),
        categories=["reference"] + [f"halton_{i + 1}" for i in range(20)],
    )
    # Format placement
    directions = {
        "": "reference",
        "A": "anterior",
        "C": "central",
        "L": "lateral",
        "P": "posterior",
    }
    df["p"] = pd.Categorical(
        df["anode"].apply(
            lambda a: directions[
                a[len(ANODE)] if len(ANODE) < len(a) else ""
            ]
        ),
        categories=list(directions.values()),
    )
    df["p_id"] = pd.Categorical(
        df["p"].apply(lambda name: list(directions.values()).index(name)),
        categories=list(range(5)),
    )
    coordinates = {
        "reference": (0, 0),
        "anterior": (0, 1),
        "central": (1, 0),
        "lateral": (-1, 0),
        "posterior": (0, -1),
    }
    for i, axis in enumerate(("x", "y")):
        df[f"p_{axis}"] = df["p"].apply(
            lambda name: coordinates[name][i]
        )
    # Format final df
    df = df[
        [
            "sub",
            "k",
            "k_id",
            "k_wm",
            "k_gm",
            "k_csf",
            "k_skl",
            "k_sft",
            "p",
            "p_id",
            "p_x",
            "p_y",
            "v",
            "e",
            "e_x",
            "e_y",
            "e_z",
            "e_r",
            "e_t",
            "j",
            "j_x",
            "j_y",
            "j_z",
            "j_r",
            "j_t"
        ]
    ].sort_values(by=["sub", "k_id", "p_id"])
    # Save CSV file
    df.to_csv(f"roi-{ROI}_anode-{ANODE}_cathode-{CATHODE}.csv", sep=";", index=False)