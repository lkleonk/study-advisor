"""Degree registry.

Each supported degree program lives in its own package exposing a
``DegreeDefinition`` (prompt fragments, rules catalogue, and deterministic
study-plan validator). Sessions are bound to exactly one degree id; the LLM
never chooses the degree.
"""

from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.bsc_bioinformatik import DEGREE as BSC_BIOINFORMATIK
from app.domain.degrees.bsc_informatik import DEGREE as BSC_INFORMATIK
from app.domain.degrees.bsc_physik import DEGREE as BSC_PHYSIK
from app.domain.degrees.msc_data_science import DEGREE as MSC_DATA_SCIENCE
from app.domain.degrees.msc_informatik import DEGREE as MSC_INFORMATIK
from app.domain.degrees.msc_physik import DEGREE as MSC_PHYSIK


_DEGREES: dict[str, DegreeDefinition] = {
    MSC_INFORMATIK.id: MSC_INFORMATIK,
    MSC_DATA_SCIENCE.id: MSC_DATA_SCIENCE,
    BSC_INFORMATIK.id: BSC_INFORMATIK,
    BSC_PHYSIK.id: BSC_PHYSIK,
    BSC_BIOINFORMATIK.id: BSC_BIOINFORMATIK,
    MSC_PHYSIK.id: MSC_PHYSIK,
}

DEFAULT_DEGREE_ID = MSC_INFORMATIK.id


def list_degrees() -> list[DegreeDefinition]:
    return list(_DEGREES.values())


def is_valid_degree(degree_id: str) -> bool:
    return degree_id in _DEGREES


def get_degree(degree_id: str) -> DegreeDefinition:
    try:
        return _DEGREES[degree_id]
    except KeyError:
        raise ValueError(f"Unknown degree id: {degree_id!r}") from None


def get_degree_or_default(degree_id: str | None) -> DegreeDefinition:
    if degree_id and degree_id in _DEGREES:
        return _DEGREES[degree_id]
    return _DEGREES[DEFAULT_DEGREE_ID]
