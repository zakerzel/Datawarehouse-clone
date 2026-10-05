"""Local Moran's I / LISA cluster and spatial-outlier analysis."""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
from esda import Moran_Local

from phase3_common import load_ageb_kpis, numeric_subset, output_dir, queen_weights, write_json

DEFAULT_VARIABLES = ["crime_records_per_1000", "business_density"]
QUADRANT_LABELS = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}


def classify_lisa(q: int, p_value: float, alpha: float = 0.05) -> str:
    if p_value >= alpha:
        return "Not significant"
    return QUADRANT_LABELS.get(int(q), "Unknown")


def analyze_variable(frame, variable: str, permutations: int, seed: int, alpha: float, destination) -> dict:
    subset, data_audit = numeric_subset(frame, [variable])
    weights, weights_audit = queen_weights(subset)
    values = subset[variable].to_numpy(dtype=float)
    if np.unique(values).size < 2:
        raise ValueError(f"{variable} is constant after exclusions")

    np.random.seed(seed)
    local = Moran_Local(values, weights, permutations=permutations)
    subset["lisa_i"] = local.Is
    subset["lisa_p_sim"] = local.p_sim
    subset["lisa_q"] = local.q
    subset["lisa_cluster"] = [
        classify_lisa(q, p, alpha) for q, p in zip(local.q, local.p_sim)
    ]

    counts = subset["lisa_cluster"].value_counts(dropna=False).to_dict()
    cluster_csv = destination / f"lisa_clusters_{variable}.csv"
    subset.drop(columns="geometry").to_csv(cluster_csv, index=False)

    figure_path = destination / f"lisa_map_{variable}.png"
    fig, ax = plt.subplots(figsize=(8, 8))
    subset.plot(column="lisa_cluster", categorical=True, legend=True, ax=ax)
    ax.set_title(f"Local Moran / LISA — {variable} (p < {alpha})")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return {
        "variable": variable,
        "alpha": float(alpha),
        "permutations": int(permutations),
        "seed": int(seed),
        "cluster_counts": {str(key): int(value) for key, value in counts.items()},
        "significant_count": int(np.sum(local.p_sim < alpha)),
        "data_audit": data_audit,
        "weights_audit": weights_audit,
        "table": str(cluster_csv),
        "figure": str(figure_path),
        "caution": (
            "LISA identifies local spatial association/outliers, not causal effects. "
            "Interpret only permutation-significant observations."
        ),
    }


def run(
    dataset_id: int,
    variables: list[str],
    permutations: int = 999,
    seed: int = 42,
    alpha: float = 0.05,
) -> dict:
    frame = load_ageb_kpis(dataset_id)
    destination = output_dir(dataset_id) / "lisa"
    destination.mkdir(parents=True, exist_ok=True)
    results = [
        analyze_variable(frame, variable, permutations, seed, alpha, destination)
        for variable in variables
    ]
    payload = {
        "dataset_id": dataset_id,
        "unit": "AGEB urbana, CDMX",
        "neighborhood_rule": "Queen contiguity",
        "variables": results,
    }
    write_json(destination / "lisa_summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True, type=int)
    parser.add_argument("--variables", nargs="+", default=DEFAULT_VARIABLES)
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args()
    run(args.dataset_id, args.variables, args.permutations, args.seed, args.alpha)
