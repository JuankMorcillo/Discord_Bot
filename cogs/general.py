from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        help_text = (
            "Available commands:\n"
            "!help - Show this help message\n"
            "!ping - Check bot responsiveness\n"
            "!play <url> - Play a song from the given URL\n"
            "!skip - Skip the current song\n"
            "!queue - Show the current song queue\n"
        )
        await ctx.send(help_text)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = self.bot.latency
        await ctx.send(f'Pong! Latency: {latency*1000:.2f} ms')
    
    @commands.command(name='join')
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined {channel.name}')
        else:
            await ctx.send('You are not connected to a voice channel.')
    
    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Disconnected from the voice channel.')
        else:
            await ctx.send('I am not connected to any voice channel.')

async def setup(bot):
    await bot.add_cog(General(bot))