def normalize(s):
    return str(s).lower().replace("_", " ").strip()

def issues_match(c, v):
    if c == "unknown" or v == "unknown": return True
    if c == v or c in v or v in c: return True
    
    # A user might call a dent a scratch, or a shatter a crack. 
    # If the VLM detected ANY physical damage, we support the claim's issue.
    if c not in ["none"] and v not in ["none"]:
        return True
    return False

def parts_match(c, v):
    if c == "unknown" or v == "unknown": return True
    if c == v or c in v or v in c: return True
    
    c_words = set(c.split())
    v_words = set(v.split())
    
    for cw in c_words:
        for vw in v_words:
            if cw in vw or vw in cw:
                return True
                
    # Broad proximity rules
    if any(p in c for p in ["rear", "trunk", "back", "tail"]) and any(p in v for p in ["rear", "trunk", "back", "tail"]): return True
    if any(p in c for p in ["front", "hood", "grille"]) and any(p in v for p in ["front", "hood", "grille"]): return True
    if any(p in c for p in ["side", "door", "mirror", "fender"]) and any(p in v for p in ["side", "door", "mirror", "fender"]): return True
    if any(p in c for p in ["glass", "window", "windshield", "screen"]) and any(p in v for p in ["glass", "window", "windshield", "screen"]): return True
    
    return False

def make_decision(claim, vision, evidence):
    """
    Deterministic rule-based decision logic.
    LLM NEVER decides status.
    """
    c_issue = normalize(claim.get("issue_type", "unknown"))
    v_issue = normalize(vision.get("issue_type", "unknown"))
    
    c_part = normalize(claim.get("object_part", "unknown"))
    v_part = normalize(vision.get("object_part", "unknown"))
    
    pmatch = parts_match(c_part, v_part)
    imatch = issues_match(c_issue, v_issue)
    
    if v_issue == "none" or not vision.get("visible_damage", False):
        if pmatch:
            return "contradicted"
        else:
            return "not_enough_information"
            
    if imatch:
        if pmatch:
            return "supported"
        else:
            return "contradicted"
            
    return "not_enough_information"

def get_justification(status, claim, vision):
    if status == "supported":
        return f"Damage ({vision.get('issue_type')}) is visible on the {vision.get('object_part')}, matching the claim."
    elif status == "contradicted":
        return f"Image clearly shows {vision.get('object_part')} is intact, contradicting the claim."
    else:
        return "Images are insufficient to verify the exact claim."
