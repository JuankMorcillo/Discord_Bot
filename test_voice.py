import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = str(os.getenv('DISCORD_TOKEN'))
PREFIX = '%'

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot listo: {bot.user}')
    print(f'Opus cargado: {discord.opus.is_loaded()}')
    
    # Intentar cargar opus manualmente si no está cargado
    if not discord.opus.is_loaded():
        try:
            discord.opus.load_opus('opus')  # Linux
        except:
            try:
                discord.opus.load_opus('libopus-0.dll')  # Windows
            except Exception as e:
                print(f'No se pudo cargar opus: {e}')

@bot.command(name='testjoin')
async def testjoin(ctx):
    print(f"Comando recibido de {ctx.author}")
    print(f"Usuario en canal de voz: {ctx.author.voice}")
    
    if not ctx.author.voice:
        await ctx.send("No estás en un canal de voz")
        return
    
    channel = ctx.author.voice.channel
    print(f"Canal objetivo: {channel.name} (ID: {channel.id})")
    print(f"Permisos del bot: {channel.permissions_for(ctx.guild.me)}")
    
    try:
        print("Intentando conectar...")
        vc = await channel.connect(timeout=30.0, reconnect=True)
        print(f"¡Conectado! VoiceClient: {vc}")
        print(f"is_connected(): {vc.is_connected()}")
        await ctx.send(f"✅ Conectado a {channel.name}")
    except asyncio.TimeoutError:
        print("TIMEOUT al conectar")
        await ctx.send("❌ Timeout al conectar")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        await ctx.send(f"❌ Error: {type(e).__name__}: {e}")

bot.run(TOKEN)