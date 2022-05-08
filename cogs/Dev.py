from discord.ext import commands

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(
        name = "cog",
        aliases = ["load", "unload", "reload"]
    )
    async def load(self, ctx: commands.Context, *, extension: str):
        if ctx.invoked_with in ["load", "unload", "reload"]:
            try:
                func = getattr(self.bot, f"{ctx.invoked_with}_extension")
                func(extension)
            except Exception as err:
                print(err)
                await ctx.send("there was an error")
            else:
                await ctx.send("done")
        elif ctx.invoked_with == "cog":
            await ctx.send("Options: load, reload, and unload")
        else:
            await ctx.send("Unknown Command Invoked")

def setup(bot):
    bot.add_cog(Dev(bot))