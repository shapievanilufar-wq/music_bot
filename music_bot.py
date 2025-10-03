import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv
import os

# .env faylidan tokenni o'qish
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Bot sozlamalari
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default().enable('message_content'))

# YouTube'dan musiqa olish sozlamalari
ytdl_options = {'format': 'bestaudio', 'noplaylist': True}
ytdl = yt_dlp.YoutubeDL(ytdl_options)

# Musiqa ijro etish uchun sinf
class Musiqa(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        super().__init__(source)
        self.title = data.get('title')

    @classmethod
    async def url_dan(cls, url):
        data = ytdl.extract_info(url, download=False)
        if 'entries' in data:
            data = data['entries'][0]
        return cls(discord.FFmpegPCMAudio(data['url']), data=data)

# Bot tayyor bo'lganda
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ishga tushdi!')

# Kanalga kirish buyrug'i
@bot.command(name='kir')
async def kir(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("Bot ovozli kanalga kirdi!")
    else:
        await ctx.send("Siz ovozli kanalda bo'lishingiz kerak!")

# Qo'shiq ijro etish buyrug'i
@bot.command(name='play')
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.send("Bot ovozli kanalda emas! Avval !kir buyrug'ini ishlat.")
        return
    try:
        musiqa = await Musiqa.url_dan(url)
        ctx.voice_client.play(musiqa)
        await ctx.send(f"Ijro etilmoqda: {musiqa.title}")
    except:
        await ctx.send("Xato: URL noto'g'ri yoki boshqa muammo bor.")

# Kanalni tark etish buyrug'i
@bot.command(name='chiq')
async def chiq(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bot ovozli kanaldan chiqdi!")
    else:
        await ctx.send("Bot hech qanday kanalda emas!")

# Botni ishga tushirish
bot.run(BOT_TOKEN)
