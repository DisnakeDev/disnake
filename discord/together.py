class ActivityLink:
    """A meta class which takes in the payload sent by the API, as the only argument, and generates an
    invite link from that.
    
    BEWARE- THIS CLASS IS NOT INTENTED TO BE USED IN GENERAL AND IS JUST MEANT FOR DOCUMENTATION PURPOSES"""

    def __init__(self, payload: dict):
        self.code = payload.pop(code)
    def __repr__(self):
         return f"https://discord.gg/{self.code}"
    def __str__(self):
         return f"https://discord.gg/{self.code}"
