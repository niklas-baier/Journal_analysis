import ollama
import re
from typing import List, Optional

def check_name_typos(name_list: List[str], model: str = "deepseek-r1:7b", 
                    custom_rules: Optional[str] = None) -> str:
    """
    Check for typos and variations in a list of person names.
    
    Args:
        name_list: List of names to check for typos
        model: Ollama model to use for checking
        custom_rules: Optional string with domain-specific rules
    
    Returns:
        String containing the model's response about name groupings
    """
    if not name_list:
        return "No names provided to check."
    
    if len(name_list) > 50:
        print(f"Warning: Processing {len(name_list)} names. Consider breaking into smaller batches.")
    
    names_str = ", ".join(name_list)
    
    # Build custom rules section
    rules_section = ""
    if custom_rules:
        rules_section = f"\nSpecial rules for this dataset:\n{custom_rules}\n"
    
    prompt = f"""You are a name deduplication expert. Analyze the following list of person names and group together those that likely refer to the same person.

NAMES TO ANALYZE:
{names_str}

GROUPING CRITERIA:
1. Obvious typos (missing/extra letters, common keyboard mistakes)
2. Common nickname variations (Mike/Michael, Bob/Robert, etc.)  
3. Missing punctuation between names
4. Context clues like "(online)" or similar annotations
5. Names differing by 1-3 characters are likely the same person
6. Names differing by 4+ characters are likely different people
7. Long names with two surnames but no hyphen should be split into separate people

{rules_section}
OUTPUT FORMAT:
Return ONLY a Python list structure like this:
[
  ["Correct Name", "variation1", "variation2"],
  ["Another Correct Name", "typo1"],
  ["Single Name With No Variations"]
]

Rules:
- First name in each sublist = most likely correct spelling
- Include all variations/typos after the correct name
- Names that appear correct and have no variations should still be in their own sublist
- Do not include any explanatory text, only the list structure"""

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response['message']['content']
        
    except Exception as e:
        return f"Error checking name typos: {str(e)}"

def strip_reasoning(output: str) -> str:
    """Remove reasoning blocks from model output."""
    # Remove <think> ... </think> blocks
    output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
    # Remove any text before the first '[' and after the last ']'
    match = re.search(r'\[.*\]', output, flags=re.DOTALL)
    if match:
        return match.group(0)
    return output

def parse_name_groups(output: str) -> List[List[str]]:
    """
    Parse the model output into a proper Python list structure.
    Returns empty list if parsing fails.
    """
    clean_output = strip_reasoning(output)
    try:
        # Try to evaluate as Python literal
        import ast
        return ast.literal_eval(clean_output)
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse output as Python list: {e}")
        print(f"Raw output: {clean_output}")
        return []

def batch_process_names(name_list: List[str], batch_size: int = 25, 
                       model: str = "deepseek-r1:7b") -> List[List[str]]:
    """
    Process large name lists in batches to improve accuracy.
    """
    if len(name_list) <= batch_size:
        output = check_name_typos(name_list, model)
        return parse_name_groups(output)
    
    all_groups = []
    for i in range(0, len(name_list), batch_size):
        batch = name_list[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} names")
        
        output = check_name_typos(batch, model)
        batch_groups = parse_name_groups(output)
        all_groups.extend(batch_groups)
    
    return all_groups
