import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Bot sozlamalari
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# YouTube'dan audio olish uchun sozlamalar
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **{'options': '-vn'}), data=data)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} sifatida tizimga kirdi')

@bot.command(name='play', help='YouTube URL orqali qo\'shiq ijro etadi')
async def play(ctx, *, url):
    if not ctx.message.author.voice:
        await ctx.send("Siz ovozli kanalga kirishingiz kerak!")
        return
    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop)
            ctx.voice_client.play(player)
            await ctx.send(f'Hozir ijro etilmoqda: {player.title}')
    except Exception as e:
        await ctx.send(f"Xato: {str(e)}")

@bot.command(name='join', help='Ovozli kanalga kiradi')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Siz ovozli kanalda emassiz!")

@bot.command(name='leave', help='Ovozli kanaldan chiqadi')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Bot ovozli kanalda emas!")

# Bot tokeningizni bu yerga qo'ying
bot.run('YOUR_BOT_TOKEN_HERE')
