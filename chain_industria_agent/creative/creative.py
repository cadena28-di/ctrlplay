"""
Creative Module - Generador de contenido creativo
Gestiona la generación de ideas, contenido y creatividad del agente
"""

from datetime import datetime
from creative.generators.content_generator import ContentGenerator
from creative.generators.idea_generator import IdeaGenerator

class Creative:
    def __init__(self):
        self.name = "Creative Module"
        self.status = "initialized"
        self.timestamp = datetime.now()
        self.content_generator = ContentGenerator()
        self.idea_generator = IdeaGenerator()
        self.outputs = []
    
    def generate_content(self, topic, content_type="article"):
        """Genera contenido basado en un tema"""
        print(f"🎨 Generando {content_type} sobre: {topic}")
        content = self.content_generator.generate(topic, content_type)
        self.outputs.append({
            "type": content_type,
            "topic": topic,
            "content": content,
            "timestamp": datetime.now()
        })
        return content
    
    def generate_ideas(self, topic, quantity=5):
        """Genera ideas creativas"""
        print(f"💡 Generando {quantity} ideas sobre: {topic}")
        ideas = self.idea_generator.generate(topic, quantity)
        self.outputs.append({
            "type": "ideas",
            "topic": topic,
            "ideas": ideas,
            "timestamp": datetime.now()
        })
        return ideas
    
    def get_status(self):
        """Retorna el estado del módulo"""
        return {
            "name": self.name,
            "status": self.status,
            "outputs_generated": len(self.outputs),
            "timestamp": str(self.timestamp)
        }
    
    def list_outputs(self):
        """Lista todos los outputs generados"""
        return self.outputs

if __name__ == "__main__":
    creative = Creative()
    print(creative.get_status())
