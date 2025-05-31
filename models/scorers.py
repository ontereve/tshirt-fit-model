# scorers.py

import math
import logging
from .utils.config_loader import load_model_config

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


def score_chest(body_chest, shirt_chest):
    """
    Returns (score, tag, rationale_str)
    """
    if body_chest is not None and shirt_chest is not None:
        chest_diff = shirt_chest - body_chest
        if chest_diff < -0.5:
            return (
                max(0, 100 + chest_diff * CHEST_TOO_TIGHT_PENALTY),
                "Too Tight",
                f'Chest: {chest_diff:+.1f}" vs body (tight).',
            )
        if chest_diff < 0:
            return (
                max(0, 100 + chest_diff * CHEST_SLIM_PENALTY),
                "Slim Fit",
                f'Chest: {chest_diff:+.1f}" vs body (slim).',
            )
        if chest_diff < 0.5:
            return 100, None, f'Chest: {chest_diff:+.1f}" vs body (close fit).'
        if chest_diff < CHEST_RELAXED_MAX:
            return 100, "Relaxed Fit", f'Chest: {chest_diff:+.1f}" vs body (relaxed).'
        if chest_diff < CHEST_OVERSIZED_MAX:
            return 95, "Oversized", f'Chest: {chest_diff:+.1f}" vs body (oversized).'
        if chest_diff < CHEST_COMICALLY_OVERSIZED_MAX:
            return (
                85 - (chest_diff - CHEST_OVERSIZED_MAX) * CHEST_VERY_OVERSIZED_PENALTY,
                "Very Oversized",
                f'Chest: {chest_diff:+.1f}" vs body (very oversized).',
            )
        else:
            return (
                70 - (chest_diff - CHEST_COMICALLY_OVERSIZED_MAX) * 8,
                "Comically Oversized",
                f'Chest: {chest_diff:+.1f}" vs body (comically oversized).',
            )
    logger.warning("Missing chest data for scoring.")
    return 50, None, "[No chest data]"


def score_shoulder(body_shoulder, shirt_shoulder):
    if body_shoulder is not None and shirt_shoulder is not None:
        diff = shirt_shoulder - body_shoulder
        if diff < -0.5:
            return (
                max(0, 100 + diff * SHOULDER_TOO_NARROW_PENALTY),
                "Shoulders Too Narrow",
                f'Shoulder: {diff:+.1f}" vs body (too narrow).',
            )
        if diff < 0.5:
            return 100, None, f'Shoulder: {diff:+.1f}" vs body (fitted).'
        if diff < SHOULDER_DROP_MAX:
            return 100, "Drop-Shoulder", f'Shoulder: {diff:+.1f}" vs body (drop-shoulder).'
        else:
            return (
                max(60, 100 - (diff - SHOULDER_DROP_MAX) * SHOULDER_VERY_OVERSIZED_PENALTY),
                "Very Oversized Shoulders",
                f'Shoulder: {diff:+.1f}" vs body (very oversized).',
            )
    logger.warning("Missing shoulder data for scoring.")
    return 50, None, "[No shoulder data]"


def score_length(body_length, shirt_length, shirt_chest):
    if body_length is not None and shirt_length is not None:
        diff = shirt_length - body_length
        if diff < LENGTH_CROPPED_MIN:
            return 50, "Cropped", f'Length: {diff:+.1f}" vs body (cropped).'
        if diff < LENGTH_SHORT_MAX:
            return 70, "Short Length", f'Length: {diff:+.1f}" vs body (short).'
        if diff < LENGTH_IDEAL_MAX:
            return 100, None, f'Length: {diff:+.1f}" vs body (ideal).'
        if diff < LENGTH_LONG_MAX:
            return 90, None, f'Length: {diff:+.1f}" vs body (long).'
        else:
            return (
                LENGTH_VERY_LONG_PENALTY,
                "Very Long",
                f'Length: {diff:+.1f}" vs body (very long).',
            )
    elif shirt_length is not None and shirt_chest is not None:
        ratio = shirt_length / shirt_chest
        bounds = [
            (1.2, 100, "Boxy Cut", f"Length: Length-to-chest ratio {ratio:.2f} (boxy cut)."),
            (1.4, 90, None, f"Length: Length-to-chest ratio {ratio:.2f} (regular)."),
            (
                float("inf"),
                70,
                "Longline Cut",
                f"Length: Length-to-chest ratio {ratio:.2f} (longline).",
            ),
        ]
        return score_by_ratio(ratio, bounds)
    logger.warning("Missing length data for scoring.")
    return 50, None, "[No length data]"


def score_hem(body_hem, shirt_hem, shirt_chest):
    if shirt_hem is not None and ((body_hem is not None) or (shirt_chest is not None)):
        if body_hem is not None:
            diff = shirt_hem - body_hem
            if diff < 0:
                return (
                    max(0, 100 - abs(diff) * HEM_TOO_TIGHT_PENALTY),
                    "Tight Waist",
                    f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body.",
                )
            if diff < HEM_FLARED_MIN:
                return 100, None, f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body."
            else:
                return 90, "Flared Hem", f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body."
        else:
            diff = shirt_hem - shirt_chest
            if diff < -HEM_BOX_CUT_MAX:
                return (
                    HEM_TAPERED_PENALTY,
                    "Tapered Waist",
                    f"Hem: {('+' if diff >= 0 else '')}{diff:.1f}\" vs chest.",
                )
            if diff < HEM_BOX_CUT_MAX:
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
                return (
                    SLEEVE_CAP_SCORE,
                    "Cap Sleeve",
                    f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm.",
                )
            if diff < SLEEVE_SHORT_MAX:
                return (
                    SLEEVE_SHORT_SCORE,
                    "Short Sleeves",
                    f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm.",
                )
            if diff < SLEEVE_IDEAL_MAX:
                return (
                    SLEEVE_IDEAL_SCORE,
                    None,
                    f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm.",
                )
            else:
                return (
                    SLEEVE_ELBOW_SCORE,
                    "Elbow-Length Sleeves",
                    f"Sleeve: {('+' if diff >= 0 else '')}{diff:.1f}\" vs body arm.",
                )
        else:
            ratio = shirt_sleeve / shirt_chest if shirt_chest else 0
            if ratio < 0.35:
                return (
                    SLEEVE_SHORT_SCORE,
                    "Short Sleeves",
                    f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}.",
                )
            if ratio > 0.5:
                return (
                    SLEEVE_ELBOW_SCORE,
                    "Elbow-Length Sleeves",
                    f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}.",
                )
            else:
                return SLEEVE_IDEAL_SCORE, None, f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}."
    logger.warning("Missing sleeve data for scoring.")
    return 50, None, "[No sleeve data]"


def score_weight(shirt_weight, scores):
    if shirt_weight is not None and isinstance(shirt_weight, (int, float)):
        wt = shirt_weight
        only_weight = all(scores.get(k, 50) == 50 for k in ASPECTS if k != "weight")
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

