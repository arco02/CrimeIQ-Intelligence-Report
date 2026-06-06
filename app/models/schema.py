from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NCRBRecordBase(BaseModel):
    year: int
    state: str
    city: Optional[str] = None
    crime_type: str
    count: int


class NCRBRecordCreate(NCRBRecordBase):
    pass


class NCRBRecordResponse(NCRBRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    city: Optional[str]
    state: Optional[str]
    crime_type: str

    forecast_year: int

    predicted_count: float
    lower_bound: float
    upper_bound: float


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    response: str


class ClusterResponse(BaseModel):
    city: str
    state: str

    cluster_id: int

    risk_tier: str
    risk_score: float


class ReportResponse(BaseModel):
    title: str
    report_type: str
    file_path: str