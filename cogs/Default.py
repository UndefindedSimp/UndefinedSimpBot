from discord.ext import commands

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """gets the bots ping"""
        await ctx.send(f"My Ping Is: {round(self.bot.latency * 1000, 2)} ms")


def setup(bot):
    bot.add_cog(Default(bot))