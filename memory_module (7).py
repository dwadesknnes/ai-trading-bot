import os
import json
from collections import defaultdict

class Memory:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        self.data = defaultdict(lambda: {"wins": 0, "losses": 0})
        self._load()

    def _load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    raw_data = json.load(f)
                    self.data.update(raw_data)
            except Exception as e:
                print(f"⚠️ Failed to load memory file: {e}")
                self.data = defaultdict(lambda: {"wins": 0, "losses": 0})

    def _save(self):
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save memory: {e}")

    def record_result(self, ticker, strategy_name, result):
        key = f"{ticker}_{strategy_name}"
        if key not in self.data:
            self.data[key] = {"wins": 0, "losses": 0}
        if result == "win":
            self.data[key]["wins"] += 1
        elif result == "loss":
            self.data[key]["losses"] += 1
        self._save()

    def get_stats(self, ticker, strategy_name):
        key = f"{ticker}_{strategy_name}"
        return self.data.get(key, {"wins": 0, "losses": 0}) 
