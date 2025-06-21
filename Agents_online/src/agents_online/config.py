from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import dotenv
dotenv.load_dotenv()


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """

    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="coachak-chatbot",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Pinecone Configuration ---
    PINECONE_API_KEY: str = Field(
        description="API key for Pinecone vector database service."
    )
    PINECONE_NAMESPACE: str | None = Field(
        description="Pinecone namspace."
    )
    PINECONE_INDEX_NAME: str = Field(
        default="coachak",
        description="Name of the Pinecone index for fitness knowledge base.",
    )
    PINECONE_ENVIRONMENT: str | None = Field(
        default=None,
        description="Pinecone environment (deprecated in newer versions).",
    )


    # --- Google AI (Gemini) Configuration ---
    GEMINI_API_KEY: str | None = Field(
        default=os.getenv("GEMINI_API_KEY"),
        description="API key for Google AI services (Gemini models)."
    )
    GEMINI_MODEL_ID: str = Field(
        default="gemini-2.0-flash",
        description="Identifier for the Gemini model to be used for summarization.",
    )

    # --- OpenRouter Configuration ---
    OPENROUTER_MODEL_ID: str | None = Field(
        default="deepseek/deepseek-r1-0528:free",
        description="Deepseek model name."
    )
    OPENROUTER_API_KEY: str | None = Field(
        default=None,
        description="API key for OpenRouter service (DeepSeek and other models)."
    )
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API endpoints.",
    )
    DEEPSEEK_MODEL_ID: str = Field(
        default="deepseek/deepseek-r1-0528:free",
        description="Identifier for the DeepSeek model via OpenRouter.",
    )
    OPENROUTER_SITE_URL: str | None = Field(
        default=None,
        description="Optional site URL for OpenRouter rankings.",
    )
    OPENROUTER_SITE_NAME: str | None = Field(
        default=None,
        description="Optional site name for OpenRouter rankings.",
    )

    GROQ_API_KEY: str | None = Field(
        default=os.getenv("GROQ_API_KEY"),
        description="Groq for tool calling agent.",
    )

    # --- Application Settings ---
    MAX_AGENT_STEPS: int = Field(
        default=10,
        description="Maximum number of steps the agent can take to complete a task.",
    )
    AGENT_VERBOSITY_LEVEL: int = Field(
        default=2,
        description="Verbosity level for agent logging (0=silent, 1=normal, 2=verbose).",
    )
    
    # --- Summarization Settings ---
    USE_MULTIPLE_SUMMARIZERS: bool = Field(
        default=True,
        description="Whether to initialize multiple summarizers for redundancy.",
    )
    PRIMARY_SUMMARIZER: str = Field(
        default="deepseek", # gemini
        description="Primary summarizer to use. Options: 'gemini', 'deepseek'",
    )
    SUMMARY_MAX_LENGTH: int = Field(
        default=1024,
        description="Maximum character length for summaries.",
    )
    
    # --- Safety Settings ---
    ENABLE_MEDICAL_DETECTION: bool = Field(
        default=True,
        description="Enable detection and warning for potential medical queries.",
    )
    MEDICAL_KEYWORDS: list[str] = Field(
        default_factory=lambda: [
            "diagnose", "prescription", "medical condition", 
            "disease", "symptom", "medication", "treatment"
        ],
        description="Keywords that trigger medical query warnings.",
    )

    # --- Tool Configuration ---
    ENABLE_WORKOUT_GENERATOR: bool = Field(
        default=True,
        description="Enable the workout plan generator tool.",
    )
    ENABLE_NUTRITION_CALCULATOR: bool = Field(
        default=True,
        description="Enable the nutrition calculator tool.",
    )
    ENABLE_SAFETY_VALIDATOR: bool = Field(
        default=True,
        description="Enable the exercise safety validator tool.",
    )


    # --- Validators ---
    @field_validator("PINECONE_API_KEY")
    @classmethod
    def check_required_not_empty(cls, value: str, info) -> str:
        """Validate that required API keys are not empty."""
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} is required and cannot be empty.")
            raise ValueError(f"{info.field_name} is required and cannot be empty.")
        return value

    # @field_validator("GEMINI_API_KEY", "OPENROUTER_API_KEY")
    # @classmethod
    # def check_at_least_one_summarizer(cls, value: str | None, info) -> str | None:
    #     """Ensure at least one summarizer API key is provided."""
    #     # This is checked after all fields are validated
    #     return value

    @field_validator("PRIMARY_SUMMARIZER")
    @classmethod
    def validate_primary_summarizer(cls, value: str) -> str:
        """Validate primary summarizer choice."""
        valid_options = ["gemini", "deepseek"]
        if value.lower() not in valid_options:
            raise ValueError(f"PRIMARY_SUMMARIZER must be one of {valid_options}")
        return value.lower()

    def model_post_init(self, __context) -> None:
        """Post-initialization validation."""
        # Check that at least one summarizer is configured
        if not self.GEMINI_API_KEY and not self.OPENROUTER_API_KEY:
            logger.warning(
                "No summarizer API keys found. At least one of GEMINI_API_KEY "
                "or OPENROUTER_API_KEY should be provided for summarization features."
            )
        
        
        # Log configuration summary
        logger.info("=" * 50)
        logger.info("FITNESS AI ASSISTANT CONFIGURATION")
        logger.info("=" * 50)
        logger.info(f"Pinecone Index: {self.PINECONE_INDEX_NAME}")
        
        if self.GEMINI_API_KEY:
            logger.info(f"✓ Gemini Model: {self.GEMINI_MODEL_ID}")
        else:
            logger.info("✗ Gemini: Not configured")
            
        if self.OPENROUTER_API_KEY:
            logger.info(f"✓ DeepSeek Model: {self.DEEPSEEK_MODEL_ID}")
        else:
            logger.info("✗ DeepSeek: Not configured")
            
        logger.info(f"Primary Summarizer: {self.PRIMARY_SUMMARIZER}")
        logger.info("=" * 50)


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)