
import itertools

from numpy import tile
from sqlalchemy import desc
from classes.Music import MusicPlayer, Save, YoutubeSource

import discord
from discord.ext import commands

class MusicSave:
    players: dict[int, MusicPlayer] = {}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        Save.embed_color = self.bot.color

    @property
    def players(self):
        return MusicSave.players


    async def cleanup(self, guild: discord.Guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def get_player(self, ctx: commands.Context):
        try:
            player = self.players.get(ctx.guild.id, None)
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        if player == None:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player
    
    async def create_source(self, ctx: commands.Context, query: str):
        return await YoutubeSource.create_source(ctx, query,
            loop=self.bot.loop,
            download=False
        )

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice.channel:
            await ctx.send("your not in a vc")
            return
        channel: discord.VoiceChannel = ctx.author.voice.channel

        vc: discord.VoiceClient = ctx.voice_client

        if vc:
            await vc.move_to(channel)
        else:
            await channel.connect(timeout=120, reconnect=True)

        await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str):
        vc = ctx.voice_client
        channel: discord.VoiceChannel = ctx.author.voice.channel

        if not vc:
            if not channel:
                await ctx.send("your not in a vc")
            await channel.connect(timeout=120, reconnect=True)
        
        if vc:
            if vc.channel.id != channel.id:
                await vc.move_to(channel)


        if not vc:
            await ctx.send("not connected to voice")
            return
        
        player = await self.get_player(ctx)

        source = await self.create_source(ctx, query)

        await player.queue.put(source)

    @commands.command()
    @commands.guild_only()
    async def playing(self, ctx: commands.Context):
        player = await self.get_player(ctx)

        if not player:
            return await ctx.send("no songs playing right now")

        await ctx.send(
            embed=player.np.embeds[0]
        )

    @commands.command()
    async def wipequeue(self, ctx: commands.Context):
        player = await self.get_player(ctx)
        if player.queue.empty:
            await ctx.send("queue is already empty")
        else:
            for i in range(player.queue.qsize):
                await player.queue.get()

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx: commands.Context):
        vc: discord.VoiceClient = ctx.voice_client

        if not vc or not vc.is_connected():
            await ctx.send('I am not currently connected to voice!')
            return

        player = await self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('queue is empty')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt, color=Save.embed_color)

        await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx: commands.Context):
        vc: discord.VoiceClient = ctx.voice_client

        if not vc or not vc.is_connected():
            await ctx.send('I am not currently connected to voice!')
            return
        
        await vc.disconnect()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            await ctx.send("Not currently playing anything")
            return
        elif vc.is_paused():
            return
        
        vc.pause()
        await ctx.send(
            embed=discord.Embed(
                title="Paused",
                description=f"{ctx.author} has paused the song."
            )
        )

    @commands.command()
    async def resume(self, ctx: commands.Context):
        vc: discord.VoiceClient = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command()
    async def stop(self, ctx: commands.Context):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        await self.cleanup(ctx.guild)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        vc: discord.VoiceClient = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    
    @commands.command()
    async def volume(self, ctx: commands.Context, *, vol: float = None):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice.')

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = await self.get_player(ctx)

        if not vol:
            return await ctx.send(
                embed=discord.Embed(
                    title="Volume",
                    description=f"{vc.source.volume * 100}%",
                    color=Save.embed_color
                )
            )

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(
            embed=discord.Embed(
                title="Volume Changed",
                description=f"{ctx.author} has changed the volume to {round(player.volume * 100, 2)}%",
                color=Save.embed_color
            )
        )


def setup(bot):
    bot.add_cog(Music(bot))
