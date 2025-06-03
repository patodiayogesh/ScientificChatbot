import logging
import json
from abc import ABC, abstractmethod
from google import genai
from opik import track
from opik.integrations.genai import track_genai

from app.settings import get_settings
from app.services.tool import Tool

settings = get_settings()
logger = logging.getLogger(__name__)

class AbstractAgent(ABC):

    def __init__(self, name: str,
                 description: str,
                 model_name: str,
                 prompt: dict = None,
                 ):
        self.name = name
        self.description = description
        self.prompt_messages = []
        self.model_name = model_name

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the agent's main functionality.
        This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def load_prompt(self):
        """
        Load the prompt for the agent.
        This method should be implemented by subclasses.
        """
        pass


class Agent(AbstractAgent):

    def __init__(self, name: str,
                 description: str,
                 model_name: str,
                 prompt: dict,
                 tools: dict[str: Tool] = None,
                 ):
        super().__init__(name, description, model_name)
        self.client = track_genai(genai.Client(api_key=settings.API_KEY))
        self.tools = tools
        self.load_prompt(prompt)
        self.context = "Message History: "

    def load_prompt(self, prompt: dict):
        if not prompt:
            raise ValueError("Prompt cannot be None or empty.")
        try:
            for prompt_key, prompt_value in prompt.items():
                self.prompt_messages.append(
                    f"{prompt_key.title()}: {prompt_value}"
                )
        except Exception as e:
            raise ValueError(f"Error loading prompt: {e}")

        if self.tools:
            self.tools_message = "Tools: " + json.dumps([tool.to_dict() for tool in self.tools.values()],
                                                        indent=2, ensure_ascii=False)
        else:
            self.tools_message = "Tools: None"

    def invoke(self, query: str, context: str = None):
        """
        Invoke the agent with a query and optional context.
        """
        logger.info("Sending query, context, and tools to the model.")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[self.prompt_messages, query, context, self.tools_message],
                config = {
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "thought": {"type": "string"},
                        "tool": {"type": "string", "nullable": True},
                        "args": {"type": "object", "nullable": True},
                        "response": {"type": "string", "nullable": True},
                    }
                }
            )
            return response if response.content else None
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise ValueError(f"Error invoking agent: {e}")

    def invoke_tool(self, llm_response: str):
        """
        Invoke a tool based on the LLM response.
        This method checks if the LLM response contains a tool invocation and executes it.
        """
        try:
            response_data = json.loads(llm_response)
            if isinstance(response_data, dict) and "tool_to_use" in response_data:
                tool_name = response_data["tool"]
                tool_args = response_data.get("args", {})
                tool_to_run = self.tools.get(tool_name.lower())
                if not tool_to_run:
                    return f"Tool '{tool_name}' not found in available tools."
                return tool_to_run.execute(**tool_args)
            else:
                return llm_response  # No tool invocation, return the LLM's answer
        except Exception as e:
            logger.error(f"Error invoking tool: {e}")
            raise ValueError(f"Error invoking tool: {e}")

    @track("agent.execute")
    def execute(self, query: str, context: str = "None"):
        """
        LLM decides whether to use a tool. The LLM is prompted with the query and available tools.
        If the LLM response contains a tool invocation, run the tool and return its result.
        Otherwise, return the LLM's answer.
        """
        logger.info(f"Executing agent: {self.name}")
        logger.info(f"Query: {query}")
        logger.info(f"Context: {context}")
        logger.info(f"Prompt Messages: {self.prompt_messages}")
        logger.info(f"Tools Messages: {self.tools_message}")
        llm_response = self.invoke(query, context)
        if not llm_response:
            return "No response from the model."
        logger.info("LLM response received, checking for tool invocation.")
        llm_response = self.invoke_tool(llm_response)
        if type(llm_response) == str:
            self.context += llm_response
        return llm_response



