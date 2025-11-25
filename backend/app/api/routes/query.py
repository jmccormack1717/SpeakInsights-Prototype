"""Query API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.query_service import QueryService
from app.services.data_analysis_service import DataAnalysisService
from app.services.viz_service import VisualizationService
from app.services.analysis_service import AnalysisService
from app.services import playbooks
import pandas as pd
from app.core.database import db_manager


router = APIRouter()

query_service = QueryService()
data_analysis_service = DataAnalysisService()
viz_service = VisualizationService()
analysis_service = AnalysisService()


class QueryRequest(BaseModel):
    """Query request model"""
    user_id: str
    dataset_id: str
    query: str


class QueryResponse(BaseModel):
    """Query response model"""
    sql: str
    results: List[Dict[str, Any]]
    visualization: Dict[str, Any]
    analysis: Dict[str, Any]
    data_structure: Dict[str, Any]


@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute a natural language query using analysis playbooks.

    Flow:
    1. Get schema context
    2. Use LLM to choose an analysis playbook (no SQL generation)
    3. Execute fixed SQL to fetch data
    4. Run the playbook to produce visualization + context
    5. Generate textual analysis
    """
    import traceback
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Step 1: Get schema
        try:
            schema_info = await db_manager.get_schema(
                request.user_id,
                request.dataset_id,
            )
        except Exception as e:
            logger.error(f"Failed to get schema: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{request.dataset_id}' not found. Error: {str(e)}",
            )

        tables = schema_info.get("tables", [])
        if not tables:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{request.dataset_id}' not found or has no tables",
            )

        main_table = tables[0]["name"]

        # Step 2: Use LLM to select analysis playbook (no SQL)
        try:
            analysis_request = await query_service.select_analysis(
                request.query, schema_info
            )
        except Exception as e:
            logger.error(f"Failed to select analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to plan analysis: {str(e)}",
            )

        # Extra safety: ensure we have a dict to avoid NoneType errors
        if not isinstance(analysis_request, dict):
            logger.error(f"select_analysis returned invalid value: {analysis_request!r}")
            raise HTTPException(
                status_code=500,
                detail="Failed to plan analysis: invalid planner response",
            )

        playbook_name = analysis_request.get("playbook", "overview")
        target = analysis_request.get("target")
        mode = analysis_request.get("mode", "quick")

        # Step 3: Execute fixed SQL (no LLM-generated SQL)
        if playbook_name == "overview":
            sql = f"SELECT * FROM {main_table} LIMIT 500"
        else:
            sql = f"SELECT * FROM {main_table}"

        try:
            results = await db_manager.execute_query(
                request.user_id,
                request.dataset_id,
                sql,
            )
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            logger.error(f"SQL that failed: {sql}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute data fetch: {str(e)}",
            )

        # Step 4: Analyze data structure (generic)
        try:
            data_structure = data_analysis_service.analyze_structure(results)
        except Exception as e:
            logger.error(f"Failed to analyze data structure: {str(e)}")
            data_structure = {}

        # Step 5: Run the selected playbook
        df = pd.DataFrame(results)

        if playbook_name == "correlation":
            outcome_col = target or "Outcome"
            play = playbooks.correlation_playbook(df, outcome=outcome_col)
        else:  # default to overview
            play = playbooks.overview_playbook(df)

        visualization = play["visualization"]
        analysis_context = play.get("analysis_context", {})
        merged_structure = {**data_structure, **analysis_context}

        # Step 6: Generate analysis narrative
        try:
            textual_analysis = await analysis_service.generate_insights(
                request.query,
                results,
                sql,
                merged_structure,
            )
        except Exception as e:
            logger.error(f"Failed to generate analysis: {str(e)}")
            textual_analysis = {
                "summary": f"Analysis completed using playbook '{playbook_name}'.",
                "key_findings": [],
                "patterns": [],
                "recommendations": [],
            }

        return QueryResponse(
            sql=sql,
            results=results,
            visualization=visualization,
            analysis=textual_analysis,
            data_structure=merged_structure,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query execution: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}",
        )

