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
    print_messages: bool
    include_reasoning: bool
    reasoning_header: str
    separator: str
    interrupt_flag: bool
    print_reasoning: bool
    print_output: bool
    part_number: int
    write_reasoning: bool
    abbreviations: str
    write_interval: float
    use_summary: bool
    history_path: Path
    summary_path: Path
    prompts_path: Path
    folder_path: Path
    include_previous_part_when_summarizing: bool
    include_previous_part_when_rewriting: bool
    debug: bool
    history_prefix: str