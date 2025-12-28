import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from model.song import Song
from model.playlist import PlayList
import yt_dlp
from typing import Any

class Music (commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = PlayList()
        
    
    def search_song(self, query: str):
        videos_search = VideosSearch(query, limit = 1)
        result: Any = videos_search.result()
        if isinstance(result, dict) and result.get('result'):
            video_info = result['result'][0]
            title = video_info['title']
            url = video_info['link']
            return Song(title, url)
        else:
            return None
        
    async def play_song(self, ctx, song: Song):        
        ytdl_opts: Any = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(song.url, download=False)
            url = info.get('url')
            title = info.get('title', song.title)
            
        if not url:
            await ctx.send(f"Could not extract audio source for {title}")
            return
        
        ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
        }
    
        source = discord.FFmpegPCMAudio(url,
                                        before_options=ffmpeg_options['before_options'],
                                        options=ffmpeg_options['options'])
        
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {title}')
    
    @commands.command(name='play')
    async def play(self, ctx, url: str):
        song = self.search_song(url)
        self.playlist.add_to_queue(song)
        
        try:
            
            if song:
                await self.play_song(ctx, song)
            else:
                await ctx.send("Song not found.")
            
        except Exception as e:
            await ctx.send(f"Error playing song: {str(e)}")
            return        
        
    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            
            self.playlist.next_song()
            
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("No song is currently playing.")
            
    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the current song.")
        else:
            await ctx.send("No song is currently playing.")    
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the current song.")
        else:
            await ctx.send("No song is currently paused.")
            

def setup(bot):
    bot.add_cog(Music(bot))
        
        
        