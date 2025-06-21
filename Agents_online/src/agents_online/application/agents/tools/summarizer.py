from smolagents import Tool
from opik import track
import google.generativeai as genai
import os
from openai import OpenAI


class GeminiSummarizerTool(Tool):
    name = "gemini_summarizer"
    description = """Use this tool to summarize a piece of text using Google's Gemini 2.0 Flash model."""

    inputs = {
        "text": {
            "type": "string",
            "description": "The text to summarize.",
        }
    }
    output_type = "string"

    SYSTEM_PROMPT = """You are a helpful assistant specialized in summarizing documents. 
Generate a concise TL;DR summary in markdown format, maximum 512 characters, highlighting the most significant insights from the following content:

{content}

Respond only with the summary.
"""

    def __init__(self, api_key: str = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # Configure API key
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google AI API key must be provided or set in GEMINI_API_KEY env var")
        
        genai.configure(api_key=api_key)
        
        # Initialize model with generation config
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
        )

    @track(name="GeminiSummarizerTool.forward")
    def forward(self, text: str) -> str:
        """Generate a summary of the provided text using Gemini 2.0 Flash."""
        try:
            if not text or not text.strip():
                return "Error: No text provided to summarize."
            
            prompt = self.SYSTEM_PROMPT.format(content=text)
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            if response.text:
                summary = response.text.strip()
                return summary
            else:
                return "Error: Unable to generate summary."
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
        


class DeepSeekSummarizerTool(Tool):
    name = "deepseek_summarizer"
    description = """Use this tool to summarize a piece of text using DeepSeek R1 model via OpenRouter."""

    inputs = {
        "text": {
            "type": "string",
            "description": "The text to summarize.",
        }
    }
    output_type = "string"

    SYSTEM_PROMPT = """You are a helpful assistant specialized in summarizing documents. 
Generate a concise TL;DR summary in markdown format, maximum 512 characters, highlighting the most significant insights from the following content:

{content}

Respond only with the summary.
"""

    def __init__(self, api_key: str = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # Configure API key
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key must be provided or set in OPENROUTER_API_KEY env var")
        
        # Initialize OpenRouter client for DeepSeek
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Store model configuration
        self.model_name = "deepseek/deepseek-r1-0528:free"
        self.generation_config = {
            "temperature": 0.3,
            "max_tokens": 4096,
        }

    @track(name="DeepSeekSummarizerTool.forward")
    def forward(self, text: str) -> str:
        """Generate a summary of the provided text using DeepSeek R1."""
        try:
            if not text or not text.strip():
                return "Error: No text provided to summarize."
            
            
            prompt = self.SYSTEM_PROMPT.format(content=text)
            
            # Generate summary
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specialized in creating concise summaries. Generate summaries in markdown format, maximum 512 characters."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                **self.generation_config
            )
            
            if completion.choices and completion.choices[0].message:
                summary = completion.choices[0].message.content.strip()
                return summary
            else:
                return "Error: Unable to generate summary from DeepSeek."
                
        except Exception as e:
            return f"Error generating summary with DeepSeek: {str(e)}"