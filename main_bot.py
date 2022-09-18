import os
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from urllib import parse, request
import re
import pytz
from neuralintents import GenericAssistant
import nltk
from youtube_dl import YoutubeDL
import youtube_dl
import ffmpeg
import asyncio 
from discord import FFmpegPCMAudio
from discord.utils import get
import yfinance as yf


cogs = ['music_cog', 'help_cog']


load_dotenv()
TOKEN = os.getenv('TOKEN')

client = commands.Bot(command_prefix='!', description="This is JulieBot", intents=discord.Intents.all())
chatbot = GenericAssistant('intents.json')
chatbot.train_model()
chatbot.save_model()

nltk.download('omw-1.4')


@client.event
async def on_ready():
    print('My Body is Ready') 
    await client.change_presence(activity=discord.Streaming(name='Randomyeet', url="https://www.twitch.tv/julliervh"))
    for extension in cogs:
        await client.load_extension(extension)
        return


@client.command()
async def ping(ctx):
    await ctx.send("Esto anda wacho")

@client.command()
async def Time(ctx):
    argtz = pytz.timezone("America/Argentina/Salta")
    argtime = datetime.now(argtz)
    currenttime = argtime.strftime("%H:%M:%S")
    await ctx.send(f"The current time is: {currenttime}")

@client.command(name="Information", aliases=["info"], help="Display information from the channel")
async def info(ctx):
    argtz = pytz.timezone("America/Argentina/Salta")
    argtime = datetime.now(argtz)
    currenttime = argtime.strftime("%H:%M:%S")

    embed = discord.Embed(title=f'{ctx.guild.name}', description='Los Machimbres de Alabama',
    timestamp=argtime, color=discord.Color.blurple())
    embed.add_field(name='Server created at', value=f'{ctx.guild.created_at}')
    embed.add_field(name='Server Owner', value=f'{ctx.guild.owner}')
    embed.add_field(name='Members', value=f'{ctx.guild.member_count}')
    embed.add_field(name="Server ID", value=f'{ctx.guild.id}')
    embed.set_thumbnail(url=f"{ctx.guild.icon}")
    await ctx.send(embed=embed)


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.content.startswith("!JulieBot"):
        response = chatbot.request(msg.content[10:])
        await msg.channel.send(response)
    await client.process_commands(msg)

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(name="Youtube", aliases=["yt"], help="Plays a selected song from youtube")
async def yt(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('https://www.youtube.com/results?' + query_string)
    search_results = re.findall('watch\?v=(.{11})',html_content.read().decode('utf-8'))
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])
    ctx.voice_client.stop()
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': 'bestaudio'}
    vc = ctx.voice_client
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/watch?v={search_results[0]}', download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)


@client.command(name='restart')
async def restart(ctx):

    await ctx.send("Restarting bot...")
    restart_bot()


@client.command(
    name='gon',
    description='Hisoka',
    pass_context=True,
)
async def gon(ctx):
    # grab the user who sent the command
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    source = FFmpegPCMAudio('gon.mp3')
    player = voice.play(source)
    await ctx.send("Restarting bot...")
    time.sleep(5)
    await restart(ctx)

@client.command(name="StockPrice", aliases=["st"], help="get the current stock/Crypto price")
async def StockPrice(ctx, stock):
    stock_info = yf.Ticker(f'{stock}').info
    current = stock_info['currentPrice']
    previous = stock_info['regularMarketPreviousClose']
    if current == previous:
        return 0
    try:
        change = round(((current - previous) / previous) * 100.0, 2)
        await ctx.send(f"{stock} Current price is: \n ${current}  ({change}%)")
    except ZeroDivisionError:
        return 0


client.run(TOKEN)
