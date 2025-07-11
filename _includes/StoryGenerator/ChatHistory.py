import os, re
from .ApiComposer import ApiComposer
from ..settings import config

class ChatHistory:
    
    @staticmethod
    def read() -> str:
        with open(config.history_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content if content is not None else ""
    
    @staticmethod
    def write_history(content: str) -> None:
        with open(config.history_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def append_history(content: str) -> None:
        with open(config.history_path, 'a', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def has_separator(content=None) -> bool:
        if content is None:
            content = ChatHistory.read()
        lines = content.splitlines()
        return any(line.strip() == config.separator for line in lines)
    
    @staticmethod
    def insert_separator():
        history_content = ChatHistory.read()
        lines = history_content.strip().splitlines()
        if lines[-1] != config.separator:
            ChatHistory.append_history(f"\n\n{config.separator}\n\n")

    @staticmethod
    def count_parts(content=None) -> int:
        if content is None:
            content = ChatHistory.read()
        lines = content.splitlines()
        return sum(1 for line in lines if line.strip() == config.separator)

    @staticmethod
    def switch_to_summary():
        if '_summary.md' not in config.history_path:
            config.history_path = config.history_path.replace('.md', '_summary.md')

    @staticmethod
    def switch_to_story():
        config.history_path = config.history_path.replace('_summary', '')

    @staticmethod
    def merge_story_with_summary():

        history_content = ChatHistory.read()
        history_split = history_content.split(config.separator)

        ChatHistory.switch_to_summary()
        if not os.path.exists(config.history_path):
            ChatHistory.switch_to_story()
            return history_content
        
        summary_content = ChatHistory.read()
        number_of_summary_parts = ChatHistory.count_parts()

        history_content = config.separator.join(history_split[number_of_summary_parts:])
        history_content = summary_content + history_content
        
        ChatHistory.switch_to_story()

        return history_content

    @staticmethod
    def remove_last_response() -> None:
        content = ChatHistory.read().strip()
        lines = content.splitlines()

        # Remove last line if last line is a separator
        if lines and lines[-1] == config.separator:
            lines[-1] = ''
            content = '\n'.join(lines).strip()

        if not ChatHistory.has_separator(content):
            ChatHistory.write_history('')
            return

        #Remove text after the last separator
        if (pos := content.rfind(config.separator)) != -1:
            ChatHistory.write_history(content[:pos + len(config.separator)] + '\n\n')

    @staticmethod
    def parse_assistant_response(history_content) -> tuple[str, str]:
        lines = history_content.splitlines()

        has_separator = ChatHistory.has_separator(history_content)
        if not has_separator or lines[-1].strip() == config.separator:
            return history_content, None
        
        parts = history_content.split(f'\n{config.separator}\n')
        history_content = f'\n{config.separator}\n'.join(parts[:-1]).strip()
        assistant_response = parts[-1].strip()
        return history_content, assistant_response

    @staticmethod
    def remove_reasoning_header(history_content: str) -> str:
        return '\n'.join(
            line 
            for line in history_content.splitlines() 
            if line != config.reasoning_header).strip()
    
    @staticmethod
    def remove_reasoning_tokens(history_content: str) -> str:
        import re
    
        pattern = r'<think>.*?</think>'

        cleaned_content = re.sub(pattern, '', history_content, flags=re.DOTALL)
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        
        return cleaned_content

    @staticmethod
    def format_history(history_content: str) -> str:

        cleaned_content = '\n\n'.join(
            block.strip() 
            for block in history_content.split(config.separator) 
            if block.strip()
        )

        return cleaned_content
    
    @staticmethod
    def replace_history_part(new_part) -> str:
        history_content = ChatHistory.read()
        history_split = history_content.split(config.separator)
        new_part = '\n\n' + new_part + '\n\n'

        splitter = '</think>'
        if splitter in history_split[config.part_number-1]:
            think_part, _ = history_split[config.part_number-1].split(splitter, 1)
            history_split[config.part_number-1] = think_part + splitter + new_part
        else:
            history_split[config.part_number-1] = new_part
            
        history_content = config.separator.join(history_split)

        ChatHistory.write_history(history_content)

    @staticmethod
    def add_part(new_part) -> str:
        history_content = ChatHistory.read()
        history_split = history_content.split(config.separator)
        new_part = '\n\n' + new_part + '\n\n'

        history_split.insert(config.part_number, new_part)
        history_content = config.separator.join(history_split)

        ChatHistory.write_history(history_content)
        
    @staticmethod
    def remove_reasoning():
        history_content = ChatHistory.read()
        history_content = ChatHistory.remove_reasoning_header(history_content)
        history_content = ChatHistory.remove_reasoning_tokens(history_content)
        history_content = history_content + '\n\n'
        ChatHistory.write_history(history_content)

    @staticmethod
    def expand_abbreviations(user_prompt):
        
        if config.abbreviations is None:
            return user_prompt

        case_insensitive_mapping = {k.lower(): v for k, v in config.abbreviations.items()}
        # Match letters preceded by whitespace or start, followed by delimiters or end
        pattern = r"(^|\s)([a-zA-Z]+)(?=[:, .?!'\s]|$)"
        
        def replace_match(match):
            prefix = match.group(1)
            abbreviation = match.group(2)
            if abbreviation.lower() in case_insensitive_mapping:
                return prefix + case_insensitive_mapping[abbreviation.lower()]
            return match.group(0)
        
        result = re.sub(pattern, replace_match, user_prompt)
        return result

    @staticmethod
    def process_history(rewrite: bool = False):

        part_number_content = ""

        # Read history
        if config.use_summary:
            history_content = ChatHistory.merge_story_with_summary()
        else:
            history_content = ChatHistory.read()

        # Remove '### Reasoning' headers
        history_content = ChatHistory.remove_reasoning_header(history_content)

        # Parse assistant response to continue last response
        history_content, assistant_response = ChatHistory.parse_assistant_response(history_content)

        # Remove reasoning tokens
        history_content = ChatHistory.remove_reasoning_tokens(history_content)

        # Cut history
        if rewrite:
            history_split = history_content.split(config.separator)
            history_content = config.separator.join(history_split[:config.part_number-1])
            part_number_content = history_split[config.part_number-1]

        # Remove separators and extra empyty lines
        history_content = ChatHistory.format_history(history_content)

        # Exclude first paragraphs to match input length with max_tokens
        history_content = ApiComposer.trim_content(history_content, config.max_tokens)

        return history_content, part_number_content, assistant_response