from enum import Enum, auto


class KentState(Enum):
    IDLE = auto()
    WALKING = auto()
    SLEEPING = auto()
    WAKING = auto()
    LISTENING = auto()
    THINKING = auto()
    OBSERVING = auto()
    RESPONDING = auto()
    ERROR = auto()
