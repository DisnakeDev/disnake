from .enums import NSFWLevel, try_enum, VerificationLevel

# TODO, gotta add others features from https://mystb.in/AdvertisersExperiencesMothers.json


class Party:
    """A meta class which takes in the data in the form of a dict sent by the API, as the only argument, and 
    generates an invite link and other meta information from that.

    .. container:: operations
        
        .. describe:: str(x)

            Returns the complete invite link.
        
        .. describe:: x == y

            Checks if two invite links are equal.
    
    Attributes
    ----------
    code: :class:`str`
        The raw code without the ``discord.gg/`` prefix.
    max_uses: :class:`int`
        The maximum number of times the code can be used. ``0`` means unlimited.
    uses: :class:`int`
        The number of times the code has been used.
    max_age: :class:`int`
        The maximum age of the invite in seconds.
    temporary: :class:`bool`
        If the invite is temporary or permanent.
    guild_id: :class:`int`
        The ID of the guild, for whose voice channel, the invite was created.
    guild_name: :class:`int`
        The name of the guild, for whose voice channel, the invite was created.
    guild_description: :class:`str`
        The description of the guild, for whose voice channel, the invite was created.
    guild_splash: :class:`str`
        The splash of the guild, for whose voice channel, the invite was created.
    guild_banner: :class:`str`
        The banner of the guild, for whose voice channel, the invite was created.
    guild_icon: :class:`str`
        The icon of the guild, for whose voice channel, the invite was created.
    guild_verification_level: :class:`VerificationLevel`
        The verification level of the guild, for whose voice channel, the invite was created.
    guild_vanity_url: :class:`str`
        The vanity url of the guild, for whose voice channel, the invite was created. (If applicable)
    guild_is_nsfw: :class:`bool`
        The NSFW status of the guild, for whose voice channel, the invite was created.
    guild_nsfw_level: :class:`NSFWLevel`
        The NSFW level of the guild, for whose voice channel, the invite was created.
    

    """

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
        # I am not really sure if it works, will want some reviews. I also don't know if this is even required...
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
    def guild_verification_level(self):
        return try_enum(VerificationLevel, self.guild_info["verification_level"])

    @property
    def guild_vanity_url(self):
        return f'https://discord.gg/{self.guild_info["vanity_url_code"]}' or None

    @property
    def guild_is_nsfw(self):
        return self.guild_info["nsfw"]

    @property
    def guild_nsfw_level(self):
        return try_enum(NSFWLevel, self.guild_info["nsfw_level"])

    def __str__(self):
        return f"https://discord.gg/{self.code}"
