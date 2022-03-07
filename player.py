import asyncio
import youtube_dl
import discord
from collections import deque
from discord.ext import commands

ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192'
            }],
            'postprocessor_args': [
                '-ar', '16000'
            ],
            'prefer_ffmpeg': True,
            'keepvideo': True,
            'quiet': True
        }
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



class Queue():
    def __init__(self):
        self.container = {}

    def get_next_song(self, guild: int):
        try:
            return self.container[guild].pop()
        except IndexError:
            return False

    async def add_song(self, guild: int, *args):
        if guild not in self.container:
            self.container[guild] = deque()


        with youtube_dl.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(f"ytsearch:{args}", download=False)
        URL = info['entries'][0]['url']

        self.container[guild].append(URL)

    def print_queue(self, guild: int):
        print(self.container[guild])


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue()


    @commands.command(name='connect', help='connect')
    async def join(selfm, ctx):
        print('11')
        channel = ctx.author.voice.channel
        print(channel)
        await ctx.reply(f"Joined {channel}")
        await channel.connect()

    @commands.command(name='disconnect', help='disconnect')
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.reply(f"leaved")

    @commands.command(name='ping', help='ping')
    async def join(self, ctx):
        await ctx.reply(f"latency: {self.bot.latency*1000:,.0f} ms")




    @commands.command(name='play', help='play from youtube')
    async def play(self, ctx: commands.Context, *args):
        print(args)

        try:
            voice_channel = ctx.message.author.voice.channel
            await voice_channel.connect()
        except:
            pass

        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)
        print(guild.id)

        await self.queue.add_song(guild.id, args)




        if not voice_client.is_playing():
            URL = self.queue.get_next_song(guild.id)
            print(URL)
            voice_client.play(discord.FFmpegPCMAudio(source = URL, **FFMPEG_OPTIONS))


    @commands.command(name="kok")
    async def shuffle_command(self, ctx):
        self.queue.print_queue(ctx.guild.id)


def setup(bot):
    bot.add_cog(Music(bot))