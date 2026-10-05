"""Shared utilities for Phase 3 spatial analytics.

Phase 3 must consume analytical exports generated from PostgreSQL/PostGIS,
never raw source files. Missing values are preserved and exclusions are explicit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
from libpysal.weights import Queen

from database import ROOT


def input_dir(dataset_id: int) -> Path:
    return ROOT / "outputs" / "cdmx" / "phase3_inputs" / str(dataset_id)


def output_dir(dataset_id: int) -> Path:
    path = ROOT / "outputs" / "cdmx" / "phase3" / str(dataset_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_ageb_kpis(dataset_id: int) -> gpd.GeoDataFrame:
    """Load KPI attributes and AGEB geometry exported from the DW."""
    source = input_dir(dataset_id)
    kpi_path = source / "kpi_ageb.csv"
    geo_path = source / "areas.geojson"

    if not kpi_path.exists() or not geo_path.exists():
        raise FileNotFoundError(
            "Phase 3 inputs are missing. Run "
            f"'python src/export_analysis.py --dataset-id {dataset_id}' first."
        )

    kpis = pd.read_csv(kpi_path, dtype={"cvegeo": "string"})
    areas = gpd.read_file(geo_path)

    if "CVEGEO" in areas.columns and "cvegeo" not in areas.columns:
        areas = areas.rename(columns={"CVEGEO": "cvegeo"})
    areas["cvegeo"] = areas["cvegeo"].astype("string")

    required = {"dataset_id", "geography_id", "cvegeo"}
    missing_kpi = required.difference(kpis.columns)
    missing_geo = required.difference(areas.columns)
    if missing_kpi or missing_geo:
        raise ValueError(
            f"Missing join columns; KPI={sorted(missing_kpi)}, "
            f"geometry={sorted(missing_geo)}"
        )

    if kpis.duplicated(["dataset_id", "geography_id"]).any():
        raise ValueError("kpi_ageb must contain one row per dataset/geography")
    if areas.duplicated(["dataset_id", "geography_id"]).any():
        raise ValueError("areas.geojson must contain one geometry per dataset/geography")

    merged = areas.merge(
        kpis,
        on=["dataset_id", "geography_id", "cvegeo"],
        how="inner",
        validate="one_to_one",
    )

    if len(merged) != len(kpis):
        raise ValueError(
            f"Geometry/KPI mismatch: {len(kpis)} KPI rows, {len(merged)} matched rows"
        )
    if merged.crs is None:
        raise ValueError("AGEB geometry has no CRS")
    if merged.geometry.isna().any() or merged.geometry.is_empty.any():
        raise ValueError("AGEB geometry contains null or empty geometries")
    if not merged.is_valid.all():
        raise ValueError("AGEB geometry contains invalid geometries")

    return merged


def numeric_subset(
    frame: gpd.GeoDataFrame,
    columns: Iterable[str],
) -> tuple[gpd.GeoDataFrame, dict]:
    """Return rows with finite values for the requested variables.

    Null/invalid observations are excluded rather than imputed as zero.
    """
    columns = list(columns)
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise KeyError(f"Missing analytical columns: {missing}")

    converted = frame.copy()
    for column in columns:
        converted[column] = pd.to_numeric(converted[column], errors="coerce")

    finite = np.ones(len(converted), dtype=bool)
    for column in columns:
        finite &= np.isfinite(converted[column].to_numpy(dtype=float, na_value=np.nan))

    subset = converted.loc[finite].copy()
    audit = {
        "requested_columns": columns,
        "input_rows": int(len(frame)),
        "included_rows": int(len(subset)),
        "excluded_rows": int(len(frame) - len(subset)),
    }
    if subset.empty:
        raise ValueError(f"No complete finite observations for {columns}")
    return subset, audit


def queen_weights(frame: gpd.GeoDataFrame) -> tuple[Queen, dict]:
    """Build Queen contiguity weights and return a topology audit.

    Islands are reported, not silently connected by distance or KNN.
    This keeps the neighborhood definition transparent for interpretation.
    """
    if frame.empty:
        raise ValueError("Cannot build spatial weights for an empty frame")
    if frame.crs is None:
        raise ValueError("A CRS is required before building spatial weights")

    ids = frame["geography_id"].astype(str).tolist()
    weights = Queen.from_dataframe(frame, ids=ids, use_index=False)
    audit = {
        "rule": "Queen contiguity (shared edge or vertex)",
        "n": int(weights.n),
        "islands": [str(v) for v in weights.islands],
        "island_count": int(len(weights.islands)),
        "components": int(weights.n_components),
        "min_neighbors": int(min(len(v) for v in weights.neighbors.values())),
        "max_neighbors": int(max(len(v) for v in weights.neighbors.values())),
        "mean_neighbors": float(
            np.mean([len(v) for v in weights.neighbors.values()])
        ),
    }
    weights.transform = "r"
    return weights, audit


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
