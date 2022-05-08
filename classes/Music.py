import asyncio
from functools import partial

import discord
from discord.ext import commands
from async_timeout import timeout
from youtube_dl import YoutubeDL
from py_youtube import Data

# working

class opts:
    ffmpeg = {
        'before_options': '-nostdin',
        'options': '-vn'
    }

    ytdl = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

ytdl = YoutubeDL(opts.ytdl)

class Save:
    embed_color: discord.Color = None

class YoutubeSource(discord.PCMVolumeTransformer):
    def __init__(self, source, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title: str = data.get('title')
        self.web_url: str  = data.get('webpage_url')
        self.video = Data(self.web_url)

    @property
    def author(self):
        return self.video.channel_name()
    
    @property
    def thumb(self):
        return self.video.thumb()

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.AbstractEventLoop, download: bool =False):
        loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        embed = discord.Embed(
            title="Queue Added",
            description=f"{data['title']} has been added to queue",
            color=Save.embed_color
        )

        user: discord.User = ctx.author

        embed.set_author(name=user.display_name)

        await ctx.send(
            embed=embed
        )

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data, ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data, requester)

    def cleanup(self):
        super().cleanup()

    def __del__(self):
        self.cleanup()



class MusicPlayer:
    def __init__(self, ctx: commands.Context) -> None:
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = self.ctx.bot
        self._guild: discord.Guild = ctx.guild
        self._channel: discord.TextChannel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume: float = .5
        self.current = None

        self.bot.loop.create_task(self.player_loop())

    async def set_np(self, source: YoutubeSource):

        embed = discord.Embed(
            title=f"Now Playing: {source.title}",
            color=Save.embed_color
        )

        embed.set_footer(
            text=f"Requested By: {source.requester.display_name}",
            icon_url=source.requester.avatar.url
        )

        embed.set_image(url=source.thumb)

        self.np = await self.ctx.send(
            embed=embed
        )
        

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):  # 5 minutes
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YoutubeSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YoutubeSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing the song.')
                    print(e)
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.set_np(source)
            await self.next.wait()

            source.cleanup()
            self.current = None

            try:
                await self.np.delete()
            except discord.HTTPException:
                pass



    def destroy(self, guild: discord.Guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))


