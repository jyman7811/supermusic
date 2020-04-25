import lyricsgenius
from discord.ext import commands
import discord
import traceback
from EZPaginator import Paginator
genius = lyricsgenius.Genius('gRWeP4k87nQeNc2bvwu5i5XT9xNedG7XsKRT5kKXkihnjlMfNtkSG-esXhzE_TvK')

class Lyric(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["가사", "ly", "ㅣㅛ"])
    async def lyric(self, ctx , * , song_name="Counting Stars"):
        try:
            song = genius.search_song(song_name)
            print(song.lyrics)
        except:
            embed = discord.Embed(
                title = f"{song_name} 의 가사",
                description = f"에러: {traceback.format_exc()}",
                colour = discord.Colour.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title = f"{song_name} 의 가사", colour = discord.Colour.green())
            try:
                embed.description = song.lyrics
                await ctx.send(embed=embed)
            except:
                embed.description = song.lyrics[:1900]
                embed2 = discord.Embed(
                    title = f"{song_name} 의 가사",
                    description = song.lyrics[1900:],
                    colour = discord.Colour.green()
                )
                msg = await ctx.send(embed=embed)
                embeds = [embed, embed2]
                page = Paginator(self.bot, msg, embeds=embeds)
                await page.start()

def setup(bot):
    bot.add_cog(Lyric(bot))