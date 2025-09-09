import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN not set in .env")

handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")


async def main():
    await bot.load_extension("cogs.speciesinfo")
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{bot.user.name} is offline!")
