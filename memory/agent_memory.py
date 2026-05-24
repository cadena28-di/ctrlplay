xy
"""
Módulo de memoria del agente Chain Industria.
"""

import json


class MemoryAgent:
    def __init__(self):
        self.name = "memory_agent"

    def save(self, data):
        # Convertir a string seguro
        try:
            preview = json.dumps(data, ensure_ascii=False)
        except Exception:
            preview = str(data)

        print(f"[🧠] {self.name} guardó: {preview[:80]}...")

        return {
            "status": "saved",
            "data": data
        }

    def recall(self, query):
        return {
            "status": "recall",
            "query": query
        }

