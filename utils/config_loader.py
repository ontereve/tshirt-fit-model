import yaml
from pathlib import Path

def deep_merge_dicts(base, overlay):
    for key, value in overlay.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            deep_merge_dicts(base[key], value)
        else:
            base[key] = value
    return base

def _find_root_dir(config_dir=None):
    if config_dir is not None:
        return Path(config_dir)
    return Path.cwd()

def load_model_config(style_profile=None, config_dir=None):
    root_dir = _find_root_dir(config_dir)
    base_path = root_dir / 'config' / 'model_config.yaml'
    with open(base_path) as f:
        base_config = yaml.safe_load(f)
    if style_profile:
        overlay_path = root_dir / 'style_profiles' / f'{style_profile}.yaml'
        if overlay_path.exists():
            with open(overlay_path) as f:
                overlay = yaml.safe_load(f)
            overlay = {k: v for k, v in overlay.items() if k not in ['name', 'description']}
            deep_merge_dicts(base_config, overlay)
    return base_config
