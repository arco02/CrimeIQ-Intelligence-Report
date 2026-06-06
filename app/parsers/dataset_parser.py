import pandas as pd

from app.config import PROCESSED_DATASET_PATH


class DatasetParser:

    def __init__(self):
        self.file_path = PROCESSED_DATASET_PATH
        self.df = None

    def load_dataset(self):

        self.df = pd.read_excel(self.file_path)

        self.clean_columns()

        return self.df

    def clean_columns(self):

        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^\w\s]", "", regex=True)
        )

    def validate_required_columns(self):

        required_columns = [
            "year",
            "state",
            "city",
            "type",
            "number_of_cases"
        ]

        missing = [
            col
            for col in required_columns
            if col not in self.df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

    def normalize_dataframe(self):

        normalized_df = self.df.rename(
            columns={
                "type": "crime_type",
                "number_of_cases": "count"
            }
        )

        normalized_df = normalized_df[
            [
                "year",
                "state",
                "city",
                "crime_type",
                "count"
            ]
        ]

        normalized_df["count"] = (
            normalized_df["count"]
            .fillna(0)
            .astype(int)
        )

        return normalized_df

    def parse(self):

        self.load_dataset()

        self.validate_required_columns()

        normalized_df = self.normalize_dataframe()

        return normalized_df


if __name__ == "__main__":

    parser = DatasetParser()

    df = parser.parse()

    print(df.head())

    print("\nColumns:")
    print(df.columns.tolist())

    print(f"\nShape: {df.shape}")