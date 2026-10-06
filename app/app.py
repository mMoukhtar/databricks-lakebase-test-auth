from fastapi import FastAPI

from app.api.router import app_router

app = FastAPI(
    title="Test Databricks - Lakebase Auth",
    version="0.0.1",
    description="A simple FastAPI app to test databirck to lakebase authentication",
)


app.include_router(app_router)


@app.get("")
def root():
    return {"This is the app root"}
