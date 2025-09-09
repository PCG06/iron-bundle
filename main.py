import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN not set in .env")
if SERVER_ID is None:
    raise ValueError("SERVER_ID not set in .env")

TESTING = False

handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.all()
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")
    
    try:
        if TESTING:
            guild = discord.Object(id=int(SERVER_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to guild {SERVER_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s) globally")
        
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def main():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")
    
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{bot.user.name} is offline!")