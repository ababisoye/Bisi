"""HTTP API for ECG CSV uploads and score tracking."""

from io import BytesIO

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Score

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title="HealthView ECG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Validate an uploaded ECG CSV and return a concise dataset summary."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CSV files must be 10 MB or smaller.")
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")

    try:
        frame = pd.read_csv(BytesIO(contents))
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid CSV.") from exc

    if frame.empty or not len(frame.columns):
        raise HTTPException(status_code=400, detail="The CSV does not contain any ECG rows.")

    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    if not numeric_columns:
        raise HTTPException(status_code=400, detail="The CSV must contain at least one numeric ECG column.")

    return {
        "message": "ECG CSV uploaded successfully.",
        "filename": file.filename,
        "rows": len(frame),
        "columns": frame.columns.tolist(),
        "numeric_columns": numeric_columns,
    }


@app.post("/score")
def save_score(value: int, db: Session = Depends(get_db)):
    if not 0 <= value <= 100:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 100.")
    score = Score(value=value)
    db.add(score)
    db.commit()
    db.refresh(score)
    return {"id": score.id, "value": score.value}


@app.get("/score/stats")
def score_stats(db: Session = Depends(get_db)):
    average, count = db.query(func.avg(Score.value), func.count(Score.id)).one()
    return {"average": float(average or 0), "count": count}


@app.get("/get-random-plot")
def get_random_plot():
    raise HTTPException(status_code=503, detail="No ECG plot dataset is installed.")


handler = Mangum(app)
