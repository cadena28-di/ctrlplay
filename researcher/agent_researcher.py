class ResearcherAgent:
    def __init__(self):
        self.name = "Researcher"
    def research(self, query):
        print(f"🔍 {self.name} investigando: {query}")
        return f"Información sobre: {query}"
