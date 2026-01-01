import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from cogs.general import General
from cogs.music import Music
import asyncio
load_dotenv()

TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD_ID = int(os.getenv('GUILD_ID', '0'))
PREFIX = '%'

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # CRÍTICO: Este intent es necesario para voz
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_extensions()
    
    # Listar todos los comandos cargados
    print("\n=== Comandos cargados ===")
    for command in bot.commands:
        print(f"  - {PREFIX}{command.name} (aliases: {command.aliases})")
    print("========================\n")

async def load_extensions():
    try:
        await bot.load_extension('cogs.general')
        print("✓ General cog loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load general: {e}")
    
    try:
        await bot.load_extension('cogs.music')
        print("✓ Music cog loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load music: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Comando no encontrado. Usa {PREFIX}help para ver comandos disponibles.")
        print(f"Command not found: {ctx.message.content}")
    else:
        await ctx.send(f"Error: {error}")
        print(f"Command error: {error}")

@bot.event
async def on_disconnect():
    print("Bot disconnected from Discord")

@bot.event
async def on_resumed():
    print("Bot resumed session")

@bot.event
async def on_voice_state_update(member, before, after):
    # Desconectar si el bot está solo en el canal
    if bot.user is None:
        return
    if member.id == bot.user.id:
        return
        
    voice_client = member.guild.voice_client
    if voice_client is None:
        return
        
    # Si el bot está solo en el canal de voz, desconectarse después de 60 segundos
    if len(voice_client.channel.members) == 1:
        await asyncio.sleep(60)
        if len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
            print(f"Bot disconnected from {voice_client.channel.name} due to inactivity")

asyncio.run(bot.start(TOKEN), debug=True)

