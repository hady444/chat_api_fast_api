# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from app.core.config import settings
# from app.db.mongodb import connect_to_mongo, close_mongo_connection
# from app.db.redis import redis_client
# from app.api.endpoints import chat, health

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await connect_to_mongo()
#     await redis_client.connect()
#     yield
#     # Shutdown
#     await close_mongo_connection()
#     await redis_client.disconnect()

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.VERSION,
#     lifespan=lifespan
# )

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(
#     chat.router,
#     prefix="/chat",
#     tags=["chat"]
# )

# app.include_router(
#     health.router,
#     prefix="/api",
#     tags=["health"]
# )

# @app.get("/")
# async def root():
#     return {
#         "message": "Chat Microservice API",
#         "version": settings.VERSION,
#         "docs": "/docs"
#     }


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from app.core.config import settings
# from app.db.mongodb import connect_to_mongo, close_mongo_connection
# from app.db.redis import redis_client
# from app.api.endpoints import chat, health, auth  # Add auth import

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await connect_to_mongo()
#     await redis_client.connect()
#     yield
#     # Shutdown
#     await close_mongo_connection()
#     await redis_client.disconnect()

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.VERSION,
#     lifespan=lifespan
# )

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}



# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(
#     chat.router,
#     prefix="/chat",
#     tags=["chat"]
# )

# app.include_router(
#     health.router,
#     prefix="/api",
#     tags=["health"]
# )

# # Add auth router for development
# if settings.DEBUG:
#     app.include_router(
#         auth.router,
#         prefix="/auth",
#         tags=["auth"]
#     )

# @app.get("/")
# async def root():
#     return {
#         "message": "Chat Microservice API",
#         "version": settings.VERSION,
#         "docs": "/docs",
#         "debug_mode": settings.DEBUG
#     }


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import redis_client
from app.api.endpoints import chat, health

# Create auth router only if auth.py exists
try:
    from app.api.endpoints import auth
    auth_available = True
except ImportError:
    auth_available = False
    logger.warning("Auth module not found")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        # Try to connect to MongoDB
        await connect_to_mongo()
        logger.info("MongoDB connected")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
    
    try:
        # Try to connect to Redis
        await redis_client.connect()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    try:
        await close_mongo_connection()
    except:
        pass
    try:
        await redis_client.disconnect()
    except:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) if settings.DEBUG else "Internal server error"}
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

app.include_router(
    health.router,
    prefix="/api",
    tags=["health"]
)

# Add auth router for development if available
if settings.DEBUG and auth_available:
    app.include_router(
        auth.router,
        prefix="/auth",
        tags=["auth"]
    )

@app.get("/")
async def root():
    return {
        "message": "Chat Microservice API",
        "version": settings.VERSION,
        "docs": "/docs",
        "debug_mode": settings.DEBUG,
        "auth_endpoints": auth_available
    }

@app.get("/ping")
async def ping():
    return {"ping": "pong"}