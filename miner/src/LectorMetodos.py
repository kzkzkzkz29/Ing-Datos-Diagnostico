import re

def extract_python_functions(code_content: str) -> list:

    pattern = r"^[ \t]*def[ \t]+([a-zA-Z_][a-zA-Z0-9_]*)[ \t]*\("
    return re.findall(pattern, code_content, re.MULTILINE)

def extract_java_methods(code_content: str) -> list:

    modifiers = r"(?:(?:public|private|protected|static|final|abstract|synchronized|@\w+)[ \t]+)*"
    
    return_type = r"(?:[\w\<\>\[\]\,\?]+[ \t]+)+"
    
    method_name = r"([a-zA-Z_$][a-zA-Z0-9_$]*)[ \t]*\("
    
    pattern = r"^[ \t]*" + modifiers + return_type + method_name
    
    matches = re.findall(pattern, code_content, re.MULTILINE)
    
    reserved_words = {'if', 'for', 'while', 'catch', 'switch', 'return', 'new'}
    return [match for match in matches if match not in reserved_words]