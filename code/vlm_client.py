import os
import json
import httpx
import time
from dotenv import load_dotenv
from utils.cache import cached_call, get_image_hash

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

import PIL.Image
import pillow_avif
import io
import base64

def _call_openrouter(image_paths):
    # Minimal sleep since OpenRouter manages rate limits much better
    time.sleep(1)
    
    if not OPENROUTER_API_KEY:
        print("No OPENROUTER_API_KEY found.")
        return None

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "vision_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    content = [{"type": "text", "text": system_prompt}]

    for path in image_paths:
        try:
            if not os.path.exists(path):
                continue
            
            img = PIL.Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
                
            img.thumbnail((512, 512))
                
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            base64_img = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
            })
        except Exception as e:
            print(f"Error processing image {path}: {e}")

    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "user", "content": content}
        ],
        "temperature": 0.1,
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    url = "https://openrouter.ai/api/v1/chat/completions"
    try:
        response = httpx.post(url, headers=headers, json=payload, verify=False, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        
        raw_content = data['choices'][0]['message']['content']
        return json.loads(raw_content)
    except httpx.HTTPStatusError as e:
        print(f"Error calling OpenRouter API: Client error '{e.response.status_code} {e.response.reason_phrase}' for url '{e.request.url}'")
        print(f"For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{e.response.status_code}")
        try:
            print(f"Raw response: {e.response.text}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

def analyze_images(image_paths):
    if not image_paths:
        return None
        
    img_hash = get_image_hash(image_paths)
    return cached_call(f"vlm_{img_hash}", _call_openrouter, image_paths)
