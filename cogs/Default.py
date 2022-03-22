from discord import ApplicationContext, slash_command
from discord.ext import commands
from config import servers

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(guild_ids=servers)
    async def ping(self, ctx: ApplicationContext):
        await ctx.respond(f"My Ping Is: {round(self.bot.latency * 1000, 2)} ms")

def setup(bot):
    bot.add_cog(Default(bot))