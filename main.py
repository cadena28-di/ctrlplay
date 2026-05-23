import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from researcher.agent_researcher import ResearcherAgent
from creative.agent_creative import CreativeAgent
from memory.agent_memory import MemoryAgent

class CoordinatorAgent:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.creative = CreativeAgent()
        self.memory = MemoryAgent()
    
    def run_system(self):
        print("🤖 Coordinador activando sistema multi-agente...\n")
        
        info = self.researcher.research("Chain Industria Bucaramanga Google Maps")
        self.memory.save(info)
        
        ideas = self.creative.generate("estrategias de crecimiento industrial")
        self.memory.save(ideas)
        
        print("\n✅ Sistema completo ejecutado. Listo para autoaprendizaje.")

def main():
    print("🚀 Sistema Multi-Agente Chain Industria iniciado\n")
    coordinator = CoordinatorAgent()
    coordinator.run_system()

if __name__ == "__main__":
    main()
