import math
import logging

logger = logging.getLogger(__name__)


def score_by_ratio(ratio, bounds):
    for upper, score, tag, rationale in bounds:
        if ratio < upper:
            return score, tag, rationale
    last = bounds[-1]
    return last[1], last[2], last[3]


def score_chest(body_chest, shirt_chest):
    # Dynamically import scoring params to avoid circular import at top-level
    from models.fit_model import SCORING_PARAMS as _scoring_params
    chest = _scoring_params["chest"]

    if body_chest is not None and shirt_chest is not None:
        chest_diff = shirt_chest - body_chest
        if chest_diff < -0.5:
            return (
                max(0, 100 + chest_diff * chest["too_tight_penalty"]),
                "Too Tight",
                f'Chest: {chest_diff:+.1f}" vs body (tight).',
            )
        if chest_diff < 0:
            return (
                max(0, 100 + chest_diff * chest["slim_penalty"]),
                "Slim Fit",
                f'Chest: {chest_diff:+.1f}" vs body (slim).',
            )
        if chest_diff < 0.5:
            return 100, None, f'Chest: {chest_diff:+.1f}" vs body (close fit).'
        if chest_diff < chest["relaxed_max"]:
            return 100, "Relaxed Fit", f'Chest: {chest_diff:+.1f}" vs body (relaxed).'
        if chest_diff < chest["oversized_max"]:
            return 95, "Oversized", f'Chest: {chest_diff:+.1f}" vs body (oversized).'
        if chest_diff < chest["comically_oversized_max"]:
            return (
                85 - (chest_diff - chest["oversized_max"]) * chest["very_oversized_penalty"],
                "Very Oversized",
                f'Chest: {chest_diff:+.1f}" vs body (very oversized).',
            )
        return (
            70 - (chest_diff - chest["comically_oversized_max"]) * chest["very_oversized_penalty"],
            "Comically Oversized",
            f'Chest: {chest_diff:+.1f}" vs body (comically oversized).',
        )

    logger.warning("Missing chest data for scoring.")
    return 50, None, "[No chest data]"


def score_shoulder(body_shoulder, shirt_shoulder):
    from models.fit_model import SCORING_PARAMS as _scoring_params
    shoulder = _scoring_params["shoulder"]

    if body_shoulder is not None and shirt_shoulder is not None:
        diff = shirt_shoulder - body_shoulder
        if diff < -0.5:
            return (
                max(0, 100 + diff * shoulder["too_narrow_penalty"]),
                "Shoulders Too Narrow",
                f'Shoulder: {diff:+.1f}" vs body (too narrow).',
            )
        if diff < 0.5:
            return 100, None, f'Shoulder: {diff:+.1f}" vs body (fitted).'
        if diff < shoulder["drop_max"]:
            return 100, "Drop-Shoulder", f'Shoulder: {diff:+.1f}" vs body (drop-shoulder).'
        return (
            max(60, 100 - (diff - shoulder["drop_max"]) * shoulder["very_oversized_penalty"]),
            "Very Oversized Shoulders",
            f'Shoulder: {diff:+.1f}" vs body (very oversized).',
        )

    logger.warning("Missing shoulder data for scoring.")
    return 50, None, "[No shoulder data]"


def score_length(body_length, shirt_length, shirt_chest):
    from models.fit_model import SCORING_PARAMS as _scoring_params
    length = _scoring_params["length"]

    if body_length is not None and shirt_length is not None:
        diff = shirt_length - body_length
        if diff < length["cropped_min"]:
            return 50, "Cropped", f'Length: {diff:+.1f}" vs body (cropped).'
        if diff < length["short_max"]:
            return 70, "Short Length", f'Length: {diff:+.1f}" vs body (short).'
        if diff < length["ideal_max"]:
            return 100, None, f'Length: {diff:+.1f}" vs body (ideal).'
        if diff < length["long_max"]:
            return 90, None, f'Length: {diff:+.1f}" vs body (long).'
        return (
            length["very_long_penalty"],
            "Very Long",
            f'Length: {diff:+.1f}" vs body (very long).',
        )

    elif shirt_length is not None and shirt_chest is not None:
        ratio = shirt_length / shirt_chest
        bounds = _scoring_params["length"]["fallback_ratio_bounds"]
        return score_by_ratio(ratio, bounds)

    logger.warning("Missing length data for scoring.")
    return 50, None, "[No length data]"


def score_hem(body_hem, shirt_hem, shirt_chest):
    from models.fit_model import SCORING_PARAMS as _scoring_params
    hem = _scoring_params["hem"]

    if shirt_hem is not None and ((body_hem is not None) or (shirt_chest is not None)):
        if body_hem is not None:
            diff = shirt_hem - body_hem
            if diff < 0:
                return (
                    max(0, 100 - abs(diff) * hem["too_tight_penalty"]),
                    "Tight Waist",
                    f'Hem: {diff:+.1f}" vs body.',
                )
            if diff < hem["flared_min"]:
                return 100, None, f'Hem: {diff:+.1f}" vs body.'
            return 90, "Flared Hem", f'Hem: {diff:+.1f}" vs body.'
        else:
            diff = shirt_hem - shirt_chest
            if diff < -hem["box_cut_max"]:
                return hem["tapered_penalty"], "Tapered Waist", f'Hem: {diff:+.1f}" vs chest.'
            if diff < hem["box_cut_max"]:
                return 100, None, f'Hem: {diff:+.1f}" vs chest.'
            return 90, "Boxy Cut", f'Hem: {diff:+.1f}" vs chest.'

    logger.warning("Missing hem data for scoring.")
    return 50, None, "[No hem data]"


def score_sleeve(body_sleeve, shirt_sleeve, shirt_chest):
    from models.fit_model import SCORING_PARAMS as _scoring_params
    sleeve = _scoring_params["sleeve"]

    if shirt_sleeve is not None:
        if body_sleeve is not None:
            diff = shirt_sleeve - body_sleeve
            if diff < sleeve["cap_min"]:
                return sleeve["cap_score"], "Cap Sleeve", f'Sleeve: {diff:+.1f}" vs body arm.'
            if diff < sleeve["short_max"]:
                return sleeve["short_score"], "Short Sleeves", f'Sleeve: {diff:+.1f}" vs body arm.'
            if diff < sleeve["ideal_max"]:
                return sleeve["ideal_score"], None, f'Sleeve: {diff:+.1f}" vs body arm.'
            return (
                sleeve["elbow_score"],
                "Elbow-Length Sleeves",
                f'Sleeve: {diff:+.1f}" vs body arm.',
            )
        else:
            ratio = shirt_sleeve / shirt_chest if shirt_chest else 0
            if ratio < 0.35:
                return (
                    sleeve["short_score"],
                    "Short Sleeves",
                    f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}.",
                )
            if ratio > 0.5:
                return (
                    sleeve["elbow_score"],
                    "Elbow-Length Sleeves",
                    f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}.",
                )
            return sleeve["ideal_score"], None, f"Sleeve: Sleeve-to-chest ratio {ratio:.2f}."

    logger.warning("Missing sleeve data for scoring.")
    return 50, None, "[No sleeve data]"


def score_weight(shirt_weight, scores, aspects):
    from models.fit_model import SCORING_PARAMS as _scoring_params
    weight = _scoring_params["weight"]

    if shirt_weight is not None and isinstance(shirt_weight, (int, float)):
        wt = shirt_weight
        only_weight = all(scores.get(k, 50) == 50 for k in aspects if k != "weight")
        if wt < weight["light_max"]:
            score = 42 if only_weight else weight["light_score"]
            tag = "Lightweight"
        elif wt < weight["mid_max"]:
            score = weight["mid_score"]
            tag = "Midweight"
        elif wt < weight["heavy_max"]:
            score = weight["heavy_score"]
            tag = "Heavyweight"
        else:
            score = weight["very_heavy_score"]
            tag = "Very Heavyweight"
        rationale = f"Weight: {wt:.1f} oz (ideal is 5–6 oz for vintage)."
        return score, tag, rationale

    logger.warning("Missing shirt weight data for scoring.")
    return 50, None, "[No shirt weight data]"


def adjust_for_oversize_weight(tags, shirt_weight, fit_score):
    from models.fit_model import INTERACTION_ADJUSTMENTS as _adjustments

    if "Comically Oversized" in tags and shirt_weight and shirt_weight < 5.0:
        fit_score = max(0, fit_score - 10)
        logger.info(
            f"Applied harsh penalty for very oversized lightweight shirt (weight: {shirt_weight})."
        )
    elif ("Oversized" in tags or "Very Oversized" in tags) and shirt_weight:
        if shirt_weight >= 6.0:
            fit_score = min(100, fit_score + _adjustments["oversized_heavy_bonus"])
        elif shirt_weight < 4.5:
            fit_score = max(0, fit_score - _adjustments["oversized_light_penalty"] * 2)

    if "Relaxed Fit" in tags and shirt_weight and shirt_weight >= 6.5:
        fit_score = min(100, fit_score + _adjustments["relaxed_heavy_bonus"])

    if "Slim Fit" in tags and shirt_weight and shirt_weight < 4.5:
        fit_score = max(0, fit_score - _adjustments["slim_light_penalty"])

    if "Comically Oversized" in tags and fit_score > 70:
        fit_score = 70
    elif "Very Oversized" in tags and fit_score > 85:
        fit_score = 85

    return fit_score
