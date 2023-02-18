import asyncio
import json
import os

import discord
from discord.ext.commands import Bot


async def main():
    print("Starting main.")
    intents = discord.Intents.default()
    bot = Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print("I am ready.")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        response = "Abc"
        await message.channel.send(response)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'token.json')
    with open(file_path, 'r') as file:
        token = json.load(file)
    if token is None:
        print('Fatal: No discord token.')
        exit(1)

    for c in bot.commands:
        print(c)
    print("Loading cog.")
    await bot.load_extension('src.discord_local.cog')
    bot.get_cog("DiscordCog")
    print("Starting bot.")
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
