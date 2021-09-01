from .enums import VerificationLevel

# TODO, gotta add others features from https://mystb.in/AdvertisersExperiencesMothers.json


class Party:
    """A meta class which takes in the data in the form of a dict sent by the API, as the only argument, and 
    generates an invite link and other meta information from that.

    BEWARE- THIS CLASS IS NOT INTENTED TO BE USED IN GENERAL AND IS JUST MEANT FOR DOCUMENTATION PURPOSES"""

    def __init__(self, data: dict):
        self.code: str = data['code']
        self.uses: int = data.get('uses')
        self.max_uses: int = data.get('max_uses')
        self.max_age: int = data.get('max_age')
        self.temporary: bool = data.get('temporary')

        # JSONS
        self.guild_info: dict = data.get("guild")
        self.channel_info: dict = data.get("channel")

    def __eq__(self, o: object) -> bool:
        # I am not really sure if it works, will want some reviews
        return isinstance(o, Party) and self.code == o.code

    @property
    def guild_id(self):
        return self.guild_info["id"]

    @property
    def guild_name(self):
        return self.guild_info["name"]

    @property
    def guild_description(self):
        return self.guild_info["description"]

    @property
    def guild_splash(self):
        return self.guild_info["splash"]

    @property
    def guild_banner(self):
        return self.guild_info["banner"]

    @property
    def guild_icon(self):
        return self.guild_info["icon"]

    @property
    def guild_verification_level(self) -> VerificationLevel:
        return self.guild_info["verification_level"]

    @property
    def guild_vanity_url(self):
        return f'https://disnake.gg/{self.guild_info["vanity_url_code"]}' or None

    @property
    def guild_is_nsfw(self):
        return self.guild_info["nsfw"]

    @property
    def guild_nsfw_level(self):
        return self.guild_info["nsfw_level"]

    def __repr__(self):
        return f"https://disnake.gg/{self.code}"

    def __str__(self):
        return f"https://disnake.gg/{self.code}"
