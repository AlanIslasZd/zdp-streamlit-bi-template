"""Metric registry."""
from typing import Dict, List

from metrics.metric import Metric

_REGISTRY: Dict[str, Metric] = {}


def register(metric: Metric) -> None:
    """Register a metric. Idempotent — re-registering the same key is a no-op."""
    if metric.key in _REGISTRY:
        return
    _REGISTRY[metric.key] = metric


def _get(key: str) -> Metric:
    if key not in _REGISTRY:
        raise KeyError(f"Metric '{key}' not registered. Available: {sorted(_REGISTRY.keys())}")
    return _REGISTRY[key]


def get_validated(key: str, required_configs: List[str]) -> Metric:
    """Look up metric and validate required configs are not None."""
    metric = _get(key)
    missing = [cfg for cfg in required_configs if getattr(metric, cfg) is None]
    if missing:
        raise TypeError(
            f"Metric '{key}' is missing required configs: {missing}. "
            f"Add these when registering in metrics/definitions/."
        )
    return metric


def list_keys() -> list:
    return sorted(_REGISTRY.keys())
