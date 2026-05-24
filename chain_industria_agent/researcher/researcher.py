"""
Researcher Module - Investigación y análisis de datos
"""

from datetime import datetime

from researcher.analyzers.data_analyzer import DataAnalyzer
from researcher.analyzers.trend_analyzer import TrendAnalyzer
from researcher.data_sources.source_manager import SourceManager
from researcher.reports.report_generator import ReportGenerator
from src.integrations.memory.client import MemoryClient


class Researcher:
    def __init__(self, memory_client: MemoryClient | None = None):
        self.name = "Researcher Module"
        self.version = "1.1.0"
        self.status = "initialized"
        self.timestamp = datetime.now()
        self.memory = memory_client or MemoryClient()
        self.data_analyzer = DataAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.source_manager = SourceManager()
        self.report_generator = ReportGenerator()
        self.research_cache = []

    def search(self, query, sources=None):
        print(f"🔍 Buscando: {query}")
        if sources is None:
            sources = self.source_manager.get_default_sources()
        results = {
            "query": query,
            "sources": sources,
            "results": [],
            "timestamp": datetime.now().isoformat(),
        }
        for source in sources:
            result = self.source_manager.search(query, source)
            results["results"].append(result)

        self.research_cache.append(results)
        self.memory.log_search(
            query,
            sources,
            {
                "results": results["results"],
                "total_found": sum(
                    r.get("results_found", 0) for r in results["results"]
                ),
            },
        )
        print(f"✅ Búsqueda completada en {len(sources)} fuentes")
        return results

    def analyze_data(self, data, analysis_type="general"):
        print(f"📊 Analizando datos ({analysis_type})...")
        analysis = self.data_analyzer.analyze(data, analysis_type)
        print("✅ Análisis completado")
        return analysis

    def analyze_trends(self, data, period="monthly"):
        print(f"📈 Analizando tendencias ({period})...")
        trends = self.trend_analyzer.analyze(data, period)
        print("✅ Análisis de tendencias completado")
        return trends

    def generate_report(self, title, data, report_type="summary"):
        print(f"📄 Generando reporte: {title} ({report_type})...")
        report = self.report_generator.generate(title, data, report_type)
        print("✅ Reporte generado")
        return report

    def get_status(self):
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "cache_size": len(self.research_cache),
            "timestamp": str(self.timestamp),
        }

    def get_research_history(self):
        return self.research_cache

    def get_search_index(self, limit: int = 50):
        return self.memory.get_search_index(limit=limit).data
