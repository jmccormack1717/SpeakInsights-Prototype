"""Visualization service: Chart type selection and configuration"""
from typing import Dict, Any, List
import pandas as pd


class VisualizationService:
    """Service for selecting and configuring visualizations"""
    
    def select_chart_type(
        self,
        intent: Dict[str, Any],
        data_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select optimal chart type based on intent and data structure
        
        Args:
            intent: Query intent from LLM
            data_structure: Data structure analysis
            
        Returns:
            Chart configuration
        """
        primary_intent = intent.get("primary_intent", "comparison")
        explicit_chart = intent.get("explicit_chart_type")

        # Normalize and validate explicit chart type
        allowed_chart_types = {
            "bar",
            "horizontal_bar",
            "line",
            "pie",
            "scatter",
            "histogram",
            "correlation_matrix",
            "table",
        }

        if isinstance(explicit_chart, str):
            explicit_chart = explicit_chart.lower().strip()
            if explicit_chart not in allowed_chart_types:
                explicit_chart = None
        else:
            explicit_chart = None

        # If user explicitly requested a supported chart type, use it
        if explicit_chart:
            return self._create_chart_config(
                explicit_chart,
                intent,
                data_structure
            )
        
        # Rule 1: Time series
        if (data_structure.get("has_time_series") and 
            primary_intent in ["trend", "trend_comparison"]):
            datetime_col = data_structure.get("datetime_columns", [None])[0]
            numeric_col = data_structure.get("numeric_columns", [None])[0]
            
            if datetime_col and numeric_col:
                return {
                    "type": "line",
                    "x_axis": datetime_col,
                    "y_axis": numeric_col,
                    "config": {
                        "title": f"{numeric_col} Over Time",
                        "xLabel": datetime_col,
                        "yLabel": numeric_col
                    }
                }
        
        # Rule 2: Comparison with categories
        if primary_intent in ["comparison", "trend_comparison"]:
            categorical_cols = data_structure.get("categorical_columns", [])
            numeric_cols = data_structure.get("numeric_columns", [])
            
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                cardinality = data_structure.get("cardinality", {}).get(cat_col, 0)
                
                if cardinality <= 5:
                    return {
                        "type": "bar",
                        "x_axis": cat_col,
                        "y_axis": num_col,
                        "config": {
                            "title": f"{num_col} by {cat_col}",
                            "xLabel": cat_col,
                            "yLabel": num_col,
                            "sort": "descending"
                        }
                    }
                elif cardinality <= 20:
                    return {
                        "type": "horizontal_bar",
                        "x_axis": cat_col,
                        "y_axis": num_col,
                        "config": {
                            "title": f"{num_col} by {cat_col}",
                            "xLabel": cat_col,
                            "yLabel": num_col,
                            "sort": "descending"
                        }
                    }
        
        # Rule 3: Distribution
        if primary_intent == "distribution":
            numeric_cols = data_structure.get("numeric_columns", [])
            if numeric_cols:
                return {
                    "type": "histogram",
                    "x_axis": numeric_cols[0],
                    "config": {
                        "title": f"Distribution of {numeric_cols[0]}",
                        "xLabel": numeric_cols[0],
                        "bins": self._calculate_bins(
                            data_structure.get("row_count", 0)
                        )
                    }
                }
        
        # Rule 4: Correlation
        if primary_intent == "correlation":
            numeric_cols = data_structure.get("numeric_columns", [])
            if len(numeric_cols) >= 2:
                return {
                    "type": "correlation_matrix",
                    "config": {
                        "title": "Feature Correlations"
                    }
                }
        
        # Rule 5: Part-to-whole
        if primary_intent == "part_to_whole":
            categorical_cols = data_structure.get("categorical_columns", [])
            numeric_cols = data_structure.get("numeric_columns", [])
            
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                cardinality = data_structure.get("cardinality", {}).get(cat_col, 0)
                
                if cardinality <= 10:
                    return {
                        "type": "pie",
                        "labels": cat_col,
                        "values": numeric_cols[0],
                        "config": {
                            "title": f"{numeric_cols[0]} by {cat_col}"
                        }
                    }
        
        # Rule 6: Default - Bar chart if we have categorical + numeric
        categorical_cols = data_structure.get("categorical_columns", [])
        numeric_cols = data_structure.get("numeric_columns", [])
        
        if categorical_cols and numeric_cols:
            return {
                "type": "bar",
                "x_axis": categorical_cols[0],
                "y_axis": numeric_cols[0],
                "config": {
                    "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                    "xLabel": categorical_cols[0],
                    "yLabel": numeric_cols[0]
                }
            }
        
        # Ultimate fallback: Table
        return {
            "type": "table",
            "config": {
                "title": "Query Results"
            }
        }
    
    def format_data_for_chart(
        self,
        results: List[Dict[str, Any]],
        chart_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format query results for chart library
        
        Args:
            results: Query results
            chart_config: Chart configuration
            
        Returns:
            Formatted data for chart
        """
        chart_type = chart_config.get("type")
        
        if chart_type == "bar" or chart_type == "horizontal_bar":
            x_axis = chart_config.get("x_axis")
            y_axis = chart_config.get("y_axis")
            
            return {
                "labels": [row.get(x_axis) for row in results],
                "values": [row.get(y_axis) for row in results]
            }
        
        elif chart_type == "line":
            x_axis = chart_config.get("x_axis")
            y_axis = chart_config.get("y_axis")
            
            return {
                "x": [row.get(x_axis) for row in results],
                "y": [row.get(y_axis) for row in results]
            }
        
        elif chart_type == "pie":
            labels_col = chart_config.get("labels")
            values_col = chart_config.get("values")
            
            return {
                "labels": [row.get(labels_col) for row in results],
                "values": [row.get(values_col) for row in results]
            }
        
        elif chart_type == "scatter":
            x_axis = chart_config.get("x_axis")
            y_axis = chart_config.get("y_axis")
            
            return {
                "x": [row.get(x_axis) for row in results],
                "y": [row.get(y_axis) for row in results]
            }
        
        elif chart_type == "histogram":
            x_axis = chart_config.get("x_axis")
            values = [row.get(x_axis) for row in results if row.get(x_axis) is not None]
            return {
                "values": values,
                "bins": chart_config.get("config", {}).get("bins", 10)
            }

        elif chart_type == "correlation_matrix":
            # Build correlation matrix from numeric columns in the results
            df = pd.DataFrame(results)
            if df.empty:
                return {"labels": [], "matrix": []}

            num_df = df.select_dtypes(include="number")
            if num_df.shape[1] < 2:
                return {"labels": list(num_df.columns), "matrix": []}

            corr = num_df.corr().fillna(0.0)
            labels = list(corr.columns)
            matrix = corr.values.tolist()
            return {
                "labels": labels,
                "matrix": matrix,
            }

        else:  # table
            return {
                "columns": list(results[0].keys()) if results else [],
                "rows": results
            }
    
    def _create_chart_config(
        self,
        chart_type: str,
        intent: Dict[str, Any],
        data_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create chart config for explicit chart type"""
        # Try to infer axes from data structure
        categorical_cols = data_structure.get("categorical_columns", [])
        numeric_cols = data_structure.get("numeric_columns", [])
        datetime_cols = data_structure.get("datetime_columns", [])
        
        config = {"type": chart_type}
        
        if chart_type in ["bar", "horizontal_bar", "line"]:
            if datetime_cols and numeric_cols:
                config["x_axis"] = datetime_cols[0]
                config["y_axis"] = numeric_cols[0]
            elif categorical_cols and numeric_cols:
                config["x_axis"] = categorical_cols[0]
                config["y_axis"] = numeric_cols[0]
        
        elif chart_type == "pie":
            if categorical_cols and numeric_cols:
                config["labels"] = categorical_cols[0]
                config["values"] = numeric_cols[0]
        
        elif chart_type == "scatter":
            if len(numeric_cols) >= 2:
                config["x_axis"] = numeric_cols[0]
                config["y_axis"] = numeric_cols[1]

        elif chart_type == "correlation_matrix":
            # Title for correlation matrix views
            config["title"] = intent.get("title") or "Correlation Matrix"
        
        return config
    
    def _calculate_bins(self, row_count: int) -> int:
        """Calculate optimal number of bins for histogram"""
        if row_count < 10:
            return 5
        elif row_count < 100:
            return 10
        elif row_count < 1000:
            return 20
        else:
            return 30

