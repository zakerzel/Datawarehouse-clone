"""Global Bivariate Moran's I for one cross-variable spatial relationship."""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
from esda import Moran_BV
from libpysal.weights.spatial_lag import lag_spatial

from phase3_common import (
    load_ageb_kpis,
    numeric_subset,
    output_dir,
    queen_weights,
    standardize,
    write_json,
)

DEFAULT_X = "business_density"
DEFAULT_Y = "crime_records_per_1000"


def run(
    dataset_id: int,
    x_name: str = DEFAULT_X,
    y_name: str = DEFAULT_Y,
    permutations: int = 999,
    seed: int = 42,
) -> dict:
    frame = load_ageb_kpis(dataset_id)
    subset, data_audit = numeric_subset(frame, [x_name, y_name])
    weights, weights_audit = queen_weights(subset)
    x = subset[x_name].to_numpy(dtype=float)
    y = subset[y_name].to_numpy(dtype=float)
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        raise ValueError("Bivariate Moran's I is undefined for constant variables")

    np.random.seed(seed)
    moran = Moran_BV(x, y, weights, permutations=permutations)
    zx = standardize(x)
    zy = standardize(y)
    lag_y = lag_spatial(weights, zy)

    destination = output_dir(dataset_id) / "bivariate_moran"
    destination.mkdir(parents=True, exist_ok=True)
    figure_path = destination / f"bivariate_moran_{x_name}__{y_name}.png"
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(zx, lag_y, alpha=0.55)
    xlim = max(abs(zx.min()), abs(zx.max()))
    xx = np.linspace(-xlim, xlim, 100)
    ax.plot(xx, moran.I * xx)
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.set_xlabel(f"Standardized local {x_name}")
    ax.set_ylabel(f"Spatial lag of standardized {y_name}")
    ax.set_title(
        f"Bivariate Moran's I\n{x_name} -> spatial lag({y_name})\n"
        f"I={moran.I:.4f}, p(sim)={moran.p_sim:.4f}"
    )
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    payload = {
        "dataset_id": dataset_id,
        "unit": "AGEB urbana, CDMX",
        "x_local": x_name,
        "y_spatial_lag": y_name,
        "moran_bv_i": float(moran.I),
        "p_sim": float(moran.p_sim),
        "z_sim": float(moran.z_sim),
        "significant_at_0_05": bool(moran.p_sim < 0.05),
        "permutations": int(permutations),
        "seed": int(seed),
        "data_audit": data_audit,
        "weights_audit": weights_audit,
        "figure": str(figure_path),
        "interpretation_note": (
            "The statistic compares local X with the spatial lag of Y in neighboring "
            "AGEB under Queen contiguity. It does not establish causation."
        ),
    }
    write_json(destination / "bivariate_moran_summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True, type=int)
    parser.add_argument("--x", default=DEFAULT_X)
    parser.add_argument("--y", default=DEFAULT_Y)
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(args.dataset_id, args.x, args.y, args.permutations, args.seed)
