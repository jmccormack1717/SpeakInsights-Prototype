"""Query API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.query_service import QueryService
from app.services.data_analysis_service import DataAnalysisService
from app.services.viz_service import VisualizationService
from app.services.analysis_service import AnalysisService
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
    Execute a natural language query
    
    Flow:
    1. Get schema context
    2. Generate SQL from natural language
    3. Execute SQL query
    4. Analyze data structure
    5. Select visualization
    6. Generate textual analysis
    """
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Get schema
        try:
            schema_info = await db_manager.get_schema(
                request.user_id,
                request.dataset_id
            )
        except Exception as e:
            logger.error(f"Failed to get schema: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{request.dataset_id}' not found. Error: {str(e)}"
            )
        
        if not schema_info.get("tables"):
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{request.dataset_id}' not found or has no tables"
            )
        
        # Step 2: Generate SQL
        try:
            sql_result = await query_service.generate_sql(
                request.query,
                schema_info
            )
            sql = sql_result["sql"]
            intent = sql_result["intent"]
        except Exception as e:
            logger.error(f"Failed to generate SQL: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate SQL query: {str(e)}"
            )
        
        # Step 3: Execute query
        try:
            results = await db_manager.execute_query(
                request.user_id,
                request.dataset_id,
                sql
            )
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute SQL query: {str(e)}"
            )
        
        # Step 4: Analyze data structure
        try:
            data_structure = data_analysis_service.analyze_structure(results)
        except Exception as e:
            logger.error(f"Failed to analyze data structure: {str(e)}")
            data_structure = {}
        
        # Step 5: Select visualization
        try:
            chart_config = viz_service.select_chart_type(intent, data_structure)
            formatted_data = viz_service.format_data_for_chart(results, chart_config)
            
            visualization = {
                "type": chart_config.get("type"),
                "data": formatted_data,
                "config": chart_config.get("config", {}),
                "metadata": {
                    "x_axis": chart_config.get("x_axis"),
                    "y_axis": chart_config.get("y_axis"),
                    "labels": chart_config.get("labels"),
                    "values": chart_config.get("values")
                }
            }
        except Exception as e:
            logger.error(f"Failed to create visualization: {str(e)}")
            # Fallback to table visualization
            visualization = {
                "type": "table",
                "data": {
                    "columns": list(results[0].keys()) if results else [],
                    "rows": results[:100]
                },
                "config": {},
                "metadata": {}
            }
        
        # Step 6: Generate analysis
        try:
            textual_analysis = await analysis_service.generate_insights(
                request.query,
                results,
                sql,
                data_structure
            )
        except Exception as e:
            logger.error(f"Failed to generate analysis: {str(e)}")
            # Fallback analysis
            textual_analysis = {
                "summary": f"Query returned {len(results)} rows.",
                "key_findings": [],
                "patterns": [],
                "recommendations": []
            }
        
        return QueryResponse(
            sql=sql,
            results=results,
            visualization=visualization,
            analysis=textual_analysis,
            data_structure=data_structure
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in query execution: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Query execution failed: {str(e)}"
        )

