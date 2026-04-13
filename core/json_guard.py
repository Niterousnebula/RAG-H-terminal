import json


ALLOWED_TYPES = {"chat", "code", "reasoning", "tool"}
ALLOWED_MODELS = {"mistral", "qwen", "deepseek"}


def extract_json(text: str):
    """
    Extract JSON object from messy LLM output
    """
    try:
        return json.loads(text)
    except:
        pass

    # try to extract substring
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except:
            return None

    return None


def validate_decision(data: dict):
    """
    Ensure schema correctness
    """
    if not isinstance(data, dict):
        return None

    t = data.get("type")
    m = data.get("model")

    if t not in ALLOWED_TYPES:
        return None

    if m not in ALLOWED_MODELS:
        return None

    return {
        "type": t,
        "model": m,
        "tool": data.get("tool", None)
    }


def repair_decision(raw_text: str):
    """
    Last fallback using rules
    """
    text = raw_text.lower()

    if "code" in text or "python" in text:
        return {"type": "code", "model": "qwen"}

    if "explain" in text or "why" in text:
        return {"type": "reasoning", "model": "deepseek"}

    return {"type": "chat", "model": "mistral"}
  