import re

def extract_words_from_name(identifier: str) -> list:
    if not identifier:
        return []

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', identifier)
    
    identifier_snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    identifier_lower = identifier_snake.lower()

    words = identifier_lower.split('_')
    
    cleaned_words = [word for word in words if word.strip()]
    
    return cleaned_words