from .enums import ChannelType, InviteTarget, NSFWLevel, UserFlags, try_enum, VerificationLevel

# Seems like all the things from https://mystb.in/AdvertisersExperiencesMothers.json have been added 


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
    target_type: :class:`InviteTarget`
        The type of the target of the invite.
    created_at: :class:`str`
        The time of the creation of the invite.
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
    channe_id: :class:`int`
        The ID of the voice channel, for which, the invite was created.
    channel_name: :class:`str`
        The name of the voice channel, for which, the invite was created.
    channel_type: :class:`ChannelType`
        The type of the channel, for which, the invite was created. (Always ``VoiceChannel``)
    inviter_id: :class:`int`
        The ID of the inviter.
    inviter_username: :class:`str`
        The username (without discriminator) of the inviter.
    inviter_avatar: :class:`str`
        The avatar of the inviter.
    inviter_discriminator: :class:`int`
        The discriminator (tag) of the inviter.
    inviter_tag: :class:`int`
        The discriminator (tag) of the inviter.
    inviter_name: :class:`str`
        The username (with discriminator) of the inviter.
    inviter_public_flags: :class:`UserFlags`
        The flags of the inviter.
    inviter_is_bot: :class:`bool`
        If the inviter is a bot (Always True)
    application_id: :class:`int`
        The ID of the target application.
    application_name: :class:`str`
        The name of the target application.
    application_icon: :class:`str`
        The icon of the target application.
    application_description: :class:`str`
        The description of the target application.
    application_summary: :class:`str`
        The summary of the target application.
    application_cover_image: :class:`str`
        The cover image of the target application.
    application_hook: :class:`bool`
        Is there a hook for the target application.
    application_verify_key: :class:`str`
        The verification key of the target application.
    application_max_participants: :class:`int`
        The maximum number of participants allowed (-1 means unlimited)
    
    """

    def __init__(self, data: dict):
        self.code: str = data['code']
        self.uses: int = data.get('uses')
        self.max_uses: int = data.get('max_uses')
        self.max_age: int = data.get('max_age')
        self.temporary: bool = data.get('temporary')
        self.created_at: str = data.get("created_at")        
        self.target_type: InviteTarget = try_enum(InviteTarget, data.get("target_type"))

        # Nested Dicts
        self.guild_info: dict = data.get("guild")
        self.channel_info: dict = data.get("channel")
        self.inviter_info: dict = data.get("inviter")
        self.application_info: dict = data.get("target_application")

    def __eq__(self, o: object) -> bool:
        # I am not really sure if it works, will want some reviews. I also don't know if this is even required...
        return isinstance(o, Party) and self.code == o.code

    @property
    def guild_id(self) -> int:
        return self.guild_info["id"]

    @property
    def guild_name(self) -> str:
        return self.guild_info["name"]

    @property
    def guild_description(self) -> str:
        return self.guild_info["description"]

    @property
    def guild_splash(self) -> str:
        return self.guild_info["splash"]

    @property
    def guild_banner(self) -> str:
        return self.guild_info["banner"]

    @property
    def guild_icon(self) -> str:
        return self.guild_info["icon"]

    @property
    def guild_verification_level(self) -> VerificationLevel:
        return try_enum(VerificationLevel, self.guild_info["verification_level"])

    @property
    def guild_vanity_url(self):
        return f'https://discord.gg/{self.guild_info["vanity_url_code"]}' or None

    @property
    def guild_is_nsfw(self) -> bool:
        return self.guild_info["nsfw"]

    @property
    def guild_nsfw_level(self) -> NSFWLevel:
        return try_enum(NSFWLevel, self.guild_info["nsfw_level"])
    
    @property
    def channel_id(self) -> int:
        return self.channel_info["id"]
    
    @property
    def channel_name(self) -> str:
        return self.channel_info["name"]
    
    @property
    def channel_type(self) -> ChannelType:
        return try_enum(ChannelType, self.channel_info["type"])
    
    @property
    def inviter_id(self) -> int:
        return self.inviter_info["id"]
    
    @property
    def inviter_username(self) -> str:
        return self.inviter_info["username"]

    @property
    def inviter_avatar(self) -> str:
        return self.inviter_info["avatar"]
    
    @property
    def inviter_discriminator(self) -> int:
        return self.inviter_info["discriminator"]
    
    @property
    def inviter_tag(self) -> int:
        return self.inviter_discriminator
    
    @property
    def inviter_name(self) -> str:
        return f"{self.inviter_username}#{self.inviter_discriminator}"
    
    @property
    def inviter_public_flags(self) -> UserFlags:
        return try_enum(UserFlags, self.inviter_info["public_flags"])
    
    @property
    def inviter_is_bot(self) -> bool:
        return self.inviter_info["bot"]
    
    @property
    def application_id(self) -> int:
        return self.application_info["id"]
    
    @property
    def application_name(self) -> str:
        return self.application_info["name"]
    
    @property
    def application_icon(self) -> str:
        return self.application_info["icon"]
    
    @property
    def application_description(self) -> str:
        return self.application_info["description"]
    
    @property
    def application_summary(self) -> str:
        return self.application_info["summary"]
    
    @property
    def application_cover_image(self) -> str:
        return self.application_info["cover_image"]
    
    @property
    def application_hook(self) -> bool:
        return self.application_info["hook"]
    
    @property
    def application_rpc_origins(self) -> list:  # Gotta see a list of what objects this returns
        return self.application_info["rpc_origins"]
    
    @property
    def application_max_participants(self) -> int:
        return self.application_info.get("max_participants")  # -1 means unlimited? idk tbh, but we will take this as unlimited for now

    @property
    def application_verify_key(self) -> str:
        return self.application_info.get("verify_key")  # Gotta see what this thing does tbh

    def __str__(self) -> str:
        return f"https://discord.gg/{self.code}"
