from discord.ext import commands
import discord
import os
from config import owners

if not os.environ['TOKEN']:
    from dotenv import load_dotenv
    load_dotenv()

token = os.environ['TOKEN']

intents = discord.Intents.all()
intents.message_content = True

prefix = commands.when_mentioned_or(".")

bot = commands.Bot(
    command_prefix=prefix,
    intents=intents,
    owner_ids=owners
)


cogfiles = [
    f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs/")
    if filename.endswith(".py")
]


@bot.event
async def on_ready():
    print(f"{bot.user} has logged in!")

    for cog in cogfiles:
        try:
            bot.load_extension(cog)
        except Exception as err:
            print(err)
            print(f"failed to load cog: {cog}")
        else:
            print(f"loaded cog: {cog}")

if __name__ == "__main__":
    bot.run(token)