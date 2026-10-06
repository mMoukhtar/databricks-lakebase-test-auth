from fastapi import FastAPI

app = FastAPI(
    title="Test Databricks - Lakebase Auth",
    version="0.0.1",
    description="A simple FastAPI app to test databirck to lakebase authentication",
)


@app.get("/healthy")
def healthy_check():
    return {"healthy": "ok"}
