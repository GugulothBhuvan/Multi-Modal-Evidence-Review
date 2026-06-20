import pandas as pd

def calculate_risk(user_history_row):
    flags = []
    
    try:
        rejected = int(user_history_row.get("rejected_claim", 0))
    except:
        rejected = 0
        
    if rejected > 5:
        flags.append("manual_review_required")
        
    try:
        last_90 = int(user_history_row.get("last_90_days_claim_count", 0))
    except:
        last_90 = 0
        
    if last_90 > 10:
        flags.append("user_history_risk")
        
    return flags

def add_image_risks(vision, risk_flags):
    quality = vision.get("image_quality", "").lower()
    if quality == "blurry":
        risk_flags.append("blurry_image")
    elif quality == "cropped":
        risk_flags.append("cropped_or_obstructed")
    elif quality == "glare":
        risk_flags.append("low_light_or_glare")
        
    return risk_flags
