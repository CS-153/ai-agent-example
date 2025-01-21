from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import os
import httpx

WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast?current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
USER_AGENT = "weather-app/1.0"


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


class WeatherAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model_name="mistral-small-latest",
            temperature=0.3,
        )
        self.tools = [get_weather_tool]
        self.agent = create_react_agent(self.llm, tools=self.tools)

    def run(self, message: str):
        system_message = """Given the following Discord message, determine if the user is SPECIFICALLY requesting weather information for a SPECIFIC city. If they are, extract the location mentioned and fetch the weather, then provide a detailed response to the user. Otherwise, return 'none'. Only use a tool if needed. Don't respond to the user unless they ask for weather information.
        """

        final_state = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": f"Discord message: {message}\nOutput:",
                    },
                ],
            },
        )

        if final_state["messages"][-1].content == "none":
            print("User did not request weather information.")
            return None

        return final_state["messages"][-1].content


def make_weather_request(url: str):
    print(f"Making weather request to {url}")
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}

    try:
        response = httpx.Client().get(url, headers=headers, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


@tool
def get_weather_tool(latitude: str, longitude: str):
    """Get the weather for a given location with latitude and longitude."""
    print(f"Getting weather for {latitude}, {longitude}")
    url = f"{WEATHER_API_BASE}&latitude={latitude}&longitude={longitude}"
    return make_weather_request(url)
