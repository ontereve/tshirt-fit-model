import yaml
from pathlib import Path


def deep_merge_dicts(base, overlay):
    """
    Merge nested dictionaries by replacing leaf values. (unchanged from before)
    """
    for key, value in overlay.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            deep_merge_dicts(base[key], value)
        else:
            base[key] = value
    return base


def apply_overlays_to_aspects(base_aspects, overlay_aspects):
    """
    For each aspect in overlay:
      - If a key ends with `_multiplier`, multiply the corresponding core key (same name without suffix).
      - If a key ends with `_offset`, add to the core key (same name without suffix).
      - If a key does not end with either suffix, replace exactly.

    Returns a new dict of merged aspects.
    """
    merged = {}

    for aspect, core_vals in base_aspects.items():
        merged_vals = core_vals.copy()
        if aspect in overlay_aspects:
            for k, v in overlay_aspects[aspect].items():
                if k.endswith("_multiplier"):
                    base_key = k[: -len("_multiplier")]
                    if base_key in merged_vals:
                        merged_vals[base_key] = merged_vals[base_key] * v
                    else:
                        # If somehow base_key doesn't exist, just set it to v
                        merged_vals[base_key] = v
                elif k.endswith("_offset"):
                    base_key = k[: -len("_offset")]
                    if base_key in merged_vals:
                        merged_vals[base_key] = merged_vals[base_key] + v
                    else:
                        merged_vals[base_key] = v
                else:
                    # No suffix: full replacement
                    merged_vals[k] = v
        merged[aspect] = merged_vals
    return merged


def apply_overlay_to_adjustments(base_adj, overlay_adj):
    """
    Similar logic for interaction_adjustments.
    """
    merged_adj = base_adj.copy()
    for k, v in overlay_adj.items():
        if k.endswith("_multiplier"):
            base_key = k[: -len("_multiplier")]
            if base_key in merged_adj:
                merged_adj[base_key] = merged_adj[base_key] * v
            else:
                merged_adj[base_key] = v
        elif k.endswith("_offset"):
            base_key = k[: -len("_offset")]
            if base_key in merged_adj:
                merged_adj[base_key] = merged_adj[base_key] + v
            else:
                merged_adj[base_key] = v
        else:
            merged_adj[k] = v
    return merged_adj


def _find_root_dir(config_dir=None):
    if config_dir is not None:
        return Path(config_dir)
    return Path.cwd()


def load_model_config(style_profile=None, config_dir=None):
    """
    Loads `config/model_config.yaml` (core) and, if provided, merges in a style overlay.

    - Overlay keys ending in `_multiplier` or `_offset` are applied to the core values, not simply replaced.
    """
    root_dir = _find_root_dir(config_dir)
    base_path = root_dir / "config" / "model_config.yaml"
    with open(base_path) as f:
        base_config = yaml.safe_load(f)

    if not style_profile:
        return base_config

    overlay_path = root_dir / "style_profiles" / f"{style_profile}.yaml"
    if not overlay_path.exists():
        return base_config

    with open(overlay_path) as f:
        overlay = yaml.safe_load(f)

    # 1) Apply overlay to aspects
    if "aspects" in overlay:
        base_config["aspects"] = apply_overlays_to_aspects(
            base_config.get("aspects", {}), overlay.get("aspects", {})
        )

    # 2) Apply overlay to scoring_params for each aspect (offsets/multipliers in scoring_params)
    if "scoring_params" in overlay:
        for aspect, overlay_vals in overlay["scoring_params"].items():
            if aspect in base_config["scoring_params"]:
                # Reconstruct that nested dict similarly
                for k, v in overlay_vals.items():
                    if k.endswith("_multiplier"):
                        base_key = k[: -len("_multiplier")]
                        base_config["scoring_params"][aspect][base_key] = (
                            base_config["scoring_params"][aspect].get(base_key, 0) * v
                        )
                    elif k.endswith("_offset"):
                        base_key = k[: -len("_offset")]
                        base_config["scoring_params"][aspect][base_key] = (
                            base_config["scoring_params"][aspect].get(base_key, 0) + v
                        )
                    else:
                        base_config["scoring_params"][aspect][k] = v

    # 3) Apply overlay to interaction_adjustments
    if "interaction_adjustments" in overlay:
        base_config["interaction_adjustments"] = apply_overlay_to_adjustments(
            base_config.get("interaction_adjustments", {}), overlay.get("interaction_adjustments", {})
        )

    # 4) Any other top‐level keys (e.g. projection_config) are fully replaced, as before
    if "projection_config" in overlay:
        base_config["projection_config"] = overlay["projection_config"]

    return base_config
