# SPDX-License-Identifier: MIT

"""A basic example showing how to integrate audio from youtube-dl into voice chat."""

# NOTE: this example requires ffmpeg (https://ffmpeg.org/download.html) to be installed
#       and available in your `%PATH%` or `$PATH`

# pyright: reportUnknownLambdaType=false

import asyncio
import os
from typing import Any, Dict, Optional

import disnake
import youtube_dl  # type: ignore
from disnake.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(self, source: disnake.AudioSource, *, data: Dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)

        self.title = data.get("title")

    @classmethod
    async def from_url(
        cls, url, *, loop: Optional[asyncio.AbstractEventLoop] = None, stream: bool = False
    ):
        loop = loop or asyncio.get_event_loop()
        data: Any = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        return cls(disnake.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: disnake.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Plays a file from the local filesystem"""
        await self.ensure_voice(ctx)
        source = disnake.PCMVolumeTransformer(disnake.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: {query}")

    @commands.command()
    async def yt(self, ctx, *, url: str):
        """Plays from a url (almost anything youtube_dl supports)"""
        await self._play_url(ctx, url=url, stream=False)

    @commands.command()
    async def stream(self, ctx, *, url: str):
        """Streams from a url (same as yt, but doesn't predownload)"""
        await self._play_url(ctx, url=url, stream=True)

    async def _play_url(self, ctx, *, url: str, stream: bool):
        await self.ensure_voice(ctx)
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=stream)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    description="Relatively simple music bot example",
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


bot.add_cog(Music(bot))

if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
