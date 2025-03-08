from typing import Optional, List, Dict, Any
from ..chat_settings import config

class ApiComposer:

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
        
    @staticmethod
    def trim_content(content: str, max_tokens: int) -> str:
        paragraphs = content.split('\n\n')
        current_tokens = ApiComposer.estimate_tokens(content)
        
        while current_tokens > max_tokens and len(paragraphs) > 1:
            paragraphs.pop(0)
            content = '\n\n'.join(paragraphs)
            current_tokens = ApiComposer.estimate_tokens(content)
            
        return content
    
    @staticmethod
    def append_message(messages: List[Dict[str, str]], role: str, content: Optional[str]) -> None:
        if content:
            messages.append({"role": role, "content": content.strip()})

    @staticmethod
    def compose_messages(history: Optional[str] = None,
                        assistant_response: Optional[str] = None) -> List[Dict[str, str]]:
        messages = []

        ApiComposer.append_message(messages, "system", config.system_prompt)

        if config.has_separator:
            ApiComposer.append_message(messages, "user", config.first_prompt)
            ApiComposer.append_message(messages, "assistant", history)
            ApiComposer.append_message(messages, "user", config.user_prompt)
        else:
            ApiComposer.append_message(messages, "user", config.first_prompt + config.user_prompt)
            ApiComposer.append_message(messages, "assistant", history)

        ApiComposer.append_message(messages, "assistant", assistant_response)


        return messages