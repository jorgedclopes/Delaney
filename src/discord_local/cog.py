from datetime import datetime, timedelta
from discord.ext import tasks, commands

from src.google_client.bot import create_notification_messages

DEFAULT_CATEGORY_CHANNEL_NAME = 'Text Channels'
DEFAULT_TEXT_CHANNEL_NAME = 'bot-logs'


def compute_times(repeat):
    base_time = datetime.now()
    # delta = timedelta(seconds=1)
    delta = timedelta(days=1)
    return [(base_time + i * delta).time() for i in range(1, repeat)]  # itertools.count(start=1)]


class DiscordCog(commands.Cog):
    def __init__(self, c):
        self.index = 0
        self.client = c

    @commands.Cog.listener()
    async def on_ready(self):
        times = compute_times(3)
        self.printer.change_interval(time=times)
        print(times)
        print("Logged In!")
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(time=[datetime.now().time()])
    async def printer(self):
        self.index += 1
        print(self.index)
        for guild in self.client.guilds:
            # I can't await inside the next block because it will evaluate the default block and create a channel
            category_channel = next((channel for channel in guild.categories
                                     if channel.name == DEFAULT_CATEGORY_CHANNEL_NAME),
                                    None)
            category_channel = category_channel if category_channel is not None else \
                await guild.create_text_channel(DEFAULT_CATEGORY_CHANNEL_NAME)
            text_channel = next((channel for channel in category_channel.text_channels
                                 if channel.name == DEFAULT_TEXT_CHANNEL_NAME),
                                None)
            text_channel = text_channel if text_channel is not None else \
                await category_channel.create_text_channel(DEFAULT_TEXT_CHANNEL_NAME)

            print(text_channel)

            folder_name = 'Pathfinder - Legacy of Fire'
            try:
                messages = create_notification_messages(folder_name)
                print(messages)
                print('Sending message.')
                for message in messages:
                    await text_channel.send(message)
                print('Message sent.')
                print("Target channel: {}".format(text_channel))
            except Exception as e:
                print("ERROR {}".format(e))

            times = compute_times(5)
            self.printer.change_interval(time=times)

    @printer.before_loop
    async def before_printer(self):
        print('waiting until everything is ready...')
        await self.client.wait_until_ready()

    # @printer.after_loop
    # async def after_printer(self):
    #     print('Restarting loop.')
    #     times = compute_times(10)
    #     self.printer.change_interval(time=times)
    #     self.printer.restart()


async def setup(bot):
    await bot.add_cog(DiscordCog(bot))
