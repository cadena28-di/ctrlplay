"""
Content Generator - Generador de contenido
"""

from src.integrations.llm.client import LLMClient


class ContentGenerator:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()
        self.templates = {
            "article": "Artículo sobre {topic}",
            "blog": "Post de blog: {topic}",
            "social": "Post para redes sociales: {topic}",
            "email": "Email sobre {topic}",
            "script": "Script creativo: {topic}",
        }

    def generate(self, topic, content_type="article"):
        template = self.templates.get(content_type, self.templates["article"])
        prompt = (
            f"Redacta un borrador de tipo '{content_type}' sobre: {topic}. "
            "Organización: Chain Industria. Español, tono profesional."
        )
        result = self.llm.complete(prompt)

        body = template.format(topic=topic)
        if result.success and result.data:
            body = result.data.get("text", body)

        return {
            "type": content_type,
            "topic": topic,
            "template": body,
            "provider": result.provider,
            "status": "generated",
        }
