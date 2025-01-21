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

        res = self.bot.weather_agent.run(
            f"What is today's weather in {arg}? Only return today's forecast."
        )

        if res is None:
            await ctx.reply("I couldn't find the weather for that location.")
        else:
            await ctx.reply(res)

    @commands.hybrid_command(name="week")
    async def week(self, ctx: Context, arg):
        """
        This command returns the weekly weather forecast for a given location.
        """

        res = self.bot.weather_agent.run(
            f"What is the weekly weather forecast in {arg}?"
        )

        if res is None:
            await ctx.reply("I couldn't find the weather for that location.")
        else:
            await ctx.reply(res)


async def setup(bot) -> None:
    await bot.add_cog(WeatherCommands(bot))
