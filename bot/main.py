import datetime
import re
import sqlite3
import uuid
from async_timeout import asyncio

import discord

from typing import Optional

DB_PATH = '../db.sqlite3'
REGEX_PICTURE = r'.+\.(png|jpe?g)'


with open('.token') as f:
    TOKEN = f.read().strip()


intents = discord.Intents.default()
intents.members = True
intents.reactions = True

client = discord.Client(intents=intents)
temp_channel: Optional[discord.TextChannel] = None

@client.event
async def on_ready() -> None:
    pass

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    if reaction.emoji == '\N{KEY}' and temp_channel is not None:
        await temp_channel.set_permissions(user, read_messages=True, send_messages=True)

@client.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User) -> None:
    if reaction.emoji == '\N{KEY}' and temp_channel is not None:
        await temp_channel.set_permissions(user, read_messages=False, send_messages=False)



@client.event
async def on_message(msg: discord.Message) -> None:
    if msg.author.bot:
        return

    print(msg.author)
    print(type(msg.author))
    print(str(msg.author))

    if msg.content.startswith('?start') and temp_channel is None:
        print(client.guilds[0])
        await start_temp_channel(client.guilds[0], msg.channel)  # 多分 BEATECH サーバにしか入ってないので．．．

    if msg.channel.name not in ['result', 'test']:
        # resultチャネル以外は読まない
        return

    if len(msg.attachments) == 0:
        # 添付ファイルがない場合は終了
        return

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # gorilla に登録されてないユーザのメッセージは無視
        author = cur.execute('SELECT portal_id FROM users WHERE discord_id = ?', (str(msg.author), )).fetchone()

        print(author)

        if author is None:
            return

        for attachment in msg.attachments:
            # 添付ファイルを読んで，拡張子がjpe?gかpngなら画像を取ってくる
            filename = attachment.filename.lower()
            if re.match(REGEX_PICTURE, filename) is None:
                continue

            ext = filename.split('.')[-1]
            save_filename = f'{uuid.uuid4().hex}.{ext}'

            with open(f'../images/{save_filename}', 'wb') as f:
                await attachment.save(f)

            cur.execute(
                'INSERT INTO results(user, comment, filename, created_at) VALUES (?, "", ?, ?)',
                (author[0], save_filename, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
            )


async def start_temp_channel(guild: discord.Guild, channel: discord.TextChannel) -> None:
    sent_message = await channel.send('一時的なテキストチャネルを作りました．下の絵文字クリックで参加．もう一度クリックで退出．')
    await sent_message.add_reaction('\N{KEY}')

    global temp_channel
    temp_channel = await guild.create_text_channel('一時雑談鯖', overwrites={
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    })
    msg ='''雑談用の一時的なチャネルです．
**\N{WARNING SIGN}\N{WARNING SIGN}\N{WARNING SIGN}2時間後に内容ごと消えます\N{WARNING SIGN}\N{WARNING SIGN}\N{WARNING SIGN}**
残したい内容はここで会話しないようにしてください．
'''
    await temp_channel.send(msg)
    await asyncio.sleep(60*60*2)
    await temp_channel.delete()
    temp_channel = None


client.run(TOKEN)
