"""Correlation analysis for at least three DW-derived KPI relationships."""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from phase3_common import load_ageb_kpis, numeric_subset, output_dir, write_json

DEFAULT_RELATIONSHIPS = [
    ("population_density", "business_density"),
    ("population_density", "crime_records_per_1000"),
    ("business_density", "crime_records_per_1000"),
]


def outlier_share(values: np.ndarray) -> float:
    q1, q3 = np.quantile(values, [0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0:
        median = np.median(values)
        return float(np.mean(values != median))
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return float(np.mean((values < lower) | (values > upper)))


def choose_method(x: np.ndarray, y: np.ndarray) -> tuple[str, dict]:
    """Choose Pearson for roughly symmetric/low-outlier pairs; otherwise Spearman."""
    diagnostics = {
        "x_skew": float(stats.skew(x, bias=False)),
        "y_skew": float(stats.skew(y, bias=False)),
        "x_outlier_share": outlier_share(x),
        "y_outlier_share": outlier_share(y),
    }
    use_spearman = (
        abs(diagnostics["x_skew"]) > 1.0
        or abs(diagnostics["y_skew"]) > 1.0
        or diagnostics["x_outlier_share"] > 0.05
        or diagnostics["y_outlier_share"] > 0.05
    )
    method = "spearman" if use_spearman else "pearson"
    diagnostics["selection_rule"] = (
        "Spearman if |skew| > 1 or IQR-outlier share > 5% in either variable; "
        "otherwise Pearson."
    )
    return method, diagnostics


def analyze_pair(frame, x_name: str, y_name: str, destination) -> dict:
    subset, audit = numeric_subset(frame, [x_name, y_name])
    x = subset[x_name].to_numpy(dtype=float)
    y = subset[y_name].to_numpy(dtype=float)
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        raise ValueError(f"Correlation undefined for constant pair: {x_name}, {y_name}")

    method, diagnostics = choose_method(x, y)
    if method == "spearman":
        result = stats.spearmanr(x, y)
    else:
        result = stats.pearsonr(x, y)

    coefficient = float(result.statistic)
    p_value = float(result.pvalue)

    figure_path = destination / f"correlation_{x_name}__{y_name}.png"
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(x, y, alpha=0.45)
    if method == "pearson":
        slope, intercept = np.polyfit(x, y, 1)
        xx = np.linspace(x.min(), x.max(), 100)
        ax.plot(xx, slope * xx + intercept)
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    ax.set_title(
        f"{method.title()} correlation\n"
        f"r={coefficient:.3f}, p={p_value:.4g}, n={len(subset)}"
    )
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    return {
        "x": x_name,
        "y": y_name,
        "method": method,
        "coefficient": coefficient,
        "p_value": p_value,
        "significant_at_0_05": bool(p_value < 0.05),
        "n": int(len(subset)),
        "diagnostics": diagnostics,
        "data_audit": audit,
        "figure": str(figure_path),
        "caution": "Correlation does not imply causation.",
    }


def run(dataset_id: int, relationships: list[tuple[str, str]]) -> dict:
    if len(relationships) < 3:
        raise ValueError("The project requires at least three relationships")

    frame = load_ageb_kpis(dataset_id)
    destination = output_dir(dataset_id) / "correlations"
    destination.mkdir(parents=True, exist_ok=True)

    results = [analyze_pair(frame, x, y, destination) for x, y in relationships]
    payload = {
        "dataset_id": dataset_id,
        "unit": "AGEB urbana, CDMX",
        "relationships": results,
    }
    write_json(destination / "correlations_summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def parse_relationships(items: list[str] | None) -> list[tuple[str, str]]:
    if not items:
        return DEFAULT_RELATIONSHIPS
    parsed = []
    for item in items:
        if ":" not in item:
            raise ValueError("Relationships must use x:y format")
        x, y = item.split(":", 1)
        parsed.append((x.strip(), y.strip()))
    return parsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True, type=int)
    parser.add_argument(
        "--relationships",
        nargs="*",
        help="Optional x:y pairs; at least three are required.",
    )
    args = parser.parse_args()
    run(args.dataset_id, parse_relationships(args.relationships))
