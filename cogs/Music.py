import collections
import youtube_dl
import discord
from random import shuffle, choice
from collections import namedtuple
import py_youtube as yti
from discord.ext import commands
import discord

# class MyLogger(object):
#     def debug(self, msg):
#         print(msg)

#     def warning(self, msg):
#         print(msg)

#     def error(self, msg):
#         print(msg)

# def my_hook(d):
#     print(d)
#     if d['status'] == 'finished':
#         print('Done downloading, now converting ...')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.connections = []

        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": '-vn'
        }

        self.YDL_OPTIONS = {
            "format": "bestaudio",
            # "logger": MyLogger(),
            # "progress_hooks": [my_hook]
        }

    async def search_yt(self, query: str, limit=15):
        yt = yti.Search(query, limit)
        return yt.videos()

    @commands.group(
        name="music"
    )
    @commands.guild_only()
    async def music(self, ctx: commands.Context):
        pass

    @music.command()
    @commands.guild_only()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("you need to be in a voice channel")
        else:
            vc = ctx.author.voice.channel
            if ctx.voice_client is None:
                await vc.connect()
            else:
                await ctx.voice_client.move_to(vc)

    @music.command(
        name="leave"
    )
    @commands.guild_only()
    async def leave(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()

    @music.command(
        name="play"
    )
    @commands.cooldown(1, 5)
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str):

        if ctx.voice_client is None:
            user_vc = ctx.author.voice.channel
            if user_vc is None:
                await ctx.send("You have to be in a vc to use this command")
            else:
                await user_vc.connect()

        vc: discord.VoiceClient = ctx.voice_client

        if "http" in query:
            url = query
            video = None
        else:
            video = await self.search_yt(query, limit=1)
            video = video[0]
            url = f"https://www.youtube.com/watch?v={video['id']}"

        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **self.FFMPEG_OPTIONS)

            embed = discord.Embed(
                color=self.bot.color
            )
            if video:
                embed.title = video['title']
            else:
                embed.title = url

            if video:
                if len(video['thumb']) > 0:
                    embed.set_image(url=video['thumb'][0])

            try:
                vc.play(source, after = lambda e: print(e) )
            except Exception as err:
                print(err)
            await ctx.send(embed=embed)

    @music.command()
    @commands.guild_only()
    async def pause(self, ctx: commands.Context):
        await ctx.voice_client.pause()
        await ctx.send("Paused!")

    @music.command()
    @commands.guild_only()
    async def resume(self, ctx: commands.Context):
        await ctx.voice_client.resume()
        await ctx.send("resumed")


def setup(bot):
    bot.add_cog(Music(bot))
