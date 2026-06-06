import asyncio
import pickle

from pathlib import Path

from sqlalchemy import (
    select,
    distinct
)

from app.api.dependencies import (
    AsyncSessionLocal
)

from app.models.db_models import (
    NCRBRecord
)

from app.services.prediction_service import (
    PredictionService
)

from app.config import (
    MODELS_DIR
)


async def train_and_save_models():

    async with AsyncSessionLocal() as session:

        stmt = (
            select(
                distinct(NCRBRecord.city),
                NCRBRecord.crime_type
            )
        )

        result = await session.execute(stmt)

        combinations = result.all()

        service = PredictionService(session)

        for city, crime_type in combinations:

            try:

                rows = await service.fetch_time_series(
                    city=city,
                    crime_type=crime_type
                )

                df = (
                    service.prepare_prophet_dataframe(
                        rows
                    )
                )

                model = service.train_model(df)

                filename = (
                    f"{city}_{crime_type}"
                    .replace(" ", "_")
                    .replace("/", "_")
                    .lower()
                    + ".pkl"
                )

                model_path = (
                    MODELS_DIR /
                    filename
                )

                with open(
                    model_path,
                    "wb"
                ) as f:

                    pickle.dump(model, f)

                print(
                    f"Saved model: {filename}"
                )

            except Exception as e:

                print(
                    f"Skipping "
                    f"{city} - {crime_type}"
                )

                print(e)


if __name__ == "__main__":

    asyncio.run(
        train_and_save_models()
    )