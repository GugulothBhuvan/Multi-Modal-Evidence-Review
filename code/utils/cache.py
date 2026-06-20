import hashlib
import json
import os

CACHE_DIR = ".cache"

def get_image_hash(image_paths):
    h = hashlib.sha256()
    for path in image_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                h.update(f.read())
        else:
            h.update(path.encode('utf-8'))
    return h.hexdigest()

def get_text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def cached_call(key, fn, *args, **kwargs):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    # BYPASS CACHE: We are commenting this out to flush poisoned cache entries!
    # if os.path.exists(cache_file):
    #     with open(cache_file, "r") as f:
    #         return json.load(f)
    
    result = fn(*args, **kwargs)
    with open(cache_file, "w") as f:
        json.dump(result, f)
    return result
