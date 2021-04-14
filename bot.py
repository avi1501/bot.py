import os
import random
import requests
import discord
from dotenv import load_dotenv
from discord.ext import commands

# for playing music
import youtube_dl



load_dotenv()


TOKEN = os.environ["DISCORD_TOKEN"]

bot = commands.Bot(command_prefix = "!")

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord! ")

@bot.command(name="test", help="Respond with the testing command")
async def test(ctx):
    commands = [
    'enjoy',
    'This is test command',
    'cool',
    ]
    response = random.choice(commands)
    await ctx.send(response)

@bot.command(name="roll_dice", help="simulate rolling dice")
async def roll(ctx, number_of_dice : int):
    dice = [
    str(random.choice(range(1,7))) for _ in range(number_of_dice)
    ]

    await ctx.send(','.join(dice))


@bot.command(name="toss_coin", help="Stimulate tossing coin")
async def coin(ctx, no_of_coins : int):
    coin = [
    random.choice(("H","T")) for _ in range(no_of_coins)
    ]
    await ctx.send(','.join(coin))

@bot.command(name="create_channel")
@commands.has_role('admin')
async def create_channel(ctx, channel_name="unnamed"):
    guild = ctx.guild
    already_exists = discord.utils.get(guild.channels, name=channel_name)
    if not already_exists:
        print(f"Creating new channel:{channel_name}")
        await guild.create_text_channel(channel_name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

#
# """ making bot to play music """

@bot.command()
async def play(ctx, url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key':'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality':'102',
        }],
    }
    def search(arg):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                requests.get(arg)
            except:

                video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
            else:
                video = ydl.extract_info(arg, download=False)
            return video['webpage_url']

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("wait for the current playing music to end or use the stop command")


    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="General")

    await voiceChannel.connect()

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)


    url = search(url)


    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio('song.mp3'))


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently! no audio is playing")

@bot.command()
async def resume(ctx):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="General")
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("This audio is not paused.")

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("This bot is not connected to any voice channel")

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()





bot.run(TOKEN)
