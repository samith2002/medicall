import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

# Import routes
from routes.call_routes import router as call_router
from routes.model_routes import router as model_router
from routes.webhook_routes import router as webhook_router
from routes.websocket_routes import router as websocket_router

# Import configuration
from config import SERVER_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Call Assistant",
    description="An AI-powered call assistant that transcribes and processes calls using Groq. Supports live audio transcription and real-time responses.",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        os.getenv("FRONTEND_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(call_router)
app.include_router(model_router)
app.include_router(webhook_router)
app.include_router(websocket_router)

@app.get("/", tags=["health"])
async def root(request: Request):
    """Root endpoint - redirects to Swagger UI docs"""
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AI Call Assistant API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/openapi.json", tags=["documentation"])
async def get_openapi_schema():
    """Generate OpenAPI schema"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return openapi_schema

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    uvicorn.run(
        "main:app", 
        host=SERVER_CONFIG["host"], 
        port=int(os.getenv("PORT", SERVER_CONFIG["port"])), 
        reload=SERVER_CONFIG["reload"]
    )
