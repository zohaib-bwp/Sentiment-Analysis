"""Helpers to read model metadata JSON files saved alongside model artifacts.

Functions:
- load_metadata(model_path_or_name): return dict or None
- list_all_metadata(): return dict mapping metadata_filename -> metadata
"""
import os
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

MODELS_DIR = 'models'


def _resolve_model_path(model_path_or_name: str) -> str:
    # If user passed only a basename (no path separator), assume models dir
    if os.sep not in model_path_or_name and not model_path_or_name.startswith('./'):
        return os.path.join(MODELS_DIR, model_path_or_name)
    return model_path_or_name


def load_metadata(model_path_or_name: str) -> Optional[Dict[str, Any]]:
    """Load metadata JSON for the given model file.

    model_path_or_name may be a full path, a relative path, or a basename located in `models/`.
    Returns the parsed metadata dict, or None if not found or parse error.
    """
    try:
        model_path = _resolve_model_path(model_path_or_name)
        meta_path = model_path + '.metadata.json'
        if not os.path.exists(meta_path):
            # if passed a basename without extension, try adding .joblib
            if not model_path.endswith('.joblib'):
                alt = model_path + '.joblib'
                alt_meta = alt + '.metadata.json'
                if os.path.exists(alt_meta):
                    meta_path = alt_meta
                else:
                    return None
            else:
                return None
        with open(meta_path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as e:
        logger.warning('Failed to load metadata for %s: %s', model_path_or_name, e)
        return None


def list_all_metadata() -> Dict[str, Dict[str, Any]]:
    """Return a mapping of metadata filename -> parsed metadata for all metadata files in `models/`.
    Files that fail to parse are skipped with a warning.
    """
    out = {}
    if not os.path.isdir(MODELS_DIR):
        return out
    for fname in os.listdir(MODELS_DIR):
        if fname.endswith('.metadata.json'):
            path = os.path.join(MODELS_DIR, fname)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    out[fname] = json.load(fh)
            except Exception as e:
                logger.warning('Failed to parse metadata %s: %s', path, e)
    return out
