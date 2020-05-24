import math
import re
from discord.utils import get
import discord
import lavalink
import asyncio
from discord.ext import commands

url_rx = re.compile('https?:\\/\\/(?:www\\.)?.+')

bots = commands.Bot(command_prefix="+")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.volumee = 50

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(680769129254223872)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'ko', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')
            print(bot.lavalink)

        bot.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        
    @commands.command(aliases=['p', 'ㅔ'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play(self, ctx, *, query="shilu"):
        """ 링크나 제목을 주면 검색해 재생함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send(f':x: | `{query}` 의 검색결과가 없습니다!')

        embed = discord.Embed(color=discord.Color.blurple())

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = '재생목록 추가됨:'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)}'
        else:
            tracks = results['tracks']
            if len(tracks) >= 5:
                songs = ["1. " + tracks[0]['info']['title'], "2. " + tracks[1]['info']['title'], "3. " + tracks[2]['info']['title'], "4. " + tracks[3]['info']['title'], "5. " + tracks[4]['info']['title']]
                infoo = "\n".join(songs)
                embed.title = '곡 중에서 선택'
                embed.description = infoo
                msg = await ctx.send(embed=embed)
                await asyncio.gather(
                    msg.add_reaction("1️⃣"),
                    msg.add_reaction("2️⃣"),
                    msg.add_reaction("3️⃣"),
                    msg.add_reaction("4️⃣"),
                    msg.add_reaction("5️⃣"),
                    msg.add_reaction("❌")
                )

                def check(reaction, user):
                    return user == ctx.author

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=15)
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(title="시간이 초과됨", description="시간이 초과되었습니다. 명령어를 다시 입력해주세요!", colour=discord.Colour.red())
                    await msg.edit(embed=timeout_embed)
                else:
                    react = str(reaction.emoji)
                    if react == "1️⃣":
                        index = 0
                    elif react == "2️⃣":
                        index = 1
                    elif react == "3️⃣":
                        index = 2
                    elif react == "4️⃣":
                        index = 3
                    elif react == "5️⃣":
                        index = 4
                    elif react == "❌":
                        canceled_embed = discord.Embed(title="요청이 취소됨", description="요청 취소 명령을 받았습니다!", colour=discord.Colour.light_grey())
                        return await msg.edit(embed=canceled_embed)
                    else:
                        unknown_embed = discord.Embed(title="알 수 없는 이모지", description="나와있는 이모지만 선택해주세요!", colour=discord.Colour.red())
                        return await msg.edit(embed=unknown_embed)
                    track = tracks[index]
                    good_embed = discord.Embed(colour=discord.Colour.blurple())
                    good_embed.title = '플레이리스트에 추가되었습니다!'
                    good_embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                    good_embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track['info']['identifier']}/0.jpg")
                    player.add(requester=ctx.author.id, track=track)
                    await msg.edit(embed=good_embed)

        if not player.is_playing:
            await player.play()

        await player.set_volume(self.volumee)

    @commands.command(aliases=['m', 'move', 'ㅡ'])
    async def seek(self, ctx, *, seconds: int):
        """ 시간을 초단위로 스킵함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(f':hammer_pick: | 시간 스킵: **{lavalink.utils.format_time(track_time)}**')

    @commands.command(aliases=['s', 'ㄴ'])
    async def skip(self, ctx):
        """ 트랙을 스킵함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        await player.skip()
        await ctx.send('`스킵`하였습니다!')

    @commands.command(aliases=['st', 'ㄴㅅ'])
    async def stop(self, ctx):
        """ 플레이를 멈추고 모든 요청을 삭제함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        player.queue.clear()
        await player.stop()
        await ctx.send(':stop_button: | 플레이를 멈추었습니다.')

    @commands.command(aliases=['np', 'n', 'playing', 'ㅞ', 'ㅜㅔ'])
    async def now(self, ctx):
        """ 현재 플레이되고 있는 곡의 상태를 가져옴. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.current:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = '🔴 | 라이브'
        else:
            duration = lavalink.utils.format_time(player.current.duration)

        song = f'**[{player.current.title}]({player.current.uri})**\n({position}/{duration})'

        embed = discord.Embed(color=discord.Color.blurple(),
                              title='플레이 중!', description=song)
        embed.set_image(url=f"https://img.youtube.com/vi/{player.current.identifier}/0.jpg")
        await ctx.send(embed=embed)

    @commands.command(aliases=['q', 'ㅂ'])
    async def queue(self, ctx, page: int = 1):
        """ 플레이리스트를 표시. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(':x: | 비어있는 플레이리스트 입니다.')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                              description=f'**{len(player.queue)} 개의 곡 **\n\n{queue_list}')
        embed.set_footer(text=f'페이지 {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(aliases=['pa', 'ㅔㅁ'])
    async def pause(self, ctx):
        """ 일시정지, 또는 이어듣기를 활성화함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | 이어듣기')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | 일시정지')

    @commands.command(aliases=['vol', 'v', 'ㅍ'])
    async def volume(self, ctx, volume: int = None):
        """ 소리를 낮추거나 올림. (0-1000 까지) """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 | {player.volume * 2}%')

        self.volumee = volume / 2
        await player.set_volume(volume / 2)  # Lavalink will automatically cap values between, or equal to 0-1000.
        await ctx.send(f'🔈 | 음량이 {player.volume * 2}% 로 맞춰졌습니다.')

    @commands.command(aliases=['sh', '노'])
    async def shuffle(self, ctx):
        """ 플레이리스트를 흔들어 놓습니다! (?) """
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        player.shuffle = not player.shuffle
        await ctx.send('🔀 | 셔플 ' + ('활성화 됨' if player.shuffle else '비활성화 됨'))

    @commands.command(aliases=['loop', 'l', 'ㅣ'])
    async def repeat(self, ctx):
        """ 곡을 반복합니다. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(':x: | 곡이 플레이되고 있지 않습니다.')

        player.repeat = not player.repeat
        await ctx.send('🔁 | 반복 ' + ('활성화 됨' if player.repeat else '비활성화 됨'))

    @commands.command(aliases=['r', 'ㄱ'])
    async def remove(self, ctx, index: int):
        """ 아몰랑 쨌든 지웁니당ㅇㅇ """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(':x: | 비어있는 플레이리스트 입니다.')

        if index > len(player.queue) or index < 1:
            return await ctx.send(f'숫자는 1 과 {len(player.queue)} **사이 여야** 합니다.')

        removed = player.queue.pop(index - 1)

        await ctx.send(f'플레이리스트에서 **{removed.title}** 을(를) 삭제시켰습니다.')

    @commands.command(aliases=['dc', 'leave', 'quit'])
    async def disconnect(self, ctx):
        """ 디스커넥트 """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(':x: | 채널에 연결되어있지 않습니다!')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('제가 들어가 있는 채널에 접속하셔야 합니다!')

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send(':handshake: | 연결이 해제되었습니다.')

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.

        should_connect = ctx.command.name in ('play')  # Add commands that require joining voice to work.

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError(':x: | 먼저 음성채널 부터 들가고 말하시져 ;;;')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError(':x: | 채널에 연결되어있지 않습니다. 저를 빼다니 속상하네요..ㅠㅠ')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError(':x: | 권한이 부족하거나 사람이 너무 많네요 ;;')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError(':x: | 어.. 그니까 저는 다른 채널에 빼놓고 지들끼리만 파티하는 거죠..?')


def setup(bot):
    bot.add_cog(Music(bot))
