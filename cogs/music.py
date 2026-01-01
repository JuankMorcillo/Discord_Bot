import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from model.song import Song
from model.playlist import PlayList
import yt_dlp
import asyncio
from typing import Any
# import pandas as pd

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = PlayList()
        
    def search_song(self, query: str):
        videos_search = VideosSearch(query, limit=20)
        result: Any = videos_search.result()

        # print(f"Search result for '{query}': {pd.DataFrame(result['result'])}")

        if isinstance(result, dict) and result.get('result'):
            video_info = result['result'][0]
            title = video_info['title']
            url = video_info['link']
            return Song(title, url)
        else:
            return None
    
    def play_next(self, ctx, error=None):
        """Callback para reproducir la siguiente canción"""
        if error:
            print(f'Player error: {error}')
            
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return
            
        next_song = self.playlist.next_song()
        if next_song:
            # Usar create_task en lugar de run_coroutine_threadsafe
            asyncio.create_task(self.play_song(ctx, next_song))
        
    async def play_song(self, ctx, song: Song):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await ctx.send("Not connected to a voice channel.")
            return
            
        ytdl_opts: Any = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'default_search': 'auto',
            'source_address': '0.0.0.0',  # Bind to ipv4
        }
        
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                info = ytdl.extract_info(song.url, download=False)
                url = info.get('url')
                title = info.get('title', song.title)
                
            if not url:
                await ctx.send(f"Could not extract audio source for {title}")
                return
            
            # Opciones mejoradas de FFmpeg para mayor estabilidad
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                'options': '-vn -bufsize 512k'
            }
        
            source = discord.FFmpegPCMAudio(
                url,
                before_options=ffmpeg_options['before_options'],
                options=ffmpeg_options['options']
            )
            
            # Wrapper para manejar el callback correctamente
            def after_callback(error):
                coro = self.handle_after_playing(ctx, error)
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except Exception as exc:
                    print(f'After callback error: {exc}')
            
            ctx.voice_client.play(source, after=after_callback)
            await ctx.send(f'Now playing: {title}')
            
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
            print(f"Error in play_song: {e}")
    
    async def handle_after_playing(self, ctx, error):
        """Manejador asíncrono para después de reproducir"""
        if error:
            print(f'Player error: {error}')
        
        next_song = self.playlist.next_song()
        if next_song and ctx.voice_client and ctx.voice_client.is_connected():
            await self.play_song(ctx, next_song)
    
    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        print(f"Play command invoked with query: {query}")
        # Verificar que el usuario está en un canal de voz
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel.")
            return
        
        # Conectar automáticamente si no está conectado
        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect(timeout=30.0, reconnect=True)
                await ctx.send(f"Connected to {ctx.author.voice.channel.name}")
            except asyncio.TimeoutError:
                await ctx.send("Connection timeout. Please try again.")
                return
            except Exception as e:
                await ctx.send(f"Failed to connect: {str(e)}")
                return
        
        # Verificar que estamos en el mismo canal
        if ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.send("You must be in the same voice channel as the bot.")
            return
        
        song = self.search_song(query)
        
        if not song:
            await ctx.send("Song not found.")
            return
            
        # Si ya está reproduciendo, añadir a la cola
        if ctx.voice_client.is_playing():
            self.playlist.add_to_queue(song)
            await ctx.send(f'Added to queue: {song.title}')
        else:
            await self.play_song(ctx, song)
    
    @commands.command(name='skip')
    async def skip(self, ctx):
        if not ctx.voice_client:
            await ctx.send("Not connected to a voice channel.")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("No song is currently playing.")
            
    @commands.command(name='pause')
    async def pause(self, ctx):
        if not ctx.voice_client:
            await ctx.send("Not connected to a voice channel.")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the current song.")
        else:
            await ctx.send("No song is currently playing.")    
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        if not ctx.voice_client:
            await ctx.send("Not connected to a voice channel.")
            return
            
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the current song.")
        else:
            await ctx.send("No song is currently paused.")
    
    @commands.command(name='disconnect', aliases=['dc'])
    async def disconnect(self, ctx):
        """Desconectar el bot del canal de voz"""
        if not ctx.voice_client:
            await ctx.send("Not connected to a voice channel.")
            return
        
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
        self.playlist = PlayList()  # Limpiar la playlist

async def setup(bot):
    await bot.add_cog(Music(bot))


