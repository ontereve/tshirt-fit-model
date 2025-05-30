import math
from .model_params import *

import logging
logger = logging.getLogger(__name__)

"""
Fit scoring model for t-shirts.
Calculates a FitScore (0-100) plus confidence, style tags, and a rationale...
"""

# --- Utility Functions ---
def get_val(x):
    """
    Returns None if x is missing, None, or NaN.
    """
    if x is None:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    return x
def extract_aspect_inputs(body, shirt, aspect):
    """Returns the relevant (body_value, shirt_value) for this aspect using ASPECT_TO_FIELD."""
    body_field, shirt_field = ASPECT_TO_FIELD[aspect]
    body_val = get_val(body.get(body_field)) if body_field else None
    shirt_val = get_val(shirt.get(shirt_field)) if shirt_field else None
    return body_val, shirt_val
def record_aspect(scores, tags, rationale_parts, missing, aspect, score, tag, rationale):
    scores[aspect] = score
    if tag:
        tags.append(tag)
    if rationale:
        rationale_parts.append(rationale)
    if score == 50:
        missing.append(aspect.capitalize())
def calc_confidence(aspect_present, aspect_count):
    if aspect_count == 0:
        return 0
    return round(100 * aspect_present / aspect_count)
def filter_tags(tags, min_aspects, aspect_present):
    return [t for t in tags if t] if aspect_present >= min_aspects else []
def score_by_ratio(ratio, bounds):
    """
    Generic ratio-based scoring logic.
    bounds: list of (upper_bound, score, tag, rationale)
    Returns (score, tag, rationale) for the first matching bound.
    """
    for upper, score, tag, rationale in bounds:
        if ratio < upper:
            return score, tag, rationale
    # Default: use last one
    last = bounds[-1]
    return last[1], last[2], last[3]


# --- Scoring Functions ---
def score_chest(body_chest, shirt_chest):
    """
    Returns (score, tag, rationale_str)
    """
    if body_chest is not None and shirt_chest is not None:
        chest_diff = shirt_chest - body_chest
        if chest_diff < -0.5:
            return max(0, 100 + chest_diff * CHEST_TOO_TIGHT_PENALTY), "Too Tight", f"Chest: {chest_diff:+.1f}\" vs body (tight)."
        elif chest_diff < 0:
            return max(0, 100 + chest_diff * CHEST_SLIM_PENALTY), "Slim Fit", f"Chest: {chest_diff:+.1f}\" vs body (slim)."
        elif chest_diff < 0.5:
            return 100, None, f"Chest: {chest_diff:+.1f}\" vs body (close fit)."
        elif chest_diff < CHEST_RELAXED_MAX:
            return 100, "Relaxed Fit", f"Chest: {chest_diff:+.1f}\" vs body (relaxed)."
        elif chest_diff < CHEST_OVERSIZED_MAX:
            return 95, "Oversized", f"Chest: {chest_diff:+.1f}\" vs body (oversized)."
        elif chest_diff < CHEST_COMICALLY_OVERSIZED_MAX:
            return 85 - (chest_diff - CHEST_OVERSIZED_MAX) * CHEST_VERY_OVERSIZED_PENALTY, "Very Oversized", f"Chest: {chest_diff:+.1f}\" vs body (very oversized)."
        else:
            return 70 - (chest_diff - CHEST_COMICALLY_OVERSIZED_MAX) * 8, "Comically Oversized", f"Chest: {chest_diff:+.1f}\" vs body (comically oversized)."
    logger.warning("Missing chest data for scoring.")
    return 50, None, "[No chest data]"
def score_shoulder(body_shoulder, shirt_shoulder):
    if body_shoulder is not None and shirt_shoulder is not None:
        diff = shirt_shoulder - body_shoulder
        if diff < -0.5:
            return max(0, 100 + diff * SHOULDER_TOO_NARROW_PENALTY), "Shoulders Too Narrow", f"Shoulder: {diff:+.1f}\" vs body (too narrow)."
        elif diff < 0.5:
            return 100, None, f"Shoulder: {diff:+.1f}\" vs body (fitted)."
        elif diff < SHOULDER_DROP_MAX:
            return 100, "Drop-Shoulder", f"Shoulder: {diff:+.1f}\" vs body (drop-shoulder)."
        else:
            return max(60, 100 - (diff - SHOULDER_DROP_MAX) * SHOULDER_VERY_OVERSIZED_PENALTY), "Very Oversized Shoulders", f"Shoulder: {diff:+.1f}\" vs body (very oversized)."
    logger.warning("Missing shoulder data for scoring.")
    return 50, None, "[No shoulder data]"
def score_length(body_length, shirt_length, shirt_chest):
    if body_length is not None and shirt_length is not None:
        diff = shirt_length - body_length
        if diff < LENGTH_CROPPED_MIN:
            return 50, "Cropped", f"Length: {diff:+.1f}\" vs body (cropped)."
        elif diff < LENGTH_SHORT_MAX:
            return 70, "Short Length", f"Length: {diff:+.1f}\" vs body (short)."
        elif diff < LENGTH_IDEAL_MAX:
            return 100, None, f"Length: {diff:+.1f}\" vs body (ideal)."
        elif diff < LENGTH_LONG_MAX:
            return 90, None, f"Length: {diff:+.1f}\" vs body (long)."
        else:
            return LENGTH_VERY_LONG_PENALTY, "Very Long", f"Length: {diff:+.1f}\" vs body (very long)."
    elif shirt_length is not None and shirt_chest is not None:
        ratio = shirt_length / shirt_chest
        bounds = [
            (1.2, 100, "Boxy Cut", f"Length: Length-to-chest ratio {ratio:.2f} (boxy cut)."),
            (1.4, 90, None, f"Length: Length-to-chest ratio {ratio:.2f} (regular)."),
            (float('inf'), 70, "Longline Cut", f"Length: Length-to-chest ratio {ratio:.2f} (longline)."),
        ]
        return score_by_ratio(ratio, bounds)
    logger.warning("Missing length data for scoring.")
    return 50, None, "[No length data]"
def score_hem(body_hem, shirt_hem, shirt_chest):
    if shirt_hem is not None and ((body_hem is not None) or (shirt_chest is not None)):
        if body_hem is not None:
            diff = shirt_hem - body_hem
            if diff < 0:
                return max(0, 100 - abs(diff) * HEM_TOO_TIGHT_PENALTY), "Tight Waist", f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body."
            elif diff < HEM_FLARED_MIN:
                return 100, None, f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body."
            else:
                return 90, "Flared Hem", f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body."
        else:
            diff = shirt_hem - shirt_chest
            if diff < -HEM_BOX_CUT_MAX:
                return HEM_TAPERED_PENALTY, "Tapered Waist", f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs chest."
            elif diff < HEM_BOX_CUT_MAX:
                return 100, None, f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs chest."
            else:
                return 90, "Boxy Cut", f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs chest."
    logger.warning("Missing hem data for scoring.")
    return 50, None, "[No hem data]"
def score_sleeve(body_sleeve, shirt_sleeve, shirt_chest):
    if shirt_sleeve is not None:
        if body_sleeve is not None:
            diff = shirt_sleeve - body_sleeve
            if diff < SLEEVE_CAP_MIN:
                return SLEEVE_CAP_SCORE, "Cap Sleeve", f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm."
            elif diff < SLEEVE_SHORT_MAX:
                return SLEEVE_SHORT_SCORE, "Short Sleeves", f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm."
            elif diff < SLEEVE_IDEAL_MAX:
                return SLEEVE_IDEAL_SCORE, None, f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm."
            else:
                return SLEEVE_ELBOW_SCORE, "Elbow-Length Sleeves", f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm."
        else:
            ratio = shirt_sleeve / shirt_chest if shirt_chest else 0
            if ratio < 0.35:
                return SLEEVE_SHORT_SCORE, "Short Sleeves", f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}."
            elif ratio > 0.5:
                return SLEEVE_ELBOW_SCORE, "Elbow-Length Sleeves", f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}."
            else:
                return SLEEVE_IDEAL_SCORE, None, f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}."
    logger.warning("Missing sleeve data for scoring.")
    return 50, None, "[No sleeve data]"
def score_weight(shirt_weight, scores):
    if shirt_weight is not None and isinstance(shirt_weight, (int, float)):
        wt = shirt_weight
        only_weight = all(
            scores.get(k, 50) == 50
            for k in ASPECTS if k != 'weight'
        )
        if wt < WEIGHT_LIGHT_MAX:
            score = 42 if only_weight else WEIGHT_LIGHT_SCORE
            tag = "Lightweight"
        elif wt < WEIGHT_MID_MAX:
            score = WEIGHT_MID_SCORE
            tag = "Midweight"
        elif wt < WEIGHT_HEAVY_MAX:
            score = WEIGHT_HEAVY_SCORE
            tag = "Heavyweight"
        else:
            score = WEIGHT_VERY_HEAVY_SCORE
            tag = "Very Heavyweight"
        rationale = f"Weight: {wt:.1f} oz (ideal is 5–6 oz for vintage)."
        return score, tag, rationale
    logger.warning("Missing shirt weight data for scoring.")
    return 50, None, "[No shirt weight data]"
SCORER_FUNCS = {
    'score_chest': score_chest,
    'score_shoulder': score_shoulder,
    'score_length': score_length,
    'score_hem': score_hem,
    'score_sleeve': score_sleeve,
    'score_weight': score_weight,
}


# --- Adjustments ---
def adjust_for_oversize_weight(tags, shirt_weight, fit_score):
    """
    Adjusts fit_score for oversized/weight interplay.
    """
    if "Comically Oversized" in tags and shirt_weight and shirt_weight < 5.0:
        fit_score = max(0, fit_score - 10)
        logger.info(f"Applied harsh penalty for comically oversized lightweight shirt (weight: {shirt_weight}).")
    elif ("Oversized" in tags or "Very Oversized" in tags) and shirt_weight:
        if shirt_weight >= 6.0:
            fit_score = min(100, fit_score + OVERSIZED_HEAVY_BONUS)
        elif shirt_weight < 4.5:
            fit_score = max(0, fit_score - OVERSIZED_LIGHT_PENALTY * 2)
    if "Relaxed Fit" in tags and shirt_weight and shirt_weight >= 6.5:
        fit_score = min(100, fit_score + RELAXED_HEAVY_BONUS)
    if "Slim Fit" in tags and shirt_weight and shirt_weight < 4.5:
        fit_score = max(0, fit_score - SLIM_LIGHT_PENALTY)
    if "Comically Oversized" in tags and fit_score > 70:
        fit_score = 70
    elif "Very Oversized" in tags and fit_score > 85:
        fit_score = 85
    return fit_score

# --- Main Fit/Projection Functions ---
def score_fit(body, shirt):
    """
    Calculates overall t-shirt fit score for a given body and shirt profile.

    Args:
        body (dict): Body measurement data, with expected fields.
        shirt (dict): Shirt measurement data, with expected fields.

    Returns:
        dict: {
            "FitScore": int,
            "Confidence": int,
            "Tags": list of str,
            "Rationale": str
        }
    """
    logger.debug(f"Scoring fit for shirt: {shirt.get('ShirtName', '[unnamed]')}")
    scores, tags, rationale_parts, missing = {}, [], [], []
    aspect_present = 0
    aspect_count = len(ASPECTS)

    for aspect, config in ASPECT_SCORERS.items():
        body_field, shirt_field = config['fields']
        body_val = get_val(body.get(body_field)) if body_field else None
        shirt_val = get_val(shirt.get(shirt_field)) if shirt_field else None
        scorer_fn = SCORER_FUNCS[config['scorer']]
        if aspect in ASPECTS_NEED_CHEST:
            # Always pass shirt_chest as third arg
            shirt_chest_val = get_val(shirt.get('ChestWidth'))
            score, tag, rationale = scorer_fn(body_val, shirt_val, shirt_chest_val)
        elif aspect == 'weight':
            score, tag, rationale = scorer_fn(shirt_val, scores)
        else:
            score, tag, rationale = scorer_fn(body_val, shirt_val)
        record_aspect(scores, tags, rationale_parts, missing, aspect, score, tag, rationale)
        if score != 50:
            aspect_present += 1



    # --- Final calculation ---
    fit_score = round(
        sum(scores[aspect] * WEIGHTS[aspect] for aspect in ASPECTS) /
        sum(WEIGHTS[aspect] for aspect in ASPECTS)
    )

    # Get shirt_weight for adjustments (find from shirt or from scores, as in aspect loop)
    # Best option: get directly from the shirt dict using your aspect config:
    weight_aspect = 'weight'
    weight_field = ASPECT_SCORERS[weight_aspect]['fields'][1]
    shirt_weight = get_val(shirt.get(weight_field)) if weight_field else None

    # Oversize & Weight Adjustments
    if aspect_present >= 2:
        fit_score = adjust_for_oversize_weight(tags, shirt_weight, fit_score)


    confidence = calc_confidence(aspect_present, aspect_count)
    tags = filter_tags(tags, 2, aspect_present)

    if aspect_present == 0:
        return {
            "FitScore": "",
            "Confidence": 0,
            "Tags": [],
            "Rationale": "No measurements available for this shirt."
        }

    return {
        "FitScore": fit_score,
        "Confidence": confidence,
        "Tags": tags,
        "Rationale": " ".join(rationale_parts)
    }
def bulk_projection_profile(body):
    """
    Returns a projected bulked-up body profile based on the provided body measurements.
    """
    logger.debug(f"Generating bulk profile projection from: {body}")
    new_body = body.copy()
    for field, inc in BULK_PROFILE_CONFIG['increments'].items():
        if field in new_body and inc:
            new_body[field] = float(new_body[field]) + inc
    return new_body

