class MemoryAgent:
    def __init__(self):
        self.name = "Memory"
    def save(self, data):
        print(f"💾 {self.name} guardó: {data[:80]}...")
