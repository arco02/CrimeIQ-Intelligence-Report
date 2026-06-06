import pandas as pd

from prophet import Prophet

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import (
    NCRBRecord,
    CrimePrediction
)

from app.config import (
    FORECAST_YEARS_DEFAULT,
    MIN_FORECAST_POINTS
)


class PredictionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_time_series(
        self,
        city: str,
        crime_type: str
    ):

        stmt = (
            select(
                NCRBRecord.year,
                NCRBRecord.count
            )
            .where(
                NCRBRecord.city.ilike(city),
                NCRBRecord.crime_type.ilike(crime_type)
            )
            .order_by(NCRBRecord.year)
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        if len(rows) < MIN_FORECAST_POINTS:
            raise ValueError(
                f"Not enough data points for forecasting. "
                f"Minimum required: {MIN_FORECAST_POINTS}"
            )

        return rows

    def prepare_prophet_dataframe(self, rows):

        df = pd.DataFrame(
            [
                {
                    "ds": f"{row.year}-01-01",
                    "y": row.count
                }
                for row in rows
            ]
        )

        df["ds"] = pd.to_datetime(df["ds"])

        return df

    def train_model(self, df):

        model = Prophet(
            yearly_seasonality=True,
            changepoint_prior_scale=0.5
        )

        model.fit(df)

        return model

    def generate_forecast(
        self,
        model,
        years=None          # ← accept None safely
    ):
        # Defensively fall back to default if None is passed
        if years is None:
            years = FORECAST_YEARS_DEFAULT

        future = model.make_future_dataframe(
            periods=years,
            freq="YE"       # "Y" is deprecated in newer pandas; "YE" = year-end
        )

        forecast = model.predict(future)

        return forecast

    async def save_predictions(
        self,
        forecast,
        city,
        crime_type,
        years
    ):

        if years is None:
            years = FORECAST_YEARS_DEFAULT

        forecast = forecast.tail(years)

        for _, row in forecast.iterrows():

            prediction = CrimePrediction(
                city=city,
                crime_type=crime_type,
                forecast_year=int(row["ds"].year),
                predicted_count=float(row["yhat"]),
                lower_bound=float(row["yhat_lower"]),
                upper_bound=float(row["yhat_upper"])
            )

            self.db.add(prediction)

        await self.db.commit()

    async def predict(
        self,
        city: str,
        crime_type: str,
        years: int = None   # ← allow None, resolve inside
    ):
        if years is None:
            years = FORECAST_YEARS_DEFAULT

        rows = await self.fetch_time_series(
            city,
            crime_type
        )

        prophet_df = self.prepare_prophet_dataframe(rows)

        model = self.train_model(prophet_df)

        forecast = self.generate_forecast(model, years=years)

        await self.save_predictions(
            forecast,
            city,
            crime_type,
            years
        )

        predictions = forecast.tail(years)

        return [
            {
                "year": int(row["ds"].year),
                "prediction": round(float(row["yhat"]), 2),
                "lower_bound": round(
                    float(row["yhat_lower"]), 2
                ),
                "upper_bound": round(
                    float(row["yhat_upper"]), 2
                )
            }
            for _, row in predictions.iterrows()
        ]