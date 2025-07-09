import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
from app.core.database import create_db_and_tables
from app.core.middleware import LogRequestMiddleware
from app.core.exception_handlers import (
    validation_exception_handler,
    generic_exception_handler
)

from app.routers.student import router as student_router
from app.routers.grade import router as grade_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(LogRequestMiddleware())

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(student_router, prefix=settings.API_V1_STR)
app.include_router(grade_router, prefix=settings.API_V1_STR)  # Thêm grade router

@app.get("/")
def health_check():
    return {"success": True, "data": None, "message": "API is up and running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)