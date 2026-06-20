import os
import sys
import pandas as pd
from utils.csv_utils import load_csv, save_csv

# Force bypass of any system proxies that might be blocking the connection (WinError 10013)
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    os.environ.pop(proxy_var, None)

from llm_client import extract_claim
from vlm_client import analyze_images
from evidence_engine import validate_evidence
from risk_engine import calculate_risk, add_image_risks
from decision_engine import make_decision, get_justification
from config import CLAIMS_CSV, USER_HISTORY_CSV, EVIDENCE_REQS_CSV, OUTPUT_CSV, DATASET_DIR

def main():
    if not os.path.exists(CLAIMS_CSV):
        print(f"Dataset not found at {CLAIMS_CSV}")
        return

    claims_df = load_csv(CLAIMS_CSV)
    user_history_df = load_csv(USER_HISTORY_CSV)
    user_history_dict = user_history_df.set_index('user_id').to_dict('index')
    
    evidence_reqs_df = load_csv(EVIDENCE_REQS_CSV)
    
    outputs = []
    
    for i, claim in claims_df.iterrows():
        image_paths_str = claim.get("image_paths", "")
        raw_paths = [p.strip() for p in str(image_paths_str).split(';') if p.strip()]
        resolved_paths = [os.path.join(DATASET_DIR, p) for p in raw_paths]
        
        claim_data = extract_claim(str(claim.get("user_claim", "")))
        vision_data = analyze_images(resolved_paths)
        
        if vision_data is None:
            print(f"Skipping claim {claim.get('user_id')} due to API error.")
            continue
            
        evidence = validate_evidence(claim_data, vision_data, evidence_reqs_df)
        
        u_id = claim.get("user_id")
        u_history = user_history_dict.get(u_id, {})
        risk_flags = calculate_risk(u_history)
        risk_flags = add_image_risks(vision_data, risk_flags)
        
        decision_status = make_decision(claim_data, vision_data, evidence)
        justification = get_justification(decision_status, claim_data, vision_data)
        
        allowed_statuses = {"supported", "contradicted", "not_enough_information"}
        if decision_status not in allowed_statuses:
            decision_status = "not_enough_information"
            
        allowed_severities = {"none", "low", "medium", "high", "unknown"}
        sev = vision_data.get("severity", "unknown").lower()
        if sev not in allowed_severities:
            sev = "unknown"
            
        final_risk = ";".join(risk_flags) if risk_flags else "none"
        
        supp_imgs = vision_data.get("supporting_image_ids", [])
        if not supp_imgs:
            supp_img_str = "none"
        else:
            supp_img_str = ";".join(str(img) for img in supp_imgs)
            
        out_row = {
            "user_id": claim.get("user_id"),
            "image_paths": image_paths_str,
            "user_claim": claim.get("user_claim"),
            "claim_object": claim.get("claim_object"),
            "evidence_standard_met": evidence.get("evidence_standard_met", False),
            "evidence_standard_met_reason": evidence.get("evidence_standard_met_reason", "unknown"),
            "risk_flags": final_risk,
            "issue_type": vision_data.get("issue_type", "unknown"),
            "object_part": vision_data.get("object_part", "unknown"),
            "claim_status": decision_status,
            "claim_status_justification": justification,
            "supporting_image_ids": supp_img_str,
            "valid_image": True if vision_data.get("image_quality", "") not in ["poor", "blurry", "unknown"] else False,
            "severity": sev
        }
        outputs.append(out_row)
        
    save_csv(pd.DataFrame(outputs), OUTPUT_CSV)
    print(f"Processing complete. Output saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
