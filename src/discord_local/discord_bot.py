import asyncio
import json

import discord
from discord.ext.commands import Bot


async def main():
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

    with open('token.json', 'r') as file:
        token = json.load(file)
    if token is None:
        print('Fatal: No discord token.')
        exit(1)

    for c in bot.commands:
        print(c)
    await bot.load_extension('cog')
    bot.get_cog("DiscordCog")
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
