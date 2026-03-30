from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import uuid
import logging
from typing import List, Dict, Any

from api.models.schemas import TransactionNormalized, Status
from api.core.normalizer import FinancialNormalizer

# Setup logging for monitoring and self-healing trace
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fintech Data Aggregation MVP", version="1.0.0")

# Enable CORS for the React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for MVP demonstration (replace with PG/Redis for production)
INGESTION_TASKS: Dict[str, Any] = {}
NORMALIZED_STATE: Dict[str, Any] = {
    "transactions": [],
    "anomalies": []
}

normalizer = FinancialNormalizer()

async def run_ingestion_pipeline(task_id: str, file_content: bytes, filename: str):
    """
    Simulated background normalization worker with self-healing retry logic.
    """
    INGESTION_TASKS[task_id]["status"] = Status.PROCESSING
    logger.info(f"Task {task_id}: Starting normalization for {filename}")

    try:
        # Load the file (supporting CSV for MVP)
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            # Fallback (future: XML, JSON)
            raise ValueError("Unsupported file format. Only CSV supported for MVP.")

        # Self-healing: Retry if specific columns are missing by looking for synonyms (already handled in normalizer)
        # 1. Normalization engine
        source_id = f"source-{uuid.uuid4().hex[:6]}"
        transactions, anomalies = normalizer.normalize_csv(df, source_id)
        
        # 2. Store results
        NORMALIZED_STATE["transactions"].extend([t.model_dump() for t in transactions])
        NORMALIZED_STATE["anomalies"].extend(anomalies)

        INGESTION_TASKS[task_id]["status"] = Status.COMPLETED
        INGESTION_TASKS[task_id]["results"] = {
            "total": len(transactions),
            "anomalies": len(anomalies)
        }
        logger.info(f"Task {task_id}: Succeeded with {len(transactions)} txns")

    except Exception as e:
        # Handle failures and potentially retry or flag for manual review
        INGESTION_TASKS[task_id]["status"] = Status.FAILED
        INGESTION_TASKS[task_id]["error_log"] = str(e)
        logger.error(f"Task {task_id}: Failed with error - {str(e)}")
        # In production, we'd trigger an EventBridge event to retry here.

@app.post("/ingest/file")
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Accepts CSV file and starts normalization in the background."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed.")
    
    task_id = str(uuid.uuid4())
    content = await file.read()
    
    INGESTION_TASKS[task_id] = {
        "id": task_id,
        "status": Status.PENDING,
        "filename": file.filename,
        "results": None,
        "error_log": None
    }
    
    background_tasks.add_task(run_ingestion_pipeline, task_id, content, file.filename)
    
    return {"task_id": task_id, "status": "started"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Retrieve status of a background ingestion task."""
    if task_id not in INGESTION_TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    return INGESTION_TASKS[task_id]

@app.get("/transactions", response_model=List[Dict])
async def get_transactions(limit: int = 100, offset: int = 0):
    """Returns normalized transactions."""
    return NORMALIZED_STATE["transactions"][offset : offset + limit]

@app.get("/anomalies")
async def get_anomalies():
    """Returns detected data anomalies/quality issues."""
    return NORMALIZED_STATE["anomalies"]

@app.get("/monitor/stats")
async def get_stats():
    """Operational monitoring statistics."""
    total_tasks = len(INGESTION_TASKS)
    failed_tasks = len([t for t in INGESTION_TASKS.values() if t["status"] == Status.FAILED])
    completed_tasks = len([t for t in INGESTION_TASKS.values() if t["status"] == Status.COMPLETED])
    
    return {
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks
        },
        "health": "Healthy" if failed_tasks / (total_tasks or 1) < 0.2 else "Degraded"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
