import math
import re

import discord
import lavalink
from discord.ext import commands

url_rx = re.compile('https?:\\/\\/(?:www\\.)?.+')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(680769129254223872)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'ko', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

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
    async def play(self, ctx, *, query="이마트"):
        """ 링크나 제목을 주면 검색해 재생함. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        await player.set_volume(50)

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
            track = results['tracks'][0]
            embed.title = '플레이리스트에 추가됨:'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

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
                              title='플레이 중:', description=song)
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
            return await ctx.send(f'🔈 | {player.volume}%')

        await player.set_volume(volume / 2)  # Lavalink will automatically cap values between, or equal to 0-1000.
        await ctx.send(f'🔈 | 음량이 {player.volume}% 로 맞춰졌습니다.')

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

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError(':x: | ~~힘이.... 힘이 모자라단 말이다..!!~~ 권한이 부족합니다.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError(':x: | 저 너무 외로워요.. 제 채널로 와주세요..')


def setup(bot):
    bot.add_cog(Music(bot))