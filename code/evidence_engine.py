def validate_evidence(claim, vision, requirements_df):
    """
    Validates if the visual evidence is sufficient based on image quality and visible objects.
    """
    image_quality = vision.get('image_quality', '').lower()
    if image_quality in ['poor', 'blurry', 'low']:
        return {
            "evidence_standard_met": False,
            "evidence_standard_met_reason": "Image quality is too poor to evaluate"
        }
    
    if vision.get('visible_damage'):
        return {
            "evidence_standard_met": True,
            "evidence_standard_met_reason": f"{vision.get('issue_type')} clearly visible on {vision.get('object_part')}"
        }
    else:
        return {
            "evidence_standard_met": True,
            "evidence_standard_met_reason": "Clear image showing no damage"
        }
