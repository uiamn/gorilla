import datetime
import re
import sqlite3
import uuid

import discord

DB_PATH = '../db.sqlite3'
REGEX_PICTURE = r'.+\.(png|jpe?g)'


with open('.token') as f:
    TOKEN = f.read().strip()

client = discord.Client()

@client.event
async def on_message(msg: discord.Message) -> None:
    if msg.author.bot:
        return

    print(msg.author)
    print(type(msg.author))
    print(str(msg.author))

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

client.run(TOKEN)
