import os
import discord
import logging
import platform

from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
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

        # Load all the cogs/commands.
        await self.load_cogs()

        # Set the bot's custom status to "Watching the forecasts"
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=CUSTOM_STATUS
            )
        )

    async def load_cogs(self) -> None:
        """
        This function loads all the cogs, or command categories, in the cogs directory.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def on_message(self, message: discord.Message):
        await self.process_commands(message)

        # Ignore messages from self or other bots.
        if (
            message.author == self.user
            or message.author.bot
            or message.content.startswith("!")
        ):
            return

        self.logger.info(f"Message from {message.author}: {message.content}")

        # Run the weather agent whenever the bot receives a message.
        await self.weather_agent.run(message, message.content)

    async def on_command_completion(self, ctx: Context):
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        self.logger.info(
            f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})"
        )

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            await context.reply("Please provide a location.")
        else:
            await context.reply("An error occurred while executing the command.")
            raise error


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    bot = DiscordBot()
    bot.run(token)
