class ActivityLink:
    def __init__(self, payload: dict):
        self.code = payload.pop(code)
    def __repr__(self):
         return f"https://discord.gg/{self.code}"
    def __str__(self):
         return f"https://discord.gg/{self.code}"
