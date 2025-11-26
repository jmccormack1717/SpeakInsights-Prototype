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
    extra_visualizations: Optional[List[Dict[str, Any]]] = None
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
        feature = analysis_request.get("feature")
        segment_column = analysis_request.get("segment_column")
        feature_x = analysis_request.get("feature_x")
        feature_y = analysis_request.get("feature_y")
        top_n = analysis_request.get("top_n")
        bins = analysis_request.get("bins")
        filter_segment = analysis_request.get("filter_segment")
        focus_range = analysis_request.get("focus_range")
        secondary_playbooks = analysis_request.get("secondary_playbooks") or []
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

        # Step 5: Build DataFrame and apply any filters from the planner
        df = pd.DataFrame(results)

        # Apply segment filter if provided (equality filter only for now)
        if isinstance(filter_segment, dict):
            col = filter_segment.get("column")
            value = filter_segment.get("value")
            if col in df.columns:
                try:
                    df = df[df[col] == value]
                except Exception:
                    # If filtering fails, keep original df
                    pass

        # Apply focus range for a numeric feature if provided
        if isinstance(focus_range, dict):
            fr_feature = focus_range.get("feature")
            fr_min = focus_range.get("min")
            fr_max = focus_range.get("max")
            if fr_feature in df.columns and isinstance(fr_min, (int, float)) and isinstance(fr_max, (int, float)):
                try:
                    series = pd.to_numeric(df[fr_feature], errors="coerce")
                    mask = series.between(fr_min, fr_max)
                    df = df[mask]
                except Exception:
                    pass

        if playbook_name == "correlation":
            outcome_col = target or "Outcome"
            play = playbooks.correlation_playbook(
                df,
                outcome=outcome_col,
                top_n=top_n or 5,
            )
        elif playbook_name == "distribution":
            feature_col = feature
            # Fallbacks are handled inside the playbook if feature_col is None or invalid
            play = playbooks.distribution_playbook(
                df,
                feature=feature_col,
                bins=bins or 10,
            )
        elif playbook_name == "segmented_distribution":
            play = playbooks.segmented_distribution_playbook(
                df,
                feature=feature,
                segment_column=segment_column,
            )
        elif playbook_name == "segment_comparison":
            seg_col = segment_column
            # Outcome is optional; playbook will fall back to row counts if not usable
            play = playbooks.segment_comparison_playbook(df, segment_column=seg_col, outcome=target)
        elif playbook_name == "outcome_breakdown":
            outcome_col = target or "Outcome"
            play = playbooks.outcome_breakdown_playbook(df, outcome=outcome_col)
        elif playbook_name == "feature_outcome_profile":
            feature_col = feature
            outcome_col = target or "Outcome"
            play = playbooks.feature_outcome_profile_playbook(
                df,
                feature=feature_col,
                outcome=outcome_col,
                bins=bins or 8,
            )
        elif playbook_name == "relationship":
            play = playbooks.relationship_playbook(
                df,
                feature_x=feature_x,
                feature_y=feature_y,
            )
        else:  # default to overview
            play = playbooks.overview_playbook(df)

        visualization = play["visualization"]
        analysis_context = play.get("analysis_context", {})
        merged_structure = {**data_structure, **analysis_context}

        # Step 6: Optionally run secondary playbooks requested by the planner
        extra_visualizations: List[Dict[str, Any]] = []
        for secondary in secondary_playbooks:
            try:
                if secondary == "correlation":
                    outcome_col = target or "Outcome"
                    secondary_play = playbooks.correlation_playbook(
                        df,
                        outcome=outcome_col,
                        top_n=top_n or 5,
                    )
                elif secondary == "distribution":
                    secondary_play = playbooks.distribution_playbook(
                        df,
                        feature=feature,
                        bins=bins or 10,
                    )
                elif secondary == "segment_comparison":
                    secondary_play = playbooks.segment_comparison_playbook(
                        df,
                        segment_column=segment_column,
                        outcome=target,
                    )
                elif secondary == "outcome_breakdown":
                    outcome_col = target or "Outcome"
                    secondary_play = playbooks.outcome_breakdown_playbook(df, outcome=outcome_col)
                elif secondary == "feature_outcome_profile":
                    outcome_col = target or "Outcome"
                    secondary_play = playbooks.feature_outcome_profile_playbook(
                        df,
                        feature=feature,
                        outcome=outcome_col,
                        bins=bins or 8,
                    )
                elif secondary == "relationship":
                    secondary_play = playbooks.relationship_playbook(
                        df,
                        feature_x=feature_x,
                        feature_y=feature_y,
                    )
                elif secondary == "segmented_distribution":
                    secondary_play = playbooks.segmented_distribution_playbook(
                        df,
                        feature=feature,
                        segment_column=segment_column,
                    )
                else:
                    continue

                viz = secondary_play.get("visualization")
                if isinstance(viz, dict):
                    extra_visualizations.append(viz)
            except Exception as e:
                logger.error(f"Secondary playbook '{secondary}' failed: {str(e)}")

        # Step 7: Generate analysis narrative
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
            extra_visualizations=extra_visualizations or None,
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

