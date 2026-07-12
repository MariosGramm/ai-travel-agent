from enum import StrEnum

class ChatRole(StrEnum):
    """
    Enum representing the role of a participant in a chat session.
    """
    USER = "user"
    ASSISTANT = "assistant"

class SearchSessionStatus(StrEnum):
    """
    Enum representing the status of a search session.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStep(StrEnum):
    """
    Enum representing the steps of the AI travel agent's process.
    """
    RAG_RETRIEVAL  = "rag_retrieval"
    WEATHER_FETCH  = "weather_fetch"
    PLACES_FETCH   = "places_fetch"
    FLIGHTS_FETCH  = "flights_fetch"   
    LLM_GENERATION = "llm_generation"