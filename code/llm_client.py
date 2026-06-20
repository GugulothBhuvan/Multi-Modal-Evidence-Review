import os
import json
import httpx
from groq import Groq
from dotenv import load_dotenv
from utils.cache import cached_call, get_text_hash

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(
    api_key=GROQ_API_KEY, 
    http_client=httpx.Client(verify=False)
) if GROQ_API_KEY else None

def _call_groq(claim_text):
    if not client:
        return {"issue_type": "unknown", "object_part": "unknown", "claimed_severity": "unknown", "confidence": 0.0}

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "claim_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract details from this claim: {claim_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    try:
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing Groq response: {e}")
        return {"issue_type": "unknown", "object_part": "unknown", "claimed_severity": "unknown", "confidence": 0.0}

def extract_claim(claim_text):
    text_hash = get_text_hash(claim_text)
    return cached_call(f"llm_{text_hash}", _call_groq, claim_text)
