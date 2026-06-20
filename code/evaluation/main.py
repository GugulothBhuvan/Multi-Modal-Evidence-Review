import os
import sys
import pandas as pd
from metrics import compute_metrics

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.csv_utils import load_csv
from llm_client import extract_claim
from vlm_client import analyze_images
from evidence_engine import validate_evidence
from decision_engine import make_decision

def main():
    print("Loading sample_claims.csv (Ground Truth)...")
    df = load_csv("../../dataset/sample_claims.csv")
    
    y_true = []
    y_pred = []
    
    print(f"Evaluating {len(df)} sample claims...")
    
    for i, row in df.iterrows():
        print(f"Processing row {i+1}/{len(df)}...")
        
        # Ground Truth
        expected_status = str(row.get("claim_status", "")).lower().strip()
        
        # 1. LLM
        claim_data = extract_claim(str(row.get("user_claim", "")))
        
        # 2. VLM
        raw_paths = str(row.get("image_paths", "")).split(";")
        resolved_paths = [os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset", p.strip())) for p in raw_paths if p.strip()]
        vision_data = analyze_images(resolved_paths)
        
        if vision_data is None:
            print(f"  -> Skipping row {i+1} due to API error. Excluded from metrics.")
            continue
            
        y_true.append(expected_status)
        
        # 3. Engines
        evidence = validate_evidence(claim_data, vision_data, None)
        predicted_status = make_decision(claim_data, vision_data, evidence)
        y_pred.append(predicted_status.lower().strip())
        
        if expected_status != predicted_status.lower().strip():
            print(f"  -> [MISMATCH] Expected: {expected_status} | Predicted: {predicted_status}")
            print(f"     LLM extracted  -> issue: '{claim_data.get('issue_type')}', part: '{claim_data.get('object_part')}'")
            print(f"     VLM detected   -> issue: '{vision_data.get('issue_type')}', part: '{vision_data.get('object_part')}', damage: {vision_data.get('visible_damage')}, quality: '{vision_data.get('image_quality')}'")
            print(f"     Evidence Met   -> {evidence.get('evidence_standard_met')}")
        else:
            print(f"  -> [MATCH] Expected: {expected_status} | Predicted: {predicted_status}")

    # Compute Metrics
    labels = ["supported", "contradicted", "not_enough_information"]
    results = compute_metrics(y_true, y_pred, labels)
    
    print("\n" + "="*40)
    print("BENCHMARKING RESULTS")
    print("="*40)
    print(f"Overall Accuracy: {results['accuracy'] * 100:.2f}%")
    for i, label in enumerate(labels):
        print(f"\nLabel: {label}")
        print(f"  Precision: {results['precision'][i]:.2f}")
        print(f"  Recall:    {results['recall'][i]:.2f}")
        print(f"  F1-Score:  {results['f1'][i]:.2f}")
    print("="*40)

if __name__ == "__main__":
    main()
