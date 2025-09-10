import discord
from discord.ext import commands
import os
import random
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
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")

    await bot.change_presence(
        activity=discord.CustomActivity(name="Quarking my Drive!"),
        status=discord.Status.idle
    )
    
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


ironbundle_text_array = [
    "Hydro Pump go brr!",
    "Freeze Dry go brr!",
    "Don't make me set up Aurora Veil!",
    "Flip Turn! I'm outta here!",
    "Beep boop! Ice type superiority!",
    "My Speed even makes Flutter Mane quiver!",
    "Ready to sweep with my Booster Energy!"
]

delibird_text_array = [
    "Hello, gramps!",
    "Now that's a name I haven't heard in a long time."
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    message_content = message.content.lower()
    ironbundle_index = message_content.find("iron bundle")
    delibird_index = message_content.find("delibird")

    if ironbundle_index != -1 and delibird_index != -1:
        if ironbundle_index < delibird_index:
            random_response = random.choice(ironbundle_text_array)
            await message.reply(random_response, mention_author=False)
        else:
            random_response = random.choice(delibird_text_array)
            await message.reply(random_response, mention_author=False)
    elif ironbundle_index != -1:
        random_response = random.choice(ironbundle_text_array)
        await message.reply(random_response, mention_author=False)
    elif delibird_index != -1:
        random_response = random.choice(delibird_text_array)
        await message.reply(random_response, mention_author=False)

    await bot.process_commands(message)


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