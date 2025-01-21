import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import os
from dotenv import load_dotenv
import logging
import platform
from agent import WeatherAgent

intents = discord.Intents.default()

# Enable message content intent so the bot can read messages.
# The message content intent must be enabled in the Discord Developer Portal as well.
intents.message_content = True

logger = logging.getLogger("discord")


PREFIX = "!"
CUSTOM_STATUS = "the forecasts"


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX), intents=intents
        )

        self.logger = logger
        self.weather_agent = WeatherAgent()

    async def on_ready(self):
        self.logger.info("-------------------")
        self.logger.info(f"Logged in as {self.user}")
        self.logger.info(f"Discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")

        # Set the bot's custom status to "Watching the forecasts"
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=CUSTOM_STATUS
            )
        )

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        self.logger.info(f"Message from {message.author}: {message.content}")

        response = self.weather_agent.run(message.content)
        if response is None:
            return

        await message.reply(response)

    async def on_command_completion(self, ctx: Context):
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        self.logger.info(
            f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})"
        )


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    bot = DiscordBot()
    bot.run(token)
