from typing import Any
import asyncio

from langchain_community.tools import WikipediaQueryRun  # noqa: F811
from langchain_community.utilities import WikipediaAPIWrapper  # noqa: F811
from beeai_framework.agents.react import ReActAgent, ReActAgentRunOutput
from beeai_framework.backend import ChatModel
from beeai_framework.emitter import Emitter, EmitterOptions, EventMeta
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.tools import Tool, tool


@tool
def langchain_wikipedia_tool(query: str) -> str:
    """
    Search factual and historical information, including biography, history, politics, geography, society, culture,
    science, technology, people, animal species, mathematics, and other subjects.

    Args:
        query: The topic or question to search for on Wikipedia.

    Returns:
        The information found via searching Wikipedia.
    """
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query)


# Construct ChatModel
chat_model: ChatModel = ChatModel.from_name("ollama:granite3.3:8b")

# Construct Agent instance with the chat model
agent = ReActAgent(
    llm=chat_model, tools=[langchain_wikipedia_tool], memory=UnconstrainedMemory()
)


async def process_agent_events(event_data: Any, event_meta: EventMeta) -> None:
    """Process agent events and log appropriately"""

    if event_meta.name == "error":
        print("Agent 🤖 : ", event_data)
    elif event_meta.name == "retry":
        print("Agent 🤖 : ", "retrying the action...")
    elif event_meta.name == "update":
        print(f"Agent({event_data.update.key}) 🤖 : ", event_data.update.parsed_value)


# Observe the agent
async def observer(emitter: Emitter) -> None:
    emitter.on("*.*", process_agent_events, EmitterOptions(match_nested=True))


async def main():
    # Run the agent
    result: ReActAgentRunOutput = await agent.run(
        "How is the current president of Colombia?"
    ).observe(observer)


asyncio.run(main())
