from beeai_framework.agents.react import ReActAgent
from beeai_framework.backend import ChatModel
from beeai_framework.tools import AnyTool
from beeai_framework.memory import UnconstrainedMemory
from typing import Any
from src.tools.pnl_validator import ValidatorPNLTool
from beeai_framework.template import PromptTemplateInput
from pydantic import BaseModel

def create_auditor_agent() -> ReActAgent:
    """
    Creates a ReAct agent configured to perform professional financial audits.
    
    Returns:
        ReActAgent: Configured agent with financial auditing capabilities
    """
    # Initialize the model
    llm = ChatModel.from_name("ollama:granite3.3:8b")
    # Register our custom tool
    tools: list[AnyTool] = [ ]
    
    # Create and configure the ReAct agent
    agent = ReActAgent(
        llm=llm,
        tools=tools,
        memory=UnconstrainedMemory()
    )
    
    return agent
