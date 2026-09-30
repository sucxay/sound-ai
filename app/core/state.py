from enum import Enum


class AssistantState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"

    def __str__(self) -> str:
        return self.value
