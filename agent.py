# This is a basic agent that uses Mistral AI to answer weather questions.
# This agent is designed to be piped every single message in a Discord server.
# First, the agent checks for a location in the message, and extracts it if it exists.
# This prevents the agent from responding to messages that don't ask about weather.
# Then, a separate prompt chain is used to get the weather data and response.

import os
import json
import logging
import discord

from mistralai import Mistral
from tools.weather import seven_day_forecast

logger = logging.getLogger("discord")

MISTRAL_MODEL = "mistral-large-latest"

EXTRACT_LOCATION_PROMPT = """
Is this message explicitly requesting weather information for a specific city/location?
If not, return {"location": "none"}.

Otherwise, return the full name of the city in JSON format.

Example:
Message: What's the weather in sf?
Response: {"location": "San Francisco, CA"}

Message: What's the temperature in nyc?
Response: {"location": "New York City, NY"}

Message: Is it raining in sf?
Response: {"location": "San Francisco, CA"}

Message: I love the weather in SF
Response: {"location": "none"}
"""

TOOLS_PROMPT = """
You are a helpful weather assistant.
Given a location and a user's request, use your tools to fulfill the request.
Only use tools if needed. If you use a tool, make sure the longitude is correctly negative or positive
Provide a short, concise answer that uses emojis.
"""


class WeatherAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "seven_day_forecast",
                    "description": "Get the seven day forecast for a given location with latitude and longitude.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "string"},
                            "longitude": {"type": "string"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                },
            }
        ]
        self.tools_to_functions = {
            "seven_day_forecast": seven_day_forecast,
        }

    async def extract_location(self, message: str) -> dict:
        # Extract the location from the message.
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": EXTRACT_LOCATION_PROMPT},
                {"role": "user", "content": f"Discord message: {message}\nOutput:"},
            ],
            response_format={"type": "json_object"},
        )

        message = response.choices[0].message.content

        obj = json.loads(message)
        if obj["location"] == "none":
            return None

        return obj["location"]

    async def get_weather_with_tools(self, location: str, request: str):
        messages = [
            {"role": "system", "content": TOOLS_PROMPT},
            {
                "role": "user",
                "content": f"Location: {location}\nRequest: {request}\nOutput:",
            },
        ]

        # Require the agent to use a tool with the "any" tool choice.
        tool_response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
            tools=self.tools,
            tool_choice="any",
        )

        messages.append(tool_response.choices[0].message)

        tool_call = tool_response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments)
        function_result = self.tools_to_functions[function_name](**function_params)

        # Append the tool call and its result to the messages.
        messages.append(
            {
                "role": "tool",
                "name": function_name,
                "content": function_result,
                "tool_call_id": tool_call.id,
            }
        )

        # Run the model again with the tool call and its result.
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content

    async def run(self, message: discord.Message):
        # Extract the location from the message to verify that the user is asking about weather in a specific location.
        location = await self.extract_location(message.content)
        if location is None:
            return None

        # Send a message to the user that we are fetching weather data.
        res_message = await message.reply(f"Fetching weather for {location}...")

        # Use a second prompt chain to get the weather data and response.
        weather_response = await self.get_weather_with_tools(location, message.content)

        # Edit the message to show the weather data.
        await res_message.edit(content=weather_response)
