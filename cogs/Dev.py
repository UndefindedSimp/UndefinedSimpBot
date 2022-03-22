from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.group()
    async def cog(self, ctx):
        pass

    @cog.command()
    async def reload(self, ctx, *, ext):
        self.bot.reload_extension(ext)
        await ctx.send("done")
    
    @cog.command()
    async def load(self, ctx, *, ext):
        self.bot.load_extension(ext)
        await ctx.send("done")

    @cog.command()
    async def unload(self, ctx, *, ext):
        self.bot.unload_extension(ext)
        await ctx.send("done")