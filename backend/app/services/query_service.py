"""Query service: analysis planning via playbooks (no SQL generation)."""
import logging
from typing import Dict, Any
from app.core.llm import LLMClient
from app.utils.schema_parser import build_schema_context


class QueryService:
    """Service for planning which analysis playbook to run."""

    def __init__(self):
        self.llm = LLMClient()
        self.logger = logging.getLogger(__name__)

    async def select_analysis(
        self,
        user_query: str,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use the LLM to select an analysis playbook and fill in high-level slots.

        The LLM does NOT write SQL. It only chooses which playbook to use and
        which columns (target/measures) to focus on.
        """
        schema_context = build_schema_context(schema_info)
        lower_query = user_query.lower()

        playbook_descriptions = """
Available playbooks:
- "overview": High-level description of the dataset (size, key numeric features, ranges, missingness).
- "correlation": Identify numeric features most strongly related to a target column.
- "distribution": Explore the distribution and outliers for a single numeric feature.
- "segment_comparison": Compare two cohorts (e.g. outcome=1 vs outcome=0) on a key metric.
- "outcome_breakdown": Show how often each outcome/target class occurs (class balance).
- "feature_outcome_profile": Show how outcome rate changes across the range of a numeric feature.

You can also set numeric detail parameters when relevant:
- "top_n": how many top items to show (e.g. top 10 correlated features).
- "bins": how many bins to use for histograms / profiles (e.g. 20 bins).
"""

        prompt = f"""You are an analysis planner. Your job is to choose ONE analysis playbook
for the user's question, based on the dataset schema.

{playbook_descriptions}

Dataset schema:
{schema_context}

User question: "{user_query}"

Return a JSON object ONLY, with this structure:
{{
  "playbook": "overview" | "correlation" | "distribution" | "segment_comparison" | "outcome_breakdown" | "feature_outcome_profile",
  "target": "column_name or null",              // for correlation, outcome_breakdown & feature_outcome_profile
  "feature": "column_name or null",             // for distribution & feature_outcome_profile (numeric)
  "segment_column": "column_name or null",      // for segment_comparison (categorical/boolean)
  "top_n": number or null,                      // for correlation or any ranking-style output
  "bins": number or null,                       // for distribution / feature_outcome_profile
  "mode": "quick" | "deep"
}}

Rules:
- Use "overview" when the user asks to describe or summarize the dataset or data overall.
- Use "correlation" when the user asks which features/columns are most related to an outcome or target.
- Use "distribution" when the user asks about the spread, range, outliers, or histogram of a single numeric column.
- Use "segment_comparison" when the user asks to compare two groups or cohorts (e.g. outcome=1 vs outcome=0, men vs women).
- Use "outcome_breakdown" when the user asks how often the outcome/target occurs, or for class balance / base rate.
- Use "feature_outcome_profile" when the user asks how the outcome changes as a feature increases/decreases (e.g. outcome vs glucose levels).
- When the user mentions a specific count like "top 3" or "top 10", set "top_n" accordingly (within 3-20).
- When the user asks for more or fewer "buckets" / "ranges" / "granularity", adjust "bins" between 5 and 30.
- For "correlation", choose a numeric column that looks like the outcome/target (e.g., a binary label) if possible.
- Default mode is "quick" unless the user clearly asks for very detailed or deep analysis.
- If you are unsure of a column to use for a given playbook, set its field to null and let the backend fall back safely.
"""

        messages = [
            {
                "role": "system",
                "content": "You are a careful analysis planner. Always return valid JSON and never invent columns that are not in the schema.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await self.llm.generate_json(messages, temperature=0.2)

        # Ensure we got a dictionary back; fall back to a safe default otherwise
        if not isinstance(response, dict):
            self.logger.error(f"select_analysis: LLM returned non-dict: {response!r}")
            return {
                "playbook": "overview",
                "target": None,
                "mode": "quick",
            }

        playbook = response.get("playbook", "overview")
        target = response.get("target")
        feature = response.get("feature")
        segment_column = response.get("segment_column")
        top_n = response.get("top_n")
        bins = response.get("bins")
        mode = response.get("mode", "quick")

        # Basic validation and fallbacks
        allowed_playbooks = {
            "overview",
            "correlation",
            "distribution",
            "segment_comparison",
            "outcome_breakdown",
            "feature_outcome_profile",
        }
        if playbook not in allowed_playbooks:
            playbook = "overview"

        # Heuristic: if correlation or outcome_breakdown was requested but target is missing,
        # try to infer a reasonable default from schema table names / columns.
        if playbook in {"correlation", "outcome_breakdown"} and not target:
            candidate_names = {"outcome", "target", "label", "y"}
            for table in schema_info.get("tables", []):
                for col in table.get("columns", []):
                    if col["name"].lower() in candidate_names:
                        target = col["name"]
                        break
                if target:
                    break

        # Clamp numeric detail parameters to reasonable ranges
        if isinstance(top_n, (int, float)):
            # allow between 3 and 50
            top_n = max(3, min(int(top_n), 50))
        else:
            top_n = None

        if isinstance(bins, (int, float)):
            # allow between 5 and 50
            bins = max(5, min(int(bins), 50))
        else:
            bins = None

        # Final, fully validated analysis request
        return {
            "playbook": playbook,
            "target": target,
            "feature": feature,
            "segment_column": segment_column,
            "top_n": top_n,
            "bins": bins,
            "mode": mode,
        }

