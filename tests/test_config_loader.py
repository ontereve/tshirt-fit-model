import pytest
import yaml
from pathlib import Path
from utils.config_loader import load_model_config, deep_merge_dicts

@pytest.fixture
def base_config(tmp_path):
    base = {
        'aspects': {
            'chest': {'weight': 0.20, 'relaxed_max': 2.0},
            'length': {'weight': 0.15},
        },
        'interaction_adjustments': {
            'relaxed_heavy_bonus': 3
        }
    }
    cfg_dir = tmp_path / 'config'
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / 'model_config.yaml'
    with open(cfg_path, 'w') as f:
        yaml.safe_dump(base, f)
    return tmp_path

@pytest.fixture
def relaxed_overlay(tmp_path):
    overlay = {
        'name': 'relaxed',
        'description': 'Relaxed fit overlay',
        'aspects': {
            'chest': {'weight': 0.17, 'relaxed_max': 2.7},
            'length': {'weight': 0.17},
        },
        'interaction_adjustments': {
            'relaxed_heavy_bonus': 7
        }
    }
    style_dir = tmp_path / 'style_profiles'
    style_dir.mkdir(exist_ok=True)
    overlay_path = style_dir / 'relaxed.yaml'
    with open(overlay_path, 'w') as f:
        yaml.safe_dump(overlay, f)
    return overlay_path

def test_deep_merge_dicts_merges_correctly():
    base = {'a': 1, 'b': {'x': 10, 'y': 20}}
    overlay = {'b': {'x': 99}, 'c': 7}
    merged = deep_merge_dicts(base.copy(), overlay)
    assert merged == {'a': 1, 'b': {'x': 99, 'y': 20}, 'c': 7}

def test_overlay_loader_merges_on_top(tmp_path, base_config, relaxed_overlay):
    config = load_model_config(style_profile="relaxed", config_dir=tmp_path)
    assert config['aspects']['chest']['weight'] == 0.17
    assert config['aspects']['chest']['relaxed_max'] == 2.7
    assert config['aspects']['length']['weight'] == 0.17
    assert config['interaction_adjustments']['relaxed_heavy_bonus'] == 7

def test_loader_no_overlay_uses_base(tmp_path, base_config):
    config = load_model_config(config_dir=tmp_path)
    assert config['aspects']['chest']['weight'] == 0.20
    assert config['interaction_adjustments']['relaxed_heavy_bonus'] == 3
