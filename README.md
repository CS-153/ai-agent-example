# CS 153 - Infrastructure at Scale: Weather Agent Example Code

This is an example final project for the class. Use this as a reference for what we are looking for in a final project.

## Weather Agent

This Discord bot listens for messages requesting information about the weather in a specific location (i.e. "What's the weather in SF?" or "Is it raining right now in NYC?") and responds to their prompt with accurate weather information.

This is achieved through use of a _weather tool_ which gives the agent access to real-time weather data. Your projects will probably incorporate a tool of some sort as well to enhance the abilities of your agent.

## What is an Agent?

An LLM turns into an Agent when it is given the ability to take actions on the user's behalf. In this case, the action was looking up weather data. Other examples of actions are adding an event to your calendar, scraping a website, or sending an email. This is the beauty of Agents: there's infinite actions out there yet to be explored.

## What are tools?

An Agent accomplishes its task using _tools_, which are Python functions that the agent can call to obtain certain information or take certain actions. In this case, the Weather Agent uses the `seven_day_forecast(long, lat)` function in `/tools/weather.py` to fetch weather data for a specific location.

See more on [function calling](https://docs.mistral.ai/capabilities/function_calling/) in Mistral's documentation.

## Weather Agent Structure

This project uses two separate LLM conversations to achieve its task.

### Task 1

To act as a passive observer of the channel, the first task is to check if a message explicitly requests weather information for a specific city. While this could be combined with the second task, separating the two is a design decision to allow the agent to fully focus on one single task at a time.

Task one is defined by `EXTRACT_LOCATION_PROMPT` in `agent.py`.

If no weather request is extracted from the message, which will likely be the case most of the time, the bot will not respond.

Otherwise, the bot extracts the location and continues to task 2.

### Task 2

Once the location is extracted, task 2 provides the agent with the `seven_day_forecast(long, lat)` tool to fetch weather information for a specific longitude and latitude. The LLM is great at providing the longitude and latitude itself given a location, so it's able to call the function directly.

The function is then called, and its response is piped back into the LLM.

Finally, the LLM replies with its final response, the message that will be sent to the user that answers their weather question.
