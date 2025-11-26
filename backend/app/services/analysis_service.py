"""Analysis service: Generate textual insights"""
from typing import Dict, Any, List
from app.core.llm import LLMClient


class AnalysisService:
    """Service for generating textual analysis and insights"""
    
    def __init__(self):
        self.llm = LLMClient()
    
    async def generate_insights(
        self,
        user_query: str,
        query_results: List[Dict[str, Any]],
        sql: str,
        data_structure: Dict[str, Any],
        visualization: Dict[str, Any],
        extra_visualizations: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """
        Generate textual analysis of query results
        
        Args:
            user_query: Original user query
            query_results: Query results
            sql: Executed SQL query
            data_structure: Data structure analysis
            
        Returns:
            Textual analysis with summary, findings, and insights
        """
        # Prepare results + visualization summary for LLM
        results_summary = self._prepare_results_summary(
            query_results,
            data_structure,
            visualization,
            extra_visualizations or [],
        )
        
        prompt = f"""You are helping a non-technical business user understand their data.
The user will never see any mention of SQL, queries, or technical implementation details.
Speak in clear, friendly business language.

User Question: "{user_query}"

Data + Analysis Summary:
{results_summary}

Please provide a concise, easy-to-understand analysis with:
1. Executive summary (2-3 sentences describing the key findings)
2. Key findings (3-5 bullet points highlighting important patterns or numbers)
3. Notable patterns or anomalies (if any)
4. Recommendations (if applicable, 1-2 actionable insights)
5. 2-4 follow-up questions the user could ask next to go deeper.

Follow-up question rules:
- Each follow-up must be a short, direct question the user can paste back into the assistant.
- Use imperative or direct wording like "Show", "Give me", "Compare", or "Explore" instead of "Would you like".
- Only suggest follow-ups the system can actually handle, for example:
  * "Give me a high-level overview of this dataset, including numeric ranges and missing values."
  * "Show which numeric features are most related to the main outcome or target in this dataset."
  * "Show the distribution of an important numeric feature in this dataset (such as glucose, BMI, or age)."
  * "Compare two important groups in this dataset on a key metric, such as outcome rate or row count."
  * "Show a breakdown of the main outcome or target across the dataset."
- Do not suggest follow-ups that require external data, advanced modeling, or actions outside this dataset.

Formatting rules:
- Do NOT mention SQL, queries, tables, columns, or code.
- When you mention numbers, round them to at most 2 decimal places.
- Prefer percentages and simple ranges over raw long decimals.

Return JSON format only:
{{
  "summary": "Executive summary text",
  "key_findings": ["finding 1", "finding 2", ...],
  "patterns": ["pattern 1", "pattern 2", ...],
  "recommendations": ["recommendation 1", ...],
  "follow_ups": ["follow-up question 1", "follow-up question 2", ...]
}}"""

        messages = [
            {
                "role": "system",
                "content": "You are a data analyst expert. Analyze query results and provide clear, actionable insights. Always return valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = await self.llm.generate_json(messages, temperature=0.5)

            raw_follow_ups = response.get("follow_ups") or []
            follow_ups: List[str] = [
                q for q in raw_follow_ups if isinstance(q, str) and q.strip()
            ]

            if not follow_ups:
                follow_ups = [
                    "Give me a high-level overview of this dataset, including numeric ranges and missing values.",
                    "Show which numeric features are most related to the main outcome or target in this dataset.",
                    "Show the distribution of an important numeric feature in this dataset (for example, glucose, BMI, or age).",
                    "Compare two important groups in this dataset on a key metric, such as outcome rate or row count.",
                ]

            return {
                "summary": response.get("summary", ""),
                "key_findings": response.get("key_findings", []),
                "patterns": response.get("patterns", []),
                "recommendations": response.get("recommendations", []),
                "follow_ups": follow_ups,
            }
        except Exception as e:
            # Fallback to basic analysis if LLM fails
            return self._generate_fallback_analysis(query_results, data_structure)
    
    def _prepare_results_summary(
        self,
        results: List[Dict[str, Any]],
        data_structure: Dict[str, Any],
        visualization: Dict[str, Any],
        extra_visualizations: List[Dict[str, Any]],
    ) -> str:
        """Prepare a summary of results + visualizations for LLM"""
        if not results:
            return "No results returned from query."

        summary_parts: List[str] = [
            f"Total rows: {len(results)}",
            f"Columns: {', '.join(data_structure.get('columns', {}).keys())}",
        ]

        # Describe primary visualization
        v_type = visualization.get("type")
        v_config = visualization.get("config", {}) or {}
        v_title = v_config.get("title")
        v_x = v_config.get("xLabel") or v_config.get("xField")
        v_y = v_config.get("yLabel") or v_config.get("yField")
        summary_parts.append("\nPrimary visualization:")
        summary_parts.append(f"- type: {v_type}, title: {v_title}")
        if v_x or v_y:
            summary_parts.append(f"- axes: x={v_x}, y={v_y}")

        # Mention any extra visualizations
        if extra_visualizations:
            summary_parts.append(f"\nAdditional visualizations ({len(extra_visualizations)}):")
            for extra in extra_visualizations:
                e_type = extra.get("type")
                e_cfg = extra.get("config", {}) or {}
                e_title = e_cfg.get("title")
                summary_parts.append(f"- {e_type}: {e_title}")

        # Add sample data
        summary_parts.append("\nSample data (first 5 rows):")
        for i, row in enumerate(results[:5], 1):
            summary_parts.append(f"Row {i}: {row}")

        # Add statistics for numeric columns
        numeric_cols = data_structure.get("numeric_columns", [])
        for col in numeric_cols:
            stats = data_structure.get("columns", {}).get(col, {}).get("statistics", {})
            if stats:
                summary_parts.append(
                    f"\n{col} statistics: "
                    f"min={stats.get('min')}, max={stats.get('max')}, "
                    f"mean={stats.get('mean'):.2f}, median={stats.get('median'):.2f}"
                )

        # Include playbook-specific analysis context when present
        kind = data_structure.get("kind")
        if kind == "correlation":
            top_corrs = data_structure.get("top_correlations") or {}
            if isinstance(top_corrs, dict) and top_corrs:
                summary_parts.append("\nTop correlations (feature: correlation):")
                for name, val in top_corrs.items():
                    summary_parts.append(f"- {name}: {val}")
        elif kind == "segment_comparison":
            metric = data_structure.get("metric")
            segments = data_structure.get("segments") or []
            values = data_structure.get("values") or []
            effect = data_structure.get("effect_size") or {}
            summary_parts.append(f"\nSegment comparison on metric '{metric}':")
            for seg, val in zip(segments, values):
                summary_parts.append(f"- {seg}: {val}")
            if effect:
                summary_parts.append(f"Effect size (first vs second segment): {effect}")
        elif kind == "feature_outcome_profile":
            feature = data_structure.get("feature")
            outcome = data_structure.get("outcome")
            uplift = data_structure.get("uplift") or {}
            summary_parts.append(f"\nFeature-outcome profile for {feature} vs {outcome}:")
            if uplift:
                summary_parts.append(f"Uplift summary: {uplift}")
        elif kind == "relationship":
            fx = data_structure.get("feature_x")
            fy = data_structure.get("feature_y")
            corr = data_structure.get("correlation")
            pts = data_structure.get("point_count")
            summary_parts.append(f"\nRelationship between {fx} and {fy}: correlation={corr}, points={pts}")
        elif kind == "segmented_distribution":
            feature = data_structure.get("feature")
            seg_col = data_structure.get("segment_column")
            seg_means = data_structure.get("segment_means") or {}
            summary_parts.append(f"\nSegmented distribution of {feature} by {seg_col}:")
            if isinstance(seg_means, dict):
                for seg, val in seg_means.items():
                    summary_parts.append(f"- {seg}: mean={val}")

        return "\n".join(summary_parts)
    
    def _generate_fallback_analysis(
        self,
        results: List[Dict[str, Any]],
        data_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic analysis without LLM"""
        row_count = len(results)
        
        summary = f"Query returned {row_count} result{'s' if row_count != 1 else ''}."
        
        findings = []
        if row_count > 0:
            findings.append(f"Total records: {row_count}")
        
        numeric_cols = data_structure.get("numeric_columns", [])
        for col in numeric_cols:
            stats = data_structure.get("columns", {}).get(col, {}).get("statistics", {})
            if stats:
                findings.append(
                    f"{col} ranges from {stats.get('min')} to {stats.get('max')} "
                    f"(average: {stats.get('mean'):.2f})"
                )
        
        return {
            "summary": summary,
            "key_findings": findings,
            "patterns": [],
            "recommendations": [],
            "follow_ups": [],
        }

