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

@bot.command(pass_context=True, aliases=["핑"])
async def ping(ctx):
    """ 핑퐁펭퓅풍펑평퍙 (레이턴시 가져옴) """
    await ctx.send(str(bot.latency))
    api_ping = f"{math.floor(round(bot.latency*1000))}ms"
    embed1 = discord.Embed(
        title="봇 지연수치",
        description=f"API Latency: {api_ping}",
        colour=discord.Colour.blurple()
    )
    embed2 = discord.Embed(
        title="봇 지연수치",
        description="여긴 왜 보세요..? 궁금한거 있어요?",
        colour=discord.Colour.blurple()
    )
    embed3 = discord.Embed(
        title="봇 지연수치",
        description=f"음... 사실 이곳은 개발자가 짜증나서 만든곳이니까 어서 가세요.",
        colour=discord.Colour.blurple()
    )
    embed4 = discord.Embed(
        title="이스터에그",
        description="우리 멍청한 개발자가 VoiceClient Latency 를 개발하다 망쳐서 생긴곳이예요.",
        colour=discord.Colour.blurple()
    )
    embed5 = discord.Embed(
        title="흠..",
        description="다른 할일은 없으세요?",
        colour=discord.Colour.blurple()
    )
    embed6 = discord.Embed(
        title="좀 가세요 ㅈㅂ ;;",
        description="어서 공부나 하세요..;;",
        colour=discord.Colour.blurple()
    )
    embed7 = discord.Embed(
        title="공부가 싫어요?",
        description="코딩을 해요..",
        colour=discord.Colour.blurple()
    )
    embed8 = discord.Embed(
        title="아 몰랑",
        description="코드가 너무 길어져서 더 안할게요.",
        colour=discord.Colour.blurple()
    )
    embed9 = discord.Embed(
        title="...",
        description="그냥 제 반응이 궁금하신거... 맞죠? 도움 따위는 원하시지도 않는 것 같구..",
        colour=discord.Colour.blurple()
    )
    embed10 = discord.Embed(
        title="<Empty>",
        description="*비어있는 임베드형 메시지이다.",
        colour=discord.Colour.blurple()
    )
    msg = await ctx.send(embed=embed1)
    embeds = [embed1, embed2, embed3, embed4, embed5, embed6, embed7, embed8, embed9, embed10]
    page = Paginator(bot, msg, embeds=embeds)
    await page.start()


bot.run(TOKEN) #run bot
