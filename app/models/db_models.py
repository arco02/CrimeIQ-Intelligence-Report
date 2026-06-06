from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    func,
    UniqueConstraint,
)

from pgvector.sqlalchemy import Vector

from app.api.dependencies import Base


class NCRBRecord(Base):
    __tablename__ = "ncrb_records"

    id = Column(Integer, primary_key=True, index=True)

    year = Column(Integer, nullable=False, index=True)

    state = Column(String, nullable=False, index=True)

    city = Column(String, nullable=True, index=True)

    crime_type = Column(String, nullable=False, index=True)

    count = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "year",
            "state",
            "city",
            "crime_type",
            name="unique_crime_record"
        ),
    )


class TextChunk(Base):
    __tablename__ = "text_chunks"

    id = Column(Integer, primary_key=True)

    chunk_text = Column(Text, nullable=False)

    embedding = Column(Vector(384))

    year = Column(Integer, nullable=True)

    state = Column(String, nullable=True)

    city = Column(String, nullable=True)

    crime_type = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class CrimePrediction(Base):
    __tablename__ = "crime_predictions"

    id = Column(Integer, primary_key=True)

    forecast_year = Column(Integer, nullable=False)

    state = Column(String, nullable=True)

    city = Column(String, nullable=True)

    crime_type = Column(String, nullable=False)

    predicted_count = Column(Float, nullable=False)

    lower_bound = Column(Float, nullable=False)

    upper_bound = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class CityRiskProfile(Base):
    __tablename__ = "city_risk_profiles"

    id = Column(Integer, primary_key=True)

    city = Column(String, nullable=False, unique=True)

    state = Column(String, nullable=False)

    cluster_id = Column(Integer, nullable=False)

    risk_tier = Column(String, nullable=False)

    risk_score = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    report_type = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )