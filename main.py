from discord.ext import commands
import discord
import os
from config import owners


import discord
import logging

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


if not os.environ.get("TOKEN", None):
    from dotenv import load_dotenv
    load_dotenv()

token = os.environ['TOKEN']

intents = discord.Intents.all()
if hasattr(intents, 'message_content'):
    intents.message_content = True

prefix = commands.when_mentioned_or(".")

bot = commands.Bot(
    command_prefix=prefix,
    intents=intents,
    owner_ids=owners
)

bot.color = discord.Color.from_rgb(240, 179, 255)


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