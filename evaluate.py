"""
evaluate.py
Evaluates t-shirt fit for each garment using the refined `score_fit` model,
with optional style profile overlay.
"""

import os
import logging
import argparse
import pandas as pd
from tabulate import tabulate
from utils.data_loader import load_body_measurements, load_shirt_data
from models.fit_model import score_fit, bulk_projection_profile
from utils.config_loader import load_model_config
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def score_shirts(body, shirts, style_profile=None):
    """
    Scores each shirt for both core, bulk, and optional style profiles.
    Returns a list of dicts, one per shirt.
    """
    # Determine project‐root so config_loader knows where to find “config/model_config.yaml” etc.
    root_dir = Path(__file__).resolve().parent
    # Preload base config (for “core”) and style config if requested
    core_config = load_model_config(config_dir=root_dir)
    if style_profile:
        style_config = load_model_config(style_profile=style_profile, config_dir=root_dir)
    else:
        style_config = None

    bulk_profile = bulk_projection_profile(body)
    results = []

    for idx, row in shirts.iterrows():
        shirt = row.to_dict()

        # Core fit
        core_result = score_fit(body, shirt)
        # Bulk fit
        bulk_result = score_fit(bulk_profile, shirt)

        row_data = {
            "ShirtName": shirt.get("ShirtName", f"Shirt_{idx}"),
            "CoreFitScore": core_result["FitScore"],
            "CoreConfidence": core_result["Confidence"],
            "CoreTags": "; ".join(core_result.get("Tags", [])),
            "CoreRationale": core_result.get("Rationale", ""),
            "BulkFitScore": bulk_result["FitScore"],
            "BulkConfidence": int(round(bulk_result["Confidence"] * 0.85)),
            "BulkTags": "; ".join(bulk_result.get("Tags", [])),
            "BulkRationale": bulk_result.get("Rationale", ""),
            # Legacy keys for existing tests:
            "FitScore": core_result["FitScore"],
            "Confidence": core_result["Confidence"],
        }

        if style_config:
            # --- BEGIN style-overlay injection ---
            import models.fit_model as fit_model_mod
            import models.scorers as scorers_mod

            # 1) Inject style_config into fit_model.py globals
            fit_model_mod.MODEL_CONFIG = style_config
            fit_model_mod.ASPECTS = list(style_config["aspects"].keys())
            fit_model_mod.SCORING_PARAMS = style_config["scoring_params"]
            fit_model_mod.INTERACTION_ADJUSTMENTS = style_config["interaction_adjustments"]
            fit_model_mod.PROJECTION_CONFIG = style_config.get("projection_config", {})
            fit_model_mod.WEIGHTS = {
                k: v["weight"] for k, v in style_config["aspects"].items()
            }
            fit_model_mod.ASPECT_SCORERS = {
                aspect: {
                    "scorer": aspect_cfg["scorer"],
                    "body_field": aspect_cfg["body_field"],
                    "shirt_field": aspect_cfg["shirt_field"],
                    "weight": aspect_cfg["weight"],
                    "params": style_config["scoring_params"].get(aspect, {}),
                }
                for aspect, aspect_cfg in style_config["aspects"].items()
            }
            fit_model_mod.ASPECTS_NEED_CHEST = {
                aspect
                for aspect, cfg in style_config["aspects"].items()
                if cfg.get("needs_chest", False)
            }

            # 2) Also inject style_config into scorers.py globals
            scorers_mod.config = style_config
            scorers_mod.scoring_params = style_config["scoring_params"]
            scorers_mod.adjustments = style_config["interaction_adjustments"]

            # 3) Now call score_fit(...) (it will use the *new* style_config everywhere)
            style_result = score_fit(body, shirt)
            row_data.update({
                "StyleFitScore": style_result.get("FitScore"),
                "StyleConfidence": style_result.get("Confidence"),
                "StyleTags": "; ".join(style_result.get("Tags", [])),
                "StyleRationale": style_result.get("Rationale", ""),
                "StyleProfile": style_profile,
            })

            # 4) Reset fit_model.py globals back to core_config
            fit_model_mod.MODEL_CONFIG = core_config
            fit_model_mod.ASPECTS = list(core_config["aspects"].keys())
            fit_model_mod.SCORING_PARAMS = core_config["scoring_params"]
            fit_model_mod.INTERACTION_ADJUSTMENTS = core_config["interaction_adjustments"]
            fit_model_mod.PROJECTION_CONFIG = core_config.get("projection_config", {})
            fit_model_mod.WEIGHTS = {
                k: v["weight"] for k, v in core_config["aspects"].items()
            }
            fit_model_mod.ASPECT_SCORERS = {
                aspect: {
                    "scorer": aspect_cfg["scorer"],
                    "body_field": aspect_cfg["body_field"],
                    "shirt_field": aspect_cfg["shirt_field"],
                    "weight": aspect_cfg["weight"],
                    "params": core_config["scoring_params"].get(aspect, {}),
                }
                for aspect, aspect_cfg in core_config["aspects"].items()
            }
            fit_model_mod.ASPECTS_NEED_CHEST = {
                aspect
                for aspect, cfg in core_config["aspects"].items()
                if cfg.get("needs_chest", False)
            }

            # 5) Reset scorers.py globals back to core_config as well
            scorers_mod.config = core_config
            scorers_mod.scoring_params = core_config["scoring_params"]
            scorers_mod.adjustments = core_config["interaction_adjustments"]
            # --- END style-overlay injection ---

        results.append(row_data)

    return results


def evaluate_fit(body_path, shirt_path, out_path, style_profile=None):
    body = load_body_measurements(body_path)
    shirts = load_shirt_data(shirt_path)
    results = score_shirts(body, shirts, style_profile=style_profile)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = pd.DataFrame(results)

    # Sort by the chosen score
    if style_profile:
        df = df.sort_values(by="StyleFitScore", ascending=False)
    else:
        df = df.sort_values(by="CoreFitScore", ascending=False)

    df.to_csv(out_path, index=False)
    return df.to_dict(orient="records")


def main():
    # Show full strings in pandas output (no truncation)
    pd.set_option("display.max_colwidth", None)

    parser = argparse.ArgumentParser(
        description="Evaluate t-shirt fits with optional style profile overlay."
    )
    parser.add_argument(
        "--body",
        type=str,
        default="data/body_measurements.csv",
        help="Path to body measurements CSV",
    )
    parser.add_argument(
        "--shirts",
        type=str,
        default="data/shirt_data.csv",
        help="Path to shirts CSV",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="outputs/fit_results.csv",
        help="Path to output CSV",
    )
    parser.add_argument(
        "--style_profile",
        type=str,
        default=None,
        help="Style profile overlay (do not include .yaml extension)",
    )
    args = parser.parse_args()

    # Check input files
    if not os.path.exists(args.body) or not os.path.exists(args.shirts):
        print("Missing input data. Please check the provided paths.")
        return

    results = evaluate_fit(
        args.body, args.shirts, args.out, style_profile=args.style_profile
    )

    # Build display DataFrame depending on style_profile
    df_display = pd.DataFrame(results)
    if args.style_profile:
        # Show Core and Style columns
        display_cols = [
            ("ShirtName", "Sh irt name"),
            ("CoreFitScore", "Core Score"),
            ("CoreConfidence", "Core Conf."),
            ("StyleFitScore", "Style Score"),
            ("StyleConfidence", "Style Conf."),
        ]
    else:
        # Show Core and Bulk columns
        display_cols = [
            ("ShirtName", "Shirt name"),
            ("CoreFitScore", "Score"),
            ("CoreConfidence", "Conf."),
            ("BulkFitScore", "Bulk Score"),
            ("BulkConfidence", "Bulk Conf."),
        ]

    # Subset and rename columns for console display
    try:
        display_df = df_display[[c[0] for c in display_cols]].copy()
        display_df.columns = [c[1] for c in display_cols]
    except KeyError:
        # If expected columns are missing, fallback to printing all
        print(tabulate(df_display, headers="keys", tablefmt="fancy_grid", showindex=False))
        return

    # Format numeric columns to two decimals if present
    for col in display_df.columns[1:]:
        display_df[col] = display_df[col].apply(
            lambda x: f"{float(x):.2f}" if x not in ["", None, "nan"] and str(x) != "" else ""
        )

    print("\nFitting Results:\n")
    print(tabulate(display_df, headers="keys", tablefmt="fancy_grid", showindex=False))


if __name__ == "__main__":
    main()
