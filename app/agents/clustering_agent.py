from app.services.clustering_service import (
    ClusteringService
)


class ClusteringAgent:

    def __init__(self, db):

        self.service = ClusteringService(db)

    async def analyze_city_risk(self):

        clusters = await self.service.cluster_cities()

        formatted = []

        for item in clusters:

            formatted.append(
                f"{item['city']}, "
                f"{item['state']} "
                f"→ {item['risk_tier']} Risk"
            )

        return (
            "City Risk Clustering Analysis\n\n"
            + "\n".join(formatted)
        )