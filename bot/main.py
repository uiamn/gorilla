import discord
import re

REGEX_PICTURE = r'.+\.(png|jpe?g)'


with open('.token') as f:
    TOKEN = f.read().strip()

client = discord.Client()

@client.event
async def on_message(msg: discord.Message) -> None:
    if msg.author.bot:
        return

    print(msg.author)

    if msg.channel.name not in ['result', 'test']:
        # resultチャンネル以外は読まない
        return

    if len(msg.attachments) == 0:
        # 添付ファイルがない場合は終了
        return

    for attachment in msg.attachments:
        # 添付ファイルを読んで，拡張子がjpe?gかpngなら画像を取ってくる
        filename = attachment.filename.lower()
        if re.match(REGEX_PICTURE, filename) is None:
            continue

        with open(f'images/{filename}', 'wb') as f:
            await attachment.save(f)

client.run(TOKEN)
