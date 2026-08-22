from app.schemas.vision import VisionDiagnosis, VisionRecommendation


class DevelopmentVisionAdapter:
    async def diagnose(self, image: bytes) -> VisionDiagnosis:
        return VisionDiagnosis(
            label="unavailable",
            confidence=0,
            status="low_confidence_fallback",
            recommendation=VisionRecommendation(
                condition="unavailable",
                confidence=0,
                what_to_do_now=[],
                prevention=[],
                treatment_options=[],
                recommended_inputs=[],
                sources=[],
            ),
            nearby_inputs=[],
        )


class VisionService:
    def __init__(self, adapter: DevelopmentVisionAdapter | None = None) -> None:
        self.adapter = adapter or DevelopmentVisionAdapter()

    async def diagnose(self, image: bytes) -> VisionDiagnosis:
        return await self.adapter.diagnose(image)
