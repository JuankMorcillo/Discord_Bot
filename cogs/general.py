from discord.ext import commands
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        help_text = (
            "Available commands:\n"
            "%help - Show this help message\n"
            "%ping - Check bot responsiveness\n"
            "%play <url> - Play a song from the given URL\n"
            "%skip - Skip the current song\n"
            "%queue - Show the current song queue\n"
        )
        await ctx.send(help_text)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = self.bot.latency
        await ctx.send(f'Pong! Latency: {latency*1000:.2f} ms')
    
    @commands.command(name='join')
    async def join(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            try:
                if ctx.voice_client is None:
                    print(f"Intentando conectar a {voice_channel.name}...")
                    vc = await voice_channel.connect()
                    print(f"Conectado: voice_client={vc}, channel={getattr(vc, 'channel', None)}")
                    await ctx.send(f"✅ Conectado a {voice_channel.name}")
            except Exception as e:
                await ctx.send(f"No pude conectarme al canal de voz: {e}")
                print(f"Error al conectar a voz: {e}")
                return
        else:
            await ctx.send("No estás en un canal de voz. Conéctate a uno y vuelve a intentar.")
            return
    
    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            await asyncio.sleep(0.5)
            ctx.voice_client.cleanup()
            await ctx.voice_client.disconnect(force=True)
            await ctx.send('Disconnected from the voice channel.')
        else:
            await ctx.send('I am not connected to any voice channel.')

def setup(bot):
    bot.add_cog(General(bot))