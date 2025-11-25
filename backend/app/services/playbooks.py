"""Analysis playbooks for common question types."""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def overview_playbook(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a high-level overview of the dataset for non-technical users.

    Returns a simple table of numeric features with min/max/mean/std and missing%.
    """
    row_count = len(df)
    col_count = df.shape[1]

    numeric_df = df.select_dtypes(include="number")
    rows = []

    if not numeric_df.empty:
        for col in numeric_df.columns:
            series = pd.to_numeric(numeric_df[col], errors="coerce")
            desc = series.describe()
            missing_pct = (
                100.0 * (1.0 - float(series.count()) / row_count) if row_count > 0 else 0.0
            )

            rows.append(
                {
                    "Feature": col,
                    "Min": round(float(desc.get("min", 0.0)), 2) if "min" in desc else None,
                    "Max": round(float(desc.get("max", 0.0)), 2) if "max" in desc else None,
                    "Mean": round(float(desc.get("mean", 0.0)), 2) if "mean" in desc else None,
                    "Std": round(float(desc.get("std", 0.0)), 2) if "std" in desc else None,
                    "Missing %": round(missing_pct, 1),
                }
            )

    visualization = {
        "type": "table",
        "data": {
            "columns": ["Feature", "Min", "Max", "Mean", "Std", "Missing %"],
            "rows": rows,
        },
        "config": {
            "title": "Dataset Overview",
        },
    }

    analysis_context = {
        "kind": "overview",
        "row_count": row_count,
        "column_count": col_count,
        "numeric_features": list(numeric_df.columns),
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


def correlation_playbook(
    df: pd.DataFrame,
    outcome: str = "Outcome",
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Analyze which numeric features are most related to the outcome.

    Returns a bar chart of top |correlation| with outcome, and embeds the full
    correlation matrix in metadata for optional advanced views.
    """
    num_df = df.select_dtypes(include="number").dropna()
    if outcome not in num_df.columns or num_df.shape[0] < 5:
        return {
            "visualization": {
                "type": "table",
                "data": {
                    "columns": num_df.columns.tolist(),
                    "rows": [],
                },
                "config": {
                    "title": "Insufficient data for correlation analysis",
                },
            },
            "analysis_context": {
                "kind": "correlation",
                "reason": "insufficient_data",
            },
        }

    corrs = num_df.corr()[outcome].drop(labels=[outcome]).dropna()
    if corrs.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": num_df.columns.tolist(), "rows": []},
                "config": {"title": "No meaningful correlations found"},
            },
            "analysis_context": {
                "kind": "correlation",
                "reason": "no_correlations",
            },
        }

    # Sort by absolute correlation strength
    corrs = corrs.reindex(corrs.abs().sort_values(ascending=False).index)
    top = corrs.head(top_n)

    labels = top.index.tolist()
    values = [round(float(v), 2) for v in top.values]

    # Full matrix for advanced/optional use
    corr_matrix = num_df.corr().fillna(0.0)
    matrix_labels = corr_matrix.columns.tolist()
    matrix = corr_matrix.values.tolist()

    visualization = {
        "type": "bar",
        "data": {
            "labels": labels,
            "values": values,
        },
        "config": {
            "title": f"Top {len(labels)} features related to {outcome}",
            "xLabel": "Feature",
            "yLabel": f"Correlation with {outcome}",
        },
        "metadata": {
            "correlation_matrix": {
                "labels": matrix_labels,
                "matrix": matrix,
            }
        },
    }

    analysis_context = {
        "kind": "correlation",
        "outcome": outcome,
        "top_correlations": dict(zip(labels, values)),
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


