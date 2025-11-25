"""Analysis playbooks for common question types."""
from typing import Dict, Any, List, Optional
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


def distribution_playbook(
    df: pd.DataFrame,
    feature: Optional[str] = None,
    bins: int = 10,
) -> Dict[str, Any]:
    """
    Explore the distribution of a single numeric feature with a histogram.
    """
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No numeric columns available for distribution"},
            },
            "analysis_context": {"kind": "distribution", "reason": "no_numeric_columns"},
        }

    # Fallback feature if none provided
    if not feature or feature not in numeric_df.columns:
        # Prefer columns with common names like age, score, amount, etc.
        preferred = {"age", "score", "amount", "value", "glucose", "bmi"}
        pick = None
        for col in numeric_df.columns:
            if col.lower() in preferred:
                pick = col
                break
        feature = pick or numeric_df.columns[0]

    series = pd.to_numeric(numeric_df[feature], errors="coerce").dropna()
    if series.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [feature], "rows": []},
                "config": {"title": f"No valid values for {feature}"},
            },
            "analysis_context": {
                "kind": "distribution",
                "feature": feature,
                "reason": "no_valid_values",
            },
        }

    counts, bin_edges = np.histogram(series, bins=bins)
    labels: List[str] = []
    for i in range(len(bin_edges) - 1):
        left = round(float(bin_edges[i]), 2)
        right = round(float(bin_edges[i + 1]), 2)
        labels.append(f"{left}–{right}")

    values = [int(c) for c in counts]

    visualization = {
        "type": "bar",  # Use bar chart to represent histogram bins
        "data": {
            "labels": labels,
            "values": values,
        },
        "config": {
            "title": f"Distribution of {feature}",
            "xLabel": feature,
            "yLabel": "Count of rows",
        },
    }

    analysis_context = {
        "kind": "distribution",
        "feature": feature,
        "row_count": int(series.shape[0]),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


def outcome_breakdown_playbook(
    df: pd.DataFrame,
    outcome: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Show class balance / outcome distribution as a simple bar or pie chart.
    """
    # Try to infer an outcome column if not provided
    if not outcome or outcome not in df.columns:
        candidate_names = {"outcome", "target", "label", "y"}
        for col in df.columns:
            if col.lower() in candidate_names:
                outcome = col
                break

    if not outcome or outcome not in df.columns:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No outcome/target column found for breakdown"},
            },
            "analysis_context": {"kind": "outcome_breakdown", "reason": "no_outcome"},
        }

    series = df[outcome].astype("category")
    counts = series.value_counts().sort_index()
    total = counts.sum()

    labels = [str(idx) for idx in counts.index.tolist()]
    values = [int(v) for v in counts.values.tolist()]

    visualization = {
        "type": "pie",
        "data": {
            "labels": labels,
            "values": values,
        },
        "config": {
            "title": f"Outcome breakdown for {outcome}",
        },
    }

    percentages = {
        str(idx): round(float(v) * 100.0 / float(total), 1) if total else 0.0
        for idx, v in zip(counts.index.tolist(), counts.values.tolist())
    }

    analysis_context = {
        "kind": "outcome_breakdown",
        "outcome": outcome,
        "counts": dict(zip(labels, values)),
        "percentages": percentages,
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


def segment_comparison_playbook(
    df: pd.DataFrame,
    segment_column: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compare two cohorts on a key metric (ideally the outcome rate).

    - If outcome is provided and numeric/binary, compare mean outcome per segment.
    - Otherwise, compare row counts per segment.
    """
    if segment_column is None or segment_column not in df.columns:
        # Fallback: pick first low-cardinality categorical-like column
        for col in df.columns:
            unique_vals = df[col].nunique(dropna=True)
            if 2 <= unique_vals <= 6:
                segment_column = col
                break

    if segment_column is None or segment_column not in df.columns:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No suitable segment column found to compare cohorts"},
            },
            "analysis_context": {
                "kind": "segment_comparison",
                "reason": "no_segment_column",
            },
        }

    # Limit to top 2 most common segments for clarity
    counts = df[segment_column].value_counts().head(2)
    if counts.shape[0] < 2:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [segment_column], "rows": []},
                "config": {"title": "Not enough segments to compare"},
            },
            "analysis_context": {
                "kind": "segment_comparison",
                "segment_column": segment_column,
                "reason": "single_segment_only",
            },
        }

    segments = counts.index.tolist()

    # Decide metric: outcome rate if possible, else row count
    metric_name = "Row count"
    segment_values: List[float]

    if outcome and outcome in df.columns and pd.api.types.is_numeric_dtype(df[outcome]):
        metric_name = f"Average {outcome}"
        means = []
        for seg in segments:
            seg_df = df[df[segment_column] == seg]
            if seg_df.empty:
                means.append(0.0)
            else:
                means.append(round(float(seg_df[outcome].mean()), 3))
        segment_values = means
    else:
        segment_values = [int(v) for v in counts.values.tolist()]

    labels = [str(s) for s in segments]

    visualization = {
        "type": "bar",
        "data": {
            "labels": labels,
            "values": segment_values,
        },
        "config": {
            "title": f"{metric_name} by {segment_column}",
            "xLabel": segment_column,
            "yLabel": metric_name,
        },
    }

    analysis_context = {
        "kind": "segment_comparison",
        "segment_column": segment_column,
        "segments": labels,
        "metric": metric_name,
        "values": segment_values,
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


