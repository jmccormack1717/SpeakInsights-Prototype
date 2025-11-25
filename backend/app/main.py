"""FastAPI application entry point"""
import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.api.routes import query, datasets, schema
from app.core.database import db_manager
from app.utils.csv_importer import CSVImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SpeakInsights API",
    description="Prompt-driven data analytics platform",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware - MUST be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(datasets.router, prefix="/api/v1", tags=["datasets"])
app.include_router(schema.router, prefix="/api/v1", tags=["schema"])


# Exception handlers to ensure CORS headers are always included
def get_cors_headers(request: Request) -> dict:
    """Get CORS headers based on request origin"""
    origin = request.headers.get("origin")
    # Check if origin is in allowed origins
    if origin and origin in settings.cors_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    # Fallback to first allowed origin if origin doesn't match
    elif settings.cors_origins:
        return {
            "Access-Control-Allow-Origin": settings.cors_origins[0] if isinstance(settings.cors_origins, list) else str(settings.cors_origins).split(",")[0].strip(),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=get_cors_headers(request)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers=get_cors_headers(request)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with CORS headers"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers=get_cors_headers(request)
    )


@app.on_event("startup")
async def startup_event():
    """Initialize MVP dataset on startup if it doesn't exist"""
    # Log CORS configuration
    logger.info(f"CORS allowed origins: {settings.cors_origins}")
    
    user_id = "default_user"
    dataset_id = "mvp_dataset"
    db_path = db_manager.get_database_path(user_id, dataset_id)
    
    # Check if database exists
    if not db_path.exists():
        logger.info(f"MVP dataset not found at {db_path}. Attempting to import...")
        
        # Look for CSV file in common locations (relative to backend directory)
        backend_dir = Path(__file__).parent.parent
        # Prefer cleaned dataset for MVP
        csv_paths = [
            backend_dir / "cleaned_diabetes_dataset.csv",  # In backend directory
            backend_dir.parent / "cleaned_diabetes_dataset.csv",  # In project root
            backend_dir / "data" / "cleaned_diabetes_dataset.csv",  # In backend/data
        ]
        
        csv_file = None
        for path in csv_paths:
            if path.exists():
                csv_file = path
                break
        
        if csv_file:
            try:
                logger.info(f"Found CSV file at {csv_file}. Importing...")
                await db_manager.create_database(user_id, dataset_id)
                engine = await db_manager.get_engine(user_id, dataset_id)
                
                with open(csv_file, 'rb') as f:
                    csv_content = f.read()
                
                result = await CSVImporter.import_csv(
                    engine,
                    csv_content,
                    table_name="diabetes",
                    encoding='utf-8'
                )
                
                logger.info(
                    f"Successfully imported MVP dataset: "
                    f"{result['rows_imported']} rows into table '{result['table_name']}'"
                )
                await engine.dispose()
            except Exception as e:
                logger.error(f"Failed to import MVP dataset: {str(e)}")
                logger.exception(e)
        else:
            logger.warning(
                "CSV file not found. Please ensure 'cleaned_diabetes_dataset.csv' is available "
                "in the backend directory, project root, or backend/data. "
                "Database will be created when first query is made or CSV is uploaded."
            )
    else:
        logger.info(f"MVP dataset found at {db_path}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "SpeakInsights API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

