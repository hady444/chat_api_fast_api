from pathlib import Path
from typing import Any
import os

import opik
from loguru import logger
from opik import opik_context
from smolagents import LiteLLMModel, MessageRole, MultiStepAgent, ToolCallingAgent

from second_brain_online.config import settings

from .tools import (
    PineconeRetrieverTool,
    GeminiSummarizerTool,
    DeepSeekSummarizerTool,
    WorkoutPlanGeneratorTool,
    NutritionCalculatorTool,
    ExerciseSafetyValidatorTool,
    what_can_i_do,
)


def get_agent(retriever_config_path: Path) -> "AgentWrapper":
    # Validate the config file exists
    if not retriever_config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {retriever_config_path}")
    
    # Validate required environment variables
    required_env_vars = {
        "OPENROUTER_API_KEY": "Deepseek API key for agent brain",
        "PINECONE_API_KEY": "Pinecone API key for vector search",
    }
    
    missing_required = []
    for var, description in required_env_vars.items():
        if not os.getenv(var) and not getattr(settings, var, None):
            missing_required.append(f"{var} ({description})")
    if missing_required:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_required)}")
    print(retriever_config_path)
    agent = AgentWrapper.build_from_smolagents(
        retriever_config_path=retriever_config_path
    )
    
    return agent


class AgentWrapper:
    def __init__(self, agent: MultiStepAgent) -> None:
        self.__agent = agent

    @property
    def input_messages(self) -> list[dict]:
        return self.__agent.input_messages

    @property
    def agent_name(self) -> str:
        return self.__agent.agent_name

    @property
    def max_steps(self) -> str:
        return self.__agent.max_steps

    @classmethod
    def build_from_smolagents(cls, retriever_config_path: Path) -> "AgentWrapper":
        # Initialize core tools
        retriever_tool = PineconeRetrieverTool(config_path=retriever_config_path)
    
        # Initialize summarizers
        summarizers = []
        try:
            gemini_summarizer = GeminiSummarizerTool()
            summarizers.append(gemini_summarizer)
        except Exception as e:
            logger.warning(f"Gemini summarizer unavailable: {e}")
        
        try:
            deepseek_summarizer = DeepSeekSummarizerTool()
            summarizers.append(deepseek_summarizer)
        except Exception as e:
            logger.warning(f"DeepSeek summarizer unavailable: {e}")
        print("Here 7")
        # Initialize fitness-specific tools
        workout_generator = WorkoutPlanGeneratorTool()
        nutrition_calculator = NutritionCalculatorTool()
        safety_validator = ExerciseSafetyValidatorTool()
        # Create comprehensive tool list
        tools = [
            what_can_i_do,
            retriever_tool,
            workout_generator,
            nutrition_calculator,
            safety_validator
        ] + summarizers
        # Enhanced system prompt
        system_prompt = """You are a comprehensive fitness and health assistant equipped with specialized tools. 

        Your capabilities include:
        1. **Information Retrieval**: Search fitness, muscle-building, fat loss, nutrition, supplements, recovery, njury and lifestyle knowledge base for evidence-based information
        2. **Workout Planning**: Generate personalized workout plans based on goals and experience
        3. **Nutrition Calculation**: Calculate caloric needs and macro splits
        4. **Safety Validation**: Check exercise safety based on user conditions
        5. **Summarization**: Provide concise summaries of complex information

        You only have access to these tools:
        {{tool_descriptions}}

        {{managed_agents_descriptions}}

        IMPORTANT WORKFLOW RULES:
        1. **ALWAYS use a two-step process for information queries**:
        - FIRST: Use pinecone_vector_search_retriever to find relevant documents
        - THEN: Use either gemini_summarizer or deepseek_summarizer to make the retrieved content user-friendly and/or to fill knowledge gaps if retrieving fails or less informative
        
        2. **When using the retriever**:
        - The pinecone tool returns raw document chunks that may be technical or fragmented
        - NEVER present raw Pinecone results directly to the user
        - ALWAYS pass the retrieved documents to a summarizer for processing

        3. **Choosing a summarizer**:
        - Use gemini_summarizer for general fitness and nutrition topics
        - Use deepseek_summarizer for more scientific content
        - If one summarizer fails, try the other

        4. **Example workflow for information queries**:
        User: "How do I build muscle with bad knees?"
        Step 1: Use pinecone_vector_search_retriever with query "knee-friendly muscle building exercises"
        Step 2: Pass the retrieved documents to gemini_summarizer with the original user question
        Step 3: Present the summarized, user-friendly response

        5. **For other queries**:
        - Always use safety_validator when users mention injuries or conditions
        - Calculate nutrition needs before suggesting meal plans
        - Generate workout plans that match user's experience level

        6. **Don't do**:
        - Don't let user see external links in the response.
        - If you find any external links in the retrieved documents, do not include them in the final response.
        - Don't present raw Pinecone results directly to the user
        - Don't provide medical advice or diagnoses - always include disclaimers
        - Don't answer to anything outside the scope above and prompt the user to rephrase or ask a different question


        REMEMBER:
        - You are NOT a medical professional - always include disclaimers
        - Raw Pinecone results are for YOUR use only - always summarize before presenting and make it user-friendly
        - The summarizers will fill knowledge gaps and make content accessible
        - Encourage users to consult certified professionals for personalized guidance

    """

        model = LiteLLMModel(
            model_id="groq/meta-llama/llama-4-scout-17b-16e-instruct",
            #api_base=settings.OPENROUTER_BASE_URL,
            api_key=settings.GROQ_API_KEY,
        )
        print("Here 11")
        agent = ToolCallingAgent(
            tools=tools,
            model=model,
            max_steps=5,
            verbosity_level=2,
            system_prompt=system_prompt
        )
        print("Here 12")
        
        return cls(agent)

    @opik.track(name="Agent.run")
    def run(self, task: str, **kwargs) -> Any:
        # Add safety check for medical questions
        medical_keywords = ["diagnose", "prescription", "medical condition", "disease", "symptom"]
        if any(keyword in task.lower() for keyword in medical_keywords):
            logger.warning(f"Potential medical query detected: {task}")
        
        result = self.__agent.run(task, **kwargs)

        model = self.__agent.model
        metadata = {
            "system_prompt": self.__agent.system_prompt,
            "system_prompt_template": self.__agent.system_prompt_template,
            "tool_description_template": self.__agent.tool_description_template,
            "tools": self.__agent.tools,
            "model_id": self.__agent.model.model_id,
            "api_base": self.__agent.model.api_base,
            "input_token_count": model.last_input_token_count,
            "output_token_count": model.last_output_token_count,
        }
        if hasattr(self.__agent, "step_number"):
            metadata["step_number"] = self.__agent.step_number
        opik_context.update_current_trace(
            tags=["agent"],
            metadata=metadata,
        )

        return result

def extract_tool_responses(agent: ToolCallingAgent) -> str:
    """
    Extracts and concatenates all tool response contents with numbered observation delimiters.

    Args:
        input_messages (List[Dict]): List of message dictionaries containing 'role' and 'content' keys

    Returns:
        str: Tool response contents separated by numbered observation delimiters

    Example:
        >>> messages = [
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "First response"},
        ...     {"role": MessageRole.USER, "content": "Question"},
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "Second response"}
        ... ]
        >>> extract_tool_responses(messages)
        "-------- OBSERVATION 1 --------\nFirst response\n-------- OBSERVATION 2 --------\nSecond response"
    """

    tool_responses = [
        msg["content"]
        for msg in agent.input_messages
        if msg["role"] == MessageRole.TOOL_RESPONSE
    ]

    return "\n".join(
        f"-------- OBSERVATION {i + 1} --------\n{response}"
        for i, response in enumerate(tool_responses)
    )


class OpikAgentMonitorCallback:
    def __init__(self) -> None:
        self.output_state: dict = {}

    def __call__(self, step_log) -> None:
        input_state = {
            "agent_memory": step_log.agent_memory,
            "tool_calls": step_log.tool_calls,
        }
        self.output_state = {"observations": step_log.observations}

        self.trace(input_state)

    @opik.track(name="Callback.agent_step")
    def trace(self, step_log) -> dict:
        return self.output_state