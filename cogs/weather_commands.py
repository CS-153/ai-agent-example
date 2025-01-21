from discord.ext import commands
from discord.ext.commands import Context


# This cog contains all of the weather-related commands the bot supports.
class WeatherCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="today")
    async def today(self, ctx: Context, arg):
        """
        This command returns the weather for today.
        """

        await self.bot.weather_agent.run(
            ctx.message,
            f"What is today's weather in {arg}? Only return today's forecast.",
        )

    @commands.hybrid_command(name="week")
    async def week(self, ctx: Context, arg):
        """
        This command returns the weekly weather forecast for a given location.
        """

        await self.bot.weather_agent.run(
            ctx.message,
            f"What is the weekly weather forecast in {arg}?",
        )


async def setup(bot) -> None:
    await bot.add_cog(WeatherCommands(bot))
