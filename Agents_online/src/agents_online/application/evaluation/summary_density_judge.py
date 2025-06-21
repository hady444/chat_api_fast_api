import json
from typing import Any

from opik.evaluation.metrics import base_metric, exceptions, score_result
from openai import OpenAI
from pydantic import BaseModel

from second_brain_online.config import settings


class LLMJudgeStyleOutputResult(BaseModel):
    score: int
    reason: str


class SummaryDensityJudge(base_metric.BaseMetric):
    """
    A metric that evaluates whether an LLM's output has appropriate length and density.

    This metric uses DeepSeek LLM to judge if the output length is appropriate for the given instruction.
    It returns a normalized score between 0 and 1, where:
    - 0.0 (Poor): Output is either too short and incomplete, or too long with unnecessary information
    - 0.5 (Good): Output has decent length balance but still slightly too short or too long
    - 1.0 (Excellent): Output length is appropriate, answering the question concisely without being verbose
    """

    def __init__(
        self,
        name: str = "summary_density_judge",
        model_name: str = None,
        api_key: str = None,
    ) -> None:
        self.name = name
        
        # Use DeepSeek via OpenRouter
        api_key = api_key or settings.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OpenRouter API key required for DeepSeek judge")
            
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=api_key
        )
        
        self.model_name = model_name or settings.DEEPSEEK_MODEL_ID
        
        self.prompt_template = """You are an impartial expert judge. Evaluate the quality of a given answer to an instruction based on how long the answer it is. 

How to decide whether the lengths of the answer is appropriate:
1 (Poor): Too short, does not answer the question OR too long, it contains too much noise and unrequired information, where the answer could be more concise.
2 (Good): Good length balance of the answer, but the answer is still too short OR too long.
3 (Excellent): The length of the answer is appropriate, it answers the question and is not too long or too short.

Example of bad answer that is too short: 
<answer>
LangChain, LlamaIndex, Haystack
</answer>

Example of bad answer that is too long:
<answer>
LangChain is a powerful and versatile framework designed specifically for building sophisticated LLM applications. It provides comprehensive abstractions for essential components like prompting, memory management, agent behaviors, and chain orchestration. The framework boasts an impressive ecosystem with extensive integrations across various tools and services, making it highly flexible for diverse use cases. However, this extensive functionality comes with a steeper learning curve that might require dedicated time to master.

LlamaIndex (which was formerly known as GPTIndex) has carved out a specialized niche in the LLM tooling landscape, focusing primarily on data ingestion and advanced indexing capabilities for Large Language Models. It offers a rich set of sophisticated mechanisms to structure and query your data, including vector stores for semantic similarity search, keyword indices for traditional text matching, and tree indices for hierarchical data organization. While it particularly shines in Retrieval-Augmented Generation (RAG) applications, its comprehensive feature set might be excessive for more straightforward implementation needs.

Haystack stands out as a robust end-to-end framework that places particular emphasis on question-answering systems and semantic search capabilities. It provides a comprehensive suite of document processing tools and comes equipped with production-ready pipelines that can be deployed with minimal configuration. The framework includes advanced features like multi-stage retrieval, document ranking, and reader-ranker architectures. While these capabilities make it powerful for complex information retrieval tasks, new users might find the initial configuration and architecture decisions somewhat challenging to navigate.

Each of these frameworks brings unique strengths to the table while sharing some overlapping functionality. The choice between them often depends on specific use cases, technical requirements, and team expertise. LangChain offers the broadest general-purpose toolkit, LlamaIndex excels in data handling and RAG, while Haystack provides the most streamlined experience for question-answering systems.
</answer>

Example of excellent answer that is appropriate:
<answer>
1. LangChain is a powerful framework for building LLM applications that provides abstractions for prompting, memory, agents, and chains. It has extensive integrations with various tools and services, making it highly flexible but potentially complex to learn. 
2. LlamaIndex specializes in data ingestion and indexing for LLMs, offering sophisticated ways to structure and query your data through vector stores, keyword indices, and tree indices. It excels at RAG applications but may be overkill for simpler use cases. 
3. Haystack is an end-to-end framework focused on question-answering and semantic search, with strong document processing capabilities and ready-to-use pipelines. While powerful, its learning curve can be steep for beginners. 
</answer>

Instruction: {input}

Answer: {output}

Provide your evaluation in valid JSON format with exactly this structure:
{{
    "score": <integer between 1 and 3>,
    "reason": "<explanation of your scoring decision>"
}}

Be objective and focus specifically on whether the length and density of the answer is appropriate for the question asked."""

    def score(self, input: str, output: str, **ignored_kwargs: Any):
        """
        Score the output of an LLM using DeepSeek as judge.

        Args:
            input: The original question/instruction
            output: The LLM output to evaluate
            **ignored_kwargs: Any additional keyword arguments
        """
        prompt = self.prompt_template.format(input=input, output=output)

        try:
            # Call DeepSeek via OpenRouter
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert judge evaluating text quality. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent judging
                max_tokens=256,
            )
            
            model_output = completion.choices[0].message.content.strip()
            return self._parse_model_output(model_output)
            
        except Exception as e:
            raise exceptions.MetricComputationError(f"Failed to get DeepSeek judgment: {str(e)}")

    def _parse_model_output(self, content: str) -> score_result.ScoreResult:
        try:
            # Clean up the response if needed
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            dict_content = json.loads(content.strip())
        except json.JSONDecodeError as e:
            raise exceptions.MetricComputationError(f"Failed to parse DeepSeek output as JSON: {e}\nOutput was: {content}")

        try:
            score = int(dict_content["score"])
            assert 1 <= score <= 3, f"Invalid score value: {score}"
        except (KeyError, ValueError, AssertionError) as e:
            raise exceptions.MetricComputationError(f"Invalid score format: {str(e)}")

        # Normalize the score to be between 0 and 1
        normalized_score = (score - 1) / 2.0

        return score_result.ScoreResult(
            name=self.name,
            value=normalized_score,
            reason=dict_content.get("reason", "No reason provided"),
        )