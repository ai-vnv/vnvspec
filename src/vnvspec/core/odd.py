"""Operational Design Domain (ODD) model.

An :class:`ODD` describes the operating conditions under which a system
is designed to function. Dimensions can be continuous ranges, discrete
sets, or free-text descriptions.

Example:
    >>> odd = ODD(
    ...     name="highway-driving",
    ...     dimensions={
    ...         "speed_range_kmh": [60, 120],
    ...         "weather": ["clear", "rain", "fog"],
    ...         "road_type": "divided highway",
    ...     },
    ... )
    >>> odd.name
    'highway-driving'
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ODD(BaseModel):
    """Operational Design Domain specification.

    Example:
        >>> odd = ODD(
        ...     name="urban",
        ...     dimensions={"speed_range_kmh": [0, 50], "lighting": ["day", "night"]},
        ... )
        >>> "speed_range_kmh" in odd.dimensions
        True
    """

    model_config = {"frozen": True}

    name: str = Field(description="ODD name.")
    description: str = Field(default="", description="Human-readable description.")
    dimensions: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "ODD dimensions as key-value pairs. Values can be lists (discrete sets), "
            "tuples (ranges), or strings (free-text)."
        ),
    )
    source_ontology: str | None = Field(
        default=None,
        description="Source ontology for the ODD dimensions, e.g. 'bsi_pas_1883'.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary additional metadata."
    )

    def dimension_names(self) -> list[str]:
        """Return sorted list of dimension names.

        Example:
            >>> odd = ODD(name="test", dimensions={"b": [1], "a": [2]})
            >>> odd.dimension_names()
            ['a', 'b']
        """
        return sorted(self.dimensions.keys())
