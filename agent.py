# This is a basic ReAct agent that uses Mistral AI to answer weather questions.
# A ReAct agent decides once its thinking is complete, and can use tools to get more information.
#
# It is designed to be piped every single message in a Discord server.
# If a message asks about the weather in a specific location, it can use the seven_day_forecast tool to fetch the weather.
# Check out the LangGraph documentation to explore building even more complex agents.

import os
import logging

from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from tools.weather import seven_day_forecast

logger = logging.getLogger("discord")

SYSTEM_MESSAGE = """
You are a helpful weather assistant viewing every message in a Discord server. Given a message, do the following:
1. Determine if the user is requesting weather information for a city.
2. If not, return only 'none'. If they do not explicitly ask for weather information, return only 'none'.
3. If they are, extract the location mentioned and fetch the weather, then provide a concise response to the user that answers their question.
4. Only use a tool if needed. Only use the necessary data from the tool to answer the user's question, not everything.
5. Use markdown and emojis to make your response more engaging.
6. Don't respond to the user unless they ask for weather information.
"""


class WeatherAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model_name="ministral-8b-latest",
            temperature=0.1,
        )
        self.tools = [seven_day_forecast]
        # Use ReAct agent template to create the agent
        self.agent = create_react_agent(self.llm, tools=self.tools)

    def run(self, message: str):
        final_state = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_MESSAGE,
                    },
                    {
                        "role": "user",
                        "content": f"Discord message: {message}\nOutput:",
                    },
                ],
            },
        )

        # The model returns "none" if the user's message does not contain weather information.
        if final_state["messages"][-1].content == "none":
            logger.info("User did not request weather information.")
            return None

        return final_state["messages"][-1].content
