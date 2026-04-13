class StateManager:
    def __init__(self):
        self.state = {
            "task": None,
            "status": "idle",
            "history": []
        }

    def update(self, key, value):
        self.state[key] = value

    def add_history(self, entry):
        self.state["history"].append(entry)

    def get(self):
        return self.state