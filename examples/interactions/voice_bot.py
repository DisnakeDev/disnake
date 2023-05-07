import disnake
import yt_dlp as youtube_dl 
from disnake.ext import commands
import asyncio
from typing import Any, Dict, Optional
import os
youtube_dl.utils.bug_reports_message = lambda: ""

ffmpeg_options = {'options':'-vn'}

ytdl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(self, source: disnake.AudioSource, *, data: Dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)

        self.title = data.get("title")

    @classmethod
    async def from_url(
        cls, url, *, loop: Optional[asyncio.AbstractEventLoop] = None, stream: bool = True
    ):
        loop = loop or asyncio.get_event_loop()
        data: Any = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        # print(data)
        # if "formats" in data:
        #     # take first item from a playlist
        #     data = data["formats"][5]
        
        filename = data["formats"][5]["url"] if stream else ytdl.prepare_filename(data)

        return cls(disnake.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    def __channel(self, inter):
        for voiceProtocol in self.bot.voice_clients:
            if voiceProtocol.guild == inter.guild:
                return voiceProtocol
            
    @commands.slash_command()
    async def join(self, inter: disnake.ApplicationCommandInteraction, channel: Optional[disnake.VoiceChannel] = None):
        """Joins a voice channel"""
        channel = inter.author.voice.channel if not channel else channel 
        if self.__channel(inter): await self.__channel(inter).disconnect()
        await channel.connect()
        await inter.response.send_message(f"Подключился к каналу {channel.mention}", ephemeral=True)


    @commands.slash_command()
    async def play(self, inter, *, url: str):
        """Plays from a url (almost anything youtube_dl supports)"""
        if self.__channel(inter): await self.__channel(inter).disconnect()
            
        voiceState = await self.ensure_voice(inter)

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

        voiceState.play(
            player, after=lambda e: print(f"Player error: {e}") if e else None
        )

        await inter.send(f"Now playing: {player.title}", ephemeral=True)



    @commands.slash_command()
    async def volume(self, inter, volume: int):
        """Changes the player's volume"""
        if not self.__channel(inter):
            return await inter.send("Not connected to a voice channel.")

        self.__channel(inter).source.volume = volume / 100
        await inter.send(f"Changed volume to {volume}%", ephemeral=True)

    @commands.slash_command()
    async def leave(self, inter: disnake.ApplicationCommandInteraction):
        """Stops and disconnects the bot from voice"""
        await self.__channel(inter).disconnect()
        await inter.response.send_message("Бот вышел из канала", ephemeral=True)
        
    @commands.slash_command()
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        """Stops and disconnects the bot from voice"""
        await self.ensure_voice(inter)
        await inter.response.send_message("Бот остановил воспроизведение", ephemeral=True)
    async def ensure_voice(self, inter):
        print(inter.bot.voice_clients)
        if self.__channel(inter) == None:
            if inter.author.voice:
                return await inter.author.voice.channel.connect()
            else:
                await inter.send("You are not connected to a voice channel.", ephemeral=True)
                raise commands.CommandError("Author not connected to a voice channel.")
        elif self.__channel(inter).is_playing():
            self.__channel(inter).stop()
            
            

bot = commands.Bot(command_prefix="!", intents=disnake.Intents().all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
