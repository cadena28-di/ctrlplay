"""
Idea Generator - Generador de ideas creativas
"""

from src.integrations.llm.client import LLMClient


class IdeaGenerator:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()
        self.brainstorm_techniques = [
            "mind_mapping",
            "lateral_thinking",
            "brainstorming",
            "scamper",
        ]

    def generate(self, topic, quantity=5):
        prompt = (
            f"Genera {quantity} ideas creativas sobre '{topic}' para Chain Industria. "
            "Formato: una línea por idea, numeradas 1-N. Español."
        )
        result = self.llm.complete(
            prompt,
            system="Consultor creativo de Chain Industria. Ideas concretas y accionables.",
        )

        lines: list[str] = []
        if result.success and result.data:
            text = result.data.get("text", "")
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

        ideas = []
        for i in range(quantity):
            idea_text = lines[i] if i < len(lines) else f"Idea creativa #{i + 1} sobre {topic}"
            ideas.append(
                {
                    "id": i + 1,
                    "topic": topic,
                    "idea": idea_text,
                    "technique": self.brainstorm_techniques[i % len(self.brainstorm_techniques)],
                    "provider": result.provider,
                }
            )
        return ideas
