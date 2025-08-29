from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import logging

# Import our modules
from app.database import init_database
from app.config import config
from app.api import tasks, logs, admin
from app.scheduler import task_scheduler
from app.task_executor import task_executor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="CronPilot",
    description="A comprehensive task scheduling and management system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("tasks", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # Initialize database
        init_database()
        logging.info("Database initialized successfully")
        
        # Discover and register tasks if auto-discover is enabled
        if config.auto_discover_tasks:
            from app.database import SessionLocal
            db = SessionLocal()
            try:
                discovered_tasks = task_executor.discover_tasks(config.tasks_directory)
                existing_tasks = db.query(tasks.Task).all()
                existing_names = {task.name for task in existing_tasks}
                
                for task_info in discovered_tasks:
                    if task_info['name'] not in existing_names:
                        # Auto-register new tasks
                        from app.models.models import Task, ScheduleType
                        new_task = Task(
                            name=task_info['name'],
                            file_path=task_info['file_path'],
                            module_name=task_info['module_name'],
                            description=task_info.get('description', ''),
                            schedule_type=ScheduleType.MANUAL.value,
                            is_active=True
                        )
                        db.add(new_task)
                        logging.info(f"Auto-registered task: {task_info['name']}")
                
                db.commit()
                
            except Exception as e:
                logging.error(f"Error during task auto-discovery: {e}")
            finally:
                db.close()
        
        logging.info("CronPilot application started successfully")
        
    except Exception as e:
        logging.error(f"Error during application startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    try:
        task_scheduler.shutdown()
        logging.info("CronPilot application shutdown successfully")
    except Exception as e:
        logging.error(f"Error during application shutdown: {e}")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - redirect to admin dashboard"""
    return RedirectResponse(url="/admin")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.server_host,
        port=config.server_port,
        reload=True
    ) 