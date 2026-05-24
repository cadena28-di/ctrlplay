"""
Report Generator - Generador de reportes
"""

from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.report_types = [
            "summary",
            "detailed",
            "executive",
            "technical",
            "analysis"
        ]
    
    def generate(self, title, data, report_type="summary"):
        if report_type not in self.report_types:
            report_type = "summary"
        
        report = {
            "title": title,
            "type": report_type,
            "data": data,
            "generated_at": datetime.now().isoformat(),
            "sections": self._generate_sections(report_type),
            "format": "markdown",
            "status": "generated"
        }
        return report
    
    def _generate_sections(self, report_type):
        sections = {
            "summary": ["Resumen", "Hallazgos clave", "Conclusiones"],
            "detailed": ["Introducción", "Metodología", "Resultados", "Análisis", "Conclusiones"],
            "executive": ["Resumen ejecutivo", "Recomendaciones", "Próximos pasos"],
            "technical": ["Especificaciones", "Implementación", "Resultados técnicos"],
            "analysis": ["Análisis", "Insights", "Recomendaciones"]
        }
        return sections.get(report_type, sections["summary"])
