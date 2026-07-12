from enum import StrEnum

class ChatRole(StrEnum):
    """
    Enum representing the role of a participant in a chat session.
    """
    USER = "user"
    ASSISTANT = "assistant"