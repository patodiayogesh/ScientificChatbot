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
        if self.tools:
            self.tools_message = "Available Tools: " + json.dumps([tool.to_dict() for tool in self.tools.values()],
                                                        indent=2, ensure_ascii=False)
        else:
            self.tools_message = "Available Tools: None"
        self.context = "Message History: "

    def __repr__(self):
        return f"Agent(name={self.name}, description={self.description}, model_name={self.model_name})"

    def to_dict(self):
        """
        Convert the agent to a dictionary representation.
        """
        return {
            "name": self.name,
            "description": self.description,
            "model_name": self.model_name,
        }

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

    @track("agent.invoke")
    def invoke(self, query: str, context: str = None):
        """
        Invoke the agent with a query and optional context.
        """
        logger.info("Sending query, context, and tools to the model.")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[self.prompt_messages, query, self.tools_message, context],
            )
            if not response or not response.candidates:
                logger.error("No response from the model.")
                return None
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise ValueError(f"Error invoking agent: {e}")
        try:
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            logger.error(f"Error processing model response: {e}")
            raise ValueError(f"Error processing model response: {e}")

    def load_json_from_model_response(self, llm_response: str):
        """
        Load JSON data from the LLM response.
        This method attempts to parse the LLM response as JSON.
        """
        try:
            return json.loads(llm_response)
        except Exception as e:
            logger.error(f"Error decoding json string: {e}")
            if llm_response.startswith("```json"):
                llm_response = llm_response[7:-3]
                return json.loads(llm_response)
            if llm_response.startswith("```"):
                llm_response = llm_response[3:-3]
                return json.loads(llm_response)


    @track("agent.invoke_tool")
    def invoke_tool(self, response_data: str):
        """
        Invoke a tool based on the LLM response.
        This method checks if the LLM response contains a tool invocation and executes it.
        """
        try:
            if isinstance(response_data, dict) and "tool" in response_data:
                tool_name = response_data["tool"]
                tool_args = response_data.get("args", {})
                tool_to_run = self.tools.get(tool_name.lower())
                if not tool_to_run:
                    return f"Tool '{tool_name}' not found in available tools."
                logger.info(f"Invoking tool: {tool_name} with args: {tool_args}")
                return f"Tool Output: {tool_to_run.execute(**tool_args)}"
            else:
                return ""
        except Exception as e:
            logger.error(f"Error invoking tool: {e}")
            raise ValueError(f"Error invoking tool: {e}")

    @track("agent.invoke_code")
    def invoke_code(self, response_data: str):
        """
        Execute code using the GenAI client.
        This method is a placeholder for executing code snippets.
        """
        try:
            logger.info(f"Invoking code execution with response data")
            if "code_snippet" in response_data:
                code_snippet = response_data["code_snippet"]
                if code_snippet.startswith("```python"):
                    code_snippet = code_snippet[9:-3]
                elif code_snippet.startswith("```"):
                    code_snippet = code_snippet[3:-3]
                logger.info(f"Executing code snippet")
                local_vars = {}
                exec(code_snippet, {}, local_vars)
                code_output = local_vars["result"]
                return f"Code Output: {code_output}"
        except Exception as e:
            return f"Code Output: Error parsing/executing code snippet: {e}"

    @track("agent.execute_with_context")
    def execute_with_context(self, query:str):
        """
        Execute the agent with a query and optional context.
        This method is a wrapper around the execute method to handle context.
        """

        llm_response = self.invoke(query, context=self.context)
        if not llm_response:
            return "No response from the model."
        if isinstance(llm_response, str):
            self.context += f"AI Response: {llm_response}\n"
        logger.info("LLM response received, checking for tool invocation.")
        llm_response_json = self.load_json_from_model_response(llm_response)
        tool_output = self.invoke_tool(llm_response_json)
        if tool_output and isinstance(tool_output, str):
            self.context += f"{tool_output}\n"
        code_output = self.invoke_code(llm_response_json)
        if code_output and isinstance(code_output, str):
            self.context += f"{code_output}\n"
        return llm_response_json


    @track("agent.execute")
    def execute(self, query: str, MAX_LOOPS: int = 3):
        """
        LLM decides whether to use a tool. The LLM is prompted with the query and available tools.
        If the LLM response contains a tool invocation, run the tool and return its result.
        Otherwise, return the LLM's answer.
        """
        logger.info(f"Executing agent: {self.name}")
        query = "Query: " + query
        while(MAX_LOOPS>0):
            llm_response_json = self.execute_with_context(query)
            try:
                if llm_response_json["no_further_operations"] == True or llm_response_json[
                    "no_further_operations"] == "true":
                    logger.info("No further operations requested by the LLM.")
                    break
            except Exception as e:
                logger.error("no_further_operations not found in LLM response, continuing execution.")
                self.context += "User Message: Error checking for no_further_operations in LLM response.\n"
            MAX_LOOPS -= 1

        if "response" not in llm_response_json:
            logger.error("No response found in LLM response.")
            return "No response generated by the agent."
        return llm_response_json["response"]


class SuperAgent(Agent):
    """
    A SuperAgent that can manage multiple agents and delegate tasks to them.
    This class is a placeholder for future implementation.
    """

    def __init__(self,
                 name: str,
                 description: str,
                 model_name: str,
                 prompt: dict = None,
                 agents: dict[str: Agent] = None
                 ):
        super().__init__(name, description, model_name, prompt)
        self.tools = agents
        if self.tools:
            self.tools_message = "Available Agents: " + json.dumps([tool.to_dict() for tool in self.tools.values()],
                                                                   indent=2, ensure_ascii=False)
        else:
            self.tools_message = "Available Agents: None"


    @track("super_agent.invoke_agent")
    def invoke_agent(self, llm_response: str, query: str, previous_agent_response: str):
        """
        Invoke a tool based on the LLM response.
        This method checks if the LLM response contains a tool invocation and executes it.
        """
        try:
            if isinstance(llm_response, dict) and "agent" in llm_response:
                agent_name = llm_response["agent"]
                agent_to_run = self.tools.get(agent_name.lower())
                agent_to_run.context += f"Previous Agent Response: {previous_agent_response}\n"
                if not agent_to_run:
                    return f"Agent '{agent_name}' not found in available agents."
                logger.info(f"Invoking agent: {agent_name}")
                return f"Agent Response: {agent_to_run.execute(query)}"
            else:
                return ""
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise ValueError(f"Error invoking agent: {e}")

    @track("super_agent.execute_with_context")
    def execute_with_context(self, query:str, previous_agent_response: str = ""):
        """
        Execute the SuperAgent with a query and optional context.
        This method is a wrapper around the execute method to handle context.
        """
        llm_response = self.invoke(query, context=self.context)
        if not llm_response:
            return "No response from the model."
        if isinstance(llm_response, str):
            self.context += f"AI Response: {llm_response}\n"
        logger.info("LLM response received, checking for agent invocation.")
        llm_response_json = self.load_json_from_model_response(llm_response)
        agent_output = self.invoke_agent(llm_response_json, query, previous_agent_response)
        if agent_output and isinstance(agent_output, str):
            self.context += f"Agent Response: {agent_output}\n"
        return llm_response_json, agent_output

    @track("super_agent.execute")
    def execute(self, query: str, MAX_LOOPS: int = 3):
        """
        Execute the SuperAgent with a query and optional context.
        This method is a wrapper around the execute method to handle context.
        """
        logger.info(f"Executing super agent: {self.name}")
        query = "Query: " + query
        agent_output = ""
        while(MAX_LOOPS>0):
            llm_response_json, agent_output = self.execute_with_context(query, agent_output)
            try:
                if llm_response_json["no_further_operations"] == True or llm_response_json[
                    "no_further_operations"] == "true":
                    logger.info("No further operations requested by the LLM.")
                    break
            except Exception as e:
                logger.error("no_further_operations not found in LLM response, continuing execution.")
                self.context += "User Message: Error checking for no_further_operations in LLM response.\n"
            MAX_LOOPS -= 1

        if "response" not in llm_response_json:
            logger.error("No response found in LLM response.")
            return "No response generated by the agent."
        return llm_response_json["response"]
