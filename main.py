from discord.ext import commands
import discord
from EZPaginator import Paginator
import math

bot = commands.AutoShardedBot(command_prefix="+")
TOKEN = ''

bot.load_extension("music") #load music.py file
bot.load_extension("lyric")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name = '우리모두 "30초 손씻기" 실천합시다!', url='https://www.youtube.com/watch?v=P-rhqWpjVag'))
    print("봇 활성화")
    
@bot.command(aliases=["샤딩", "sharding", "shard"])
async def shard_id(ctx):
    await ctx.send(str(bot.latencies))
    await ctx.send(str(bot.latencies[ctx.author.guild.shard_id][1]))
    embed = discord.Embed(
        title = "Sharding (샤딩)",
        colour = discord.Colour.blurple()
    )
    embed.add_field(name="Shard_ID", value=str(ctx.author.guild.shard_id))
    embed.add_field(name="Shard Latency", value=str(math.floor(round(bot.latencies[ctx.author.guild.shard_id][1]*1000))) + "ms")
    await ctx.send(embed=embed)

bot.run(TOKEN) #run bot
