"""Generate required geographic-distribution maps from DW-derived KPIs."""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt

from phase3_common import load_ageb_kpis, numeric_subset, output_dir, write_json

DEFAULT_VARIABLES = [
    "population_density",
    "business_density",
    "crime_records_per_1000",
]


def run(dataset_id: int, variables: list[str]) -> dict:
    frame = load_ageb_kpis(dataset_id)
    destination = output_dir(dataset_id) / "geographic_distribution"
    destination.mkdir(parents=True, exist_ok=True)

    results = []
    for variable in variables:
        subset, audit = numeric_subset(frame, [variable])
        figure_path = destination / f"map_{variable}.png"
        fig, ax = plt.subplots(figsize=(8, 8))
        subset.plot(column=variable, legend=True, ax=ax)
        ax.set_title(f"CDMX AGEB — {variable}")
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(figure_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        results.append(
            {
                "variable": variable,
                "data_audit": audit,
                "min": float(subset[variable].min()),
                "median": float(subset[variable].median()),
                "max": float(subset[variable].max()),
                "figure": str(figure_path),
            }
        )

    payload = {
        "dataset_id": dataset_id,
        "unit": "AGEB urbana, CDMX",
        "maps": results,
        "caution": "Mapped values are descriptive and do not imply causal relationships.",
    }
    write_json(destination / "geographic_distribution_summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True, type=int)
    parser.add_argument("--variables", nargs="+", default=DEFAULT_VARIABLES)
    args = parser.parse_args()
    run(args.dataset_id, args.variables)
