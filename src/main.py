from fastapi import FastAPI
from src.config.config import settings
from src.routes.auth.route import router as auth_routes
from src.routes.text_summarizer_service.route import router as summary_service_routes


base_prefix = "/summary-app/api/v1"

app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        contact={"name": settings.NAME, "email": settings.EMAIL},
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

app.include_router(auth_routes, prefix=f"{base_prefix}/auth", tags=["Auth"])
app.include_router(summary_service_routes, prefix=f"{base_prefix}/summary", tags=["Summary"])

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="0.0.0.0", port=8000)
