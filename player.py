
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