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
    
    # await bot.add_cog(General(bot))
    await bot.add_cog(Music(bot))

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

