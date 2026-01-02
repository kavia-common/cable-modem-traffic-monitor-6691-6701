"""ORM models package.

This package imports all ORM models so SQLAlchemy can resolve string-based
relationship targets (e.g. relationship("TrafficSample")) during mapper
configuration, regardless of import order elsewhere.
"""

from __future__ import annotations

# Import all models to ensure they are registered with SQLAlchemy's registry.
from src.models.modem import Modem  # noqa: F401
from src.models.traffic_sample import TrafficSample  # noqa: F401

__all__ = ["Modem", "TrafficSample"]
