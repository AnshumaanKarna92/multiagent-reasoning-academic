import re
from typing import Optional, Dict

def extract_linear_answer(response: str) -> Optional[str]:
    
    patterns = [
        r'x\s*=\s*([-+]?\d*\.?\d+)',
        r'x\s*=\s*\(?([-+]?\d*\.?\d+)\)?',
        r'(?:answer|solution)\s*:?\s*x\s*=\s*([-+]?\d*\.?\d+)',
        r'the\s+answer\s+is\s+x\s*=\s*([-+]?\d*\.?\d+)',
    ]
    
    response_lower = response.lower()
    
    for pattern in patterns:
        match = re.search(pattern, response_lower)
        if match:
            value = match.group(1)
            try:
                num = float(value)
                return f"x = {num}"
            except:
                pass
    
    return None

def extract_quadratic_answer(response: str) -> Optional[str]:
    
    patterns = [
        r'x\s*=\s*([-+]?\d*\.?\d+)\s+(?:or|,)\s+([-+]?\d*\.?\d+)',
        r'solutions?:?\s*x\s*=\s*([-+]?\d*\.?\d+)\s+(?:or|,)\s+([-+]?\d*\.?\d+)',
    ]
    
    response_lower = response.lower()
    
    for pattern in patterns:
        match = re.search(pattern, response_lower)
        if match:
            v1, v2 = match.group(1), match.group(2)
            try:
                f1, f2 = float(v1), float(v2)
                return f"x = {min(f1, f2)}, {max(f1, f2)}"
            except:
                pass
    
    if 'no solution' in response_lower or 'no real' in response_lower:
        return "no solution"
    
    if 'one solution' in response_lower or 'double root' in response_lower:
        pattern = r'x\s*=\s*([-+]?\d*\.?\d+)'
        match = re.search(pattern, response_lower)
        if match:
            return f"x = {float(match.group(1))}"
    
    return None

def extract_answer_from_response(response: str, problem: str) -> Optional[Dict[str, any]]:
    
    problem_lower = problem.lower()
    
    if 'solve' in problem_lower and ('^2' in problem_lower or 'x^2' in problem_lower or 'quadratic' in problem_lower):
        answer = extract_quadratic_answer(response)
        return {
            "answer": answer,
            "problem_type": "quadratic",
            "confidence": "high" if answer else "none"
        }
    
    elif 'solve' in problem_lower and ('=' in problem_lower):
        answer = extract_linear_answer(response)
        return {
            "answer": answer,
            "problem_type": "linear",
            "confidence": "high" if answer else "none"
        }
    
    else:
        return {
            "answer": None,
            "problem_type": "other",
            "confidence": "none"
        }

def normalize_answer(answer: str, problem_type: str = "linear") -> str:
    
    if answer is None:
        return None
    
    answer_lower = answer.lower().strip()
    
    if 'no solution' in answer_lower:
        return "no solution"
    
    if problem_type == "linear":
        match = re.search(r'x\s*=\s*([-+]?\d*\.?\d+)', answer_lower)
        if match:
            return f"x = {float(match.group(1))}"
    
    elif problem_type == "quadratic":
        if ',' in answer or 'or' in answer:
            vals = re.findall(r'([-+]?\d*\.?\d+)', answer)
            if len(vals) >= 2:
                f1, f2 = float(vals[0]), float(vals[1])
                return f"x = {min(f1, f2)}, {max(f1, f2)}"
        else:
            match = re.search(r'x\s*=\s*([-+]?\d*\.?\d+)', answer_lower)
            if match:
                return f"x = {float(match.group(1))}"
    
    return answer
