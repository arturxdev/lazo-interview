from beeai_framework.adapters.anthropic import AnthropicChatModel
from beeai_framework.backend import ChatModel
from beeai_framework.backend import UserMessage
class Model:
    def __init__(self, is_production: str = "False"):
        print(f"🔍 Initializing model in production: {is_production}")
        self.model = AnthropicChatModel() if is_production == "True" else ChatModel.from_name("ollama:granite3.3:8b")
    def get_model(self):
        return self.model.provider_id
    
    def create(self, prompt: str):
        return self.model.create(messages=[UserMessage(prompt)])