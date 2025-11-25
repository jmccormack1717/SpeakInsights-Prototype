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
"""

        prompt = f"""You are an analysis planner. Your job is to choose ONE analysis playbook
for the user's question, based on the dataset schema.

{playbook_descriptions}

Dataset schema:
{schema_context}

User question: "{user_query}"

Return a JSON object ONLY, with this structure:
{{
  "playbook": "overview" | "correlation",
  "target": "column_name or null",
  "mode": "quick" | "deep"
}}

Rules:
- Use "overview" when the user asks to describe or summarize the dataset or data overall.
- Use "correlation" when the user asks which features/columns are most related to an outcome or target.
- For "correlation", choose a numeric column that looks like the outcome/target (e.g., a binary label) if possible.
- If you are unsure of the target for "correlation", set "target" to null.
- Default mode is "quick" unless the user clearly asks for very detailed or deep analysis.
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

        playbook = response.get("playbook", "overview")
        target = response.get("target")
        mode = response.get("mode", "quick")

        # Basic validation and fallbacks
        if playbook not in {"overview", "correlation"}:
            playbook = "overview"

        # Heuristic: if correlation was requested but target is missing,
        # try to infer a reasonable default from schema table names / columns.
        if playbook == "correlation" and not target:
            # Look for obvious outcome/target-like columns
            candidate_names = {"outcome", "target", "label", "y"}
            for table in schema_info.get("tables", []):
                for col in table.get("columns", []):
                    if col["name"].lower() in candidate_names:
                        target = col["name"]
                        break
                if target:
                    break

