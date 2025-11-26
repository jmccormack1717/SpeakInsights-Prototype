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
            "mark": "bar",
            "xField": "Feature",
            "yField": "Correlation",
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
        "type": "histogram",  # Use bar chart to represent histogram bins
        "data": {
            "labels": labels,
            "values": values,
        },
        "config": {
            "title": f"Distribution of {feature}",
            "xLabel": feature,
            "yLabel": "Count of rows",
            "mark": "bar",
            "bins": bins,
            "xField": feature,
            "yField": "count",
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


def feature_outcome_profile_playbook(
    df: pd.DataFrame,
    feature: Optional[str] = None,
    outcome: Optional[str] = None,
    bins: int = 8,
) -> Dict[str, Any]:
    """
    Profile how outcome rate changes across the range of a numeric feature.

    - Bin the feature into quantiles.
    - Compute average outcome in each bin.
    - Return a line chart of outcome rate by feature bin.
    """
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No numeric columns available for feature profile"},
            },
            "analysis_context": {"kind": "feature_outcome_profile", "reason": "no_numeric_columns"},
        }

    # Infer feature if needed
    if not feature or feature not in num_df.columns:
        preferred = {"age", "glucose", "bmi", "insulin"}
        pick = None
        for col in num_df.columns:
            if col.lower() in preferred:
                pick = col
                break
        feature = pick or num_df.columns[0]

    # Infer outcome if needed
    if not outcome or outcome not in df.columns:
        candidate_names = {"outcome", "target", "label", "y"}
        for col in df.columns:
            if col.lower() in candidate_names:
                outcome = col
                break

    if not outcome or outcome not in df.columns or not pd.api.types.is_numeric_dtype(df[outcome]):
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [feature], "rows": []},
                "config": {"title": f"Cannot profile {feature}: no numeric outcome found"},
            },
            "analysis_context": {
                "kind": "feature_outcome_profile",
                "feature": feature,
                "reason": "no_numeric_outcome",
            },
        }

    feature_series = pd.to_numeric(df[feature], errors="coerce")
    outcome_series = pd.to_numeric(df[outcome], errors="coerce")
    mask = feature_series.notna() & outcome_series.notna()
    feature_series = feature_series[mask]
    outcome_series = outcome_series[mask]

    if feature_series.empty or outcome_series.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [feature], "rows": []},
                "config": {"title": f"No valid data to profile {feature} against {outcome}"},
            },
            "analysis_context": {
                "kind": "feature_outcome_profile",
                "feature": feature,
                "outcome": outcome,
                "reason": "no_valid_values",
            },
        }

    try:
        quantiles = pd.qcut(feature_series, q=bins, duplicates="drop")
    except ValueError:
        # Not enough unique values for quantile bins
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [feature], "rows": []},
                "config": {"title": f"Not enough variation in {feature} to build a profile"},
            },
            "analysis_context": {
                "kind": "feature_outcome_profile",
                "feature": feature,
                "outcome": outcome,
                "reason": "low_variation",
            },
        }

    grouped = outcome_series.groupby(quantiles).mean()
    labels: List[str] = []
    values: List[float] = []
    for interval, mean_val in grouped.items():
        if pd.isna(mean_val):
            continue
        left = round(float(interval.left), 2)
        right = round(float(interval.right), 2)
        labels.append(f"{left}–{right}")
        values.append(round(float(mean_val), 3))

    visualization = {
        "type": "line",
        "data": {
            "x": labels,
            "y": values,
        },
        "config": {
            "title": f"Outcome rate by {feature} range",
            "xLabel": f"{feature} range",
            "yLabel": f"Average {outcome}",
            "mark": "line",
            "xField": f"{feature}_binned",
            "yField": f"avg_{outcome}",
        },
    }

    analysis_context = {
        "kind": "feature_outcome_profile",
        "feature": feature,
        "outcome": outcome,
        "bins": labels,
        "values": values,
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


def relationship_playbook(
    df: pd.DataFrame,
    feature_x: Optional[str] = None,
    feature_y: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Show the relationship between two numeric features using a scatter plot.
    """
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] < 2:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": num_df.columns.tolist(), "rows": []},
                "config": {"title": "Not enough numeric columns to show a relationship"},
            },
            "analysis_context": {"kind": "relationship", "reason": "insufficient_numeric_columns"},
        }

    # Fallback inference if features are not provided or invalid
    candidates = list(num_df.columns)
    if not feature_x or feature_x not in candidates:
        feature_x = candidates[0]
    if not feature_y or feature_y not in candidates or feature_y == feature_x:
        feature_y = candidates[1] if len(candidates) > 1 else candidates[0]

    x_series = pd.to_numeric(df[feature_x], errors="coerce")
    y_series = pd.to_numeric(df[feature_y], errors="coerce")
    mask = x_series.notna() & y_series.notna()
    x_values = x_series[mask].tolist()
    y_values = y_series[mask].tolist()

    if len(x_values) < 5:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [feature_x, feature_y], "rows": []},
                "config": {"title": "Not enough valid data points to show a relationship"},
            },
            "analysis_context": {
                "kind": "relationship",
                "feature_x": feature_x,
                "feature_y": feature_y,
                "reason": "too_few_points",
            },
        }

    # Simple Pearson correlation as a numeric summary
    try:
        corr = float(pd.Series(x_values).corr(pd.Series(y_values)))
    except Exception:
        corr = None

    visualization = {
        "type": "scatter",
        "data": {
            "x": x_values,
            "y": y_values,
        },
        "config": {
            "title": f"{feature_y} vs {feature_x}",
            "xLabel": feature_x,
            "yLabel": feature_y,
            "mark": "point",
            "xField": feature_x,
            "yField": feature_y,
        },
    }

    analysis_context = {
        "kind": "relationship",
        "feature_x": feature_x,
        "feature_y": feature_y,
        "correlation": round(corr, 3) if corr is not None else None,
        "point_count": len(x_values),
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }


def segmented_distribution_playbook(
    df: pd.DataFrame,
    feature: Optional[str] = None,
    segment_column: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Show how the distribution/average of a numeric feature differs across segments.

    For now this returns a bar chart of the mean feature value per segment, and
    includes basic distribution summaries in the analysis context.
    """
    if df.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No data available for segmented distribution"},
            },
            "analysis_context": {"kind": "segmented_distribution", "reason": "empty_dataframe"},
        }

    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [], "rows": []},
                "config": {"title": "No numeric columns available for segmented distribution"},
            },
            "analysis_context": {"kind": "segmented_distribution", "reason": "no_numeric_columns"},
        }

    # Infer feature if needed
    if not feature or feature not in num_df.columns:
        preferred = {"age", "glucose", "bmi", "insulin"}
        pick = None
        for col in num_df.columns:
            if col.lower() in preferred:
                pick = col
                break
        feature = pick or num_df.columns[0]

    # Infer segment column if needed
    if segment_column is None or segment_column not in df.columns:
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
                "config": {"title": "No suitable segment column found for segmented distribution"},
            },
            "analysis_context": {
                "kind": "segmented_distribution",
                "feature": feature,
                "reason": "no_segment_column",
            },
        }

    grouped = df.groupby(segment_column)[feature]
    means = grouped.mean().dropna()
    if means.empty:
        return {
            "visualization": {
                "type": "table",
                "data": {"columns": [segment_column, feature], "rows": []},
                "config": {"title": f"No valid {feature} values for segmented distribution"},
            },
            "analysis_context": {
                "kind": "segmented_distribution",
                "feature": feature,
                "segment_column": segment_column,
                "reason": "no_valid_values",
            },
        }

    labels = [str(idx) for idx in means.index.tolist()]
    values = [round(float(v), 2) for v in means.values.tolist()]

    visualization = {
        "type": "bar",
        "data": {
            "labels": labels,
            "values": values,
        },
        "config": {
            "title": f"Average {feature} by {segment_column}",
            "xLabel": segment_column,
            "yLabel": f"Average {feature}",
            "mark": "bar",
            "xField": segment_column,
            "yField": f"avg_{feature}",
        },
    }

    # Basic per-segment summary stats
    summaries: List[Dict[str, Any]] = []
    for seg, series in grouped:
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty:
            continue
        summaries.append(
            {
                "segment": str(seg),
                "count": int(s.shape[0]),
                "mean": round(float(s.mean()), 2),
                "median": round(float(s.median()), 2),
                "min": round(float(s.min()), 2),
                "max": round(float(s.max()), 2),
            }
        )

    analysis_context = {
        "kind": "segmented_distribution",
        "feature": feature,
        "segment_column": segment_column,
        "segments": labels,
        "segment_means": dict(zip(labels, values)),
        "segment_summaries": summaries,
    }

    return {
        "visualization": visualization,
        "analysis_context": analysis_context,
    }

