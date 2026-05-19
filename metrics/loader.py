"""Metric Definitions Loader"""
from . import definitions


def register_all():
    """Register all metric definitions."""
    definitions.demo.register_all()
