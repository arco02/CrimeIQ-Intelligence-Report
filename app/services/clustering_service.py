import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import (
    NCRBRecord,
    CityRiskProfile
)


class ClusteringService:

    def __init__(self, db: AsyncSession):

        self.db = db

    async def fetch_city_crime_data(self):

        stmt = select(NCRBRecord)

        result = await self.db.execute(stmt)

        records = result.scalars().all()

        rows = []

        for record in records:

            rows.append({
                "city": record.city,
                "state": record.state,
                "crime_type": record.crime_type,
                "count": record.count
            })

        return pd.DataFrame(rows)

    def prepare_features(self, df):

        pivot_df = df.pivot_table(
            index=["city", "state"],
            columns="crime_type",
            values="count",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        feature_columns = [
            col
            for col in pivot_df.columns
            if col not in ["city", "state"]
        ]

        scaler = StandardScaler()

        scaled_features = scaler.fit_transform(
            pivot_df[feature_columns]
        )

        return pivot_df, scaled_features, feature_columns

    def assign_risk_tiers(self, model, scaled_features):
        """
        Assign LOW / MEDIUM / HIGH / CRITICAL tiers by ranking
        clusters on their *actual* centroid magnitude.

        KMeans cluster IDs (0, 1, 2, 3) are arbitrary — cluster 0
        is not necessarily the lowest-crime group.  We rank each
        cluster by the L1-norm of its centroid (sum of all scaled
        feature values) and assign tiers from least to most severe.
        """
        n_clusters = model.n_clusters

        # L1-norm of each centroid: higher → more crime overall
        centroid_norms = np.sum(
            np.abs(model.cluster_centers_),
            axis=1
        )

        # argsort gives indices that would sort norms ascending
        # rank[cluster_id] = position (0 = lowest, 3 = highest)
        rank_order = np.argsort(centroid_norms)
        cluster_rank = np.empty(n_clusters, dtype=int)
        for rank, cluster_id in enumerate(rank_order):
            cluster_rank[cluster_id] = rank

        tier_labels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        # Map each row's cluster_id → its earned tier
        point_clusters = model.predict(scaled_features)
        tiers = [tier_labels[cluster_rank[c]] for c in point_clusters]

        return point_clusters, tiers

    async def cluster_cities(self):

        df = await self.fetch_city_crime_data()

        pivot_df, scaled_features, feature_columns = (
            self.prepare_features(df)
        )

        model = KMeans(
            n_clusters=4,
            random_state=42,
            n_init=10
        )

        model.fit(scaled_features)

        clusters, tiers = self.assign_risk_tiers(
            model,
            scaled_features
        )

        pivot_df["cluster_id"] = clusters
        pivot_df["risk_tier"] = tiers

        # risk_score: sum of raw (unscaled) feature values
        # gives an interpretable total-crime count per city
        feature_data = pivot_df[feature_columns].values
        pivot_df["risk_score"] = feature_data.sum(axis=1).astype(float)

        for _, row in pivot_df.iterrows():

            profile = CityRiskProfile(
                city=row["city"],
                state=row["state"],
                cluster_id=int(row["cluster_id"]),
                risk_tier=row["risk_tier"],
                risk_score=float(row["risk_score"])
            )

            self.db.add(profile)

        await self.db.commit()

        return pivot_df[
            [
                "city",
                "state",
                "cluster_id",
                "risk_tier",
                "risk_score"
            ]
        ].to_dict(orient="records")