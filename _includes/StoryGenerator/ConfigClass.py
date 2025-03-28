from dataclasses import dataclass
from pathlib import Path

@dataclass
class ChatConfig:
    system_prompt: str
    first_prompt: str
    user_prompt: str
    assistant_response: str
    model: dict
    temperature: float
    max_tokens: int
    history_path: Path
    print_messages: bool
    client_type: "str"
    include_reasoning: bool
    reasoning_header: str
    separator: str
    has_separator: bool
    interrupt_flag: bool