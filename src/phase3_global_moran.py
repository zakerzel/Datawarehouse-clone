"""Global Moran's I for at least two selected AGEB KPIs."""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
from esda import Moran
from libpysal.weights.spatial_lag import lag_spatial

from phase3_common import (
    load_ageb_kpis,
    numeric_subset,
    output_dir,
    queen_weights,
    standardize,
    write_json,
)

DEFAULT_VARIABLES = ["crime_records_per_1000", "business_density"]


def analyze_variable(frame, variable: str, permutations: int, seed: int, destination) -> dict:
    subset, data_audit = numeric_subset(frame, [variable])
    weights, weights_audit = queen_weights(subset)
    values = subset[variable].to_numpy(dtype=float)
    if np.unique(values).size < 2:
        raise ValueError(f"{variable} is constant after exclusions")

    np.random.seed(seed)
    moran = Moran(values, weights, permutations=permutations, two_tailed=True)
    z = standardize(values)
    lag_z = lag_spatial(weights, z)

    figure_path = destination / f"moran_scatter_{variable}.png"
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(z, lag_z, alpha=0.55)
    xlim = max(abs(z.min()), abs(z.max()))
    xx = np.linspace(-xlim, xlim, 100)
    ax.plot(xx, moran.I * xx)
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.set_xlabel(f"Standardized {variable}")
    ax.set_ylabel("Spatial lag")
    ax.set_title(f"Global Moran's I — {variable}\nI={moran.I:.4f}, p(sim)={moran.p_sim:.4f}")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    return {
        "variable": variable,
        "moran_i": float(moran.I),
        "expected_i": float(moran.EI),
        "p_sim": float(moran.p_sim),
        "z_sim": float(moran.z_sim),
        "permutations": int(permutations),
        "seed": int(seed),
        "significant_at_0_05": bool(moran.p_sim < 0.05),
        "data_audit": data_audit,
        "weights_audit": weights_audit,
        "figure": str(figure_path),
        "caution": (
            "Spatial association does not imply causation. Results depend on "
            "the Queen-neighborhood rule and analytical exclusions."
        ),
    }


def run(dataset_id: int, variables: list[str], permutations: int = 999, seed: int = 42) -> dict:
    if len(variables) < 2:
        raise ValueError("Provide at least two indicators for Global Moran's I")
    frame = load_ageb_kpis(dataset_id)
    destination = output_dir(dataset_id) / "global_moran"
    destination.mkdir(parents=True, exist_ok=True)
    results = [
        analyze_variable(frame, variable, permutations, seed, destination)
        for variable in variables
    ]
    payload = {
        "dataset_id": dataset_id,
        "unit": "AGEB urbana, CDMX",
        "neighborhood_rule": "Queen contiguity",
        "variables": results,
    }
    write_json(destination / "global_moran_summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True, type=int)
    parser.add_argument("--variables", nargs="+", default=DEFAULT_VARIABLES)
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(args.dataset_id, args.variables, args.permutations, args.seed)
