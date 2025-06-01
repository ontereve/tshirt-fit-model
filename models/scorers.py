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
                retu
