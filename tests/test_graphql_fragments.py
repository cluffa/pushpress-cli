"""Every GraphQL document must define exactly the fragments it spreads.

The PushPress API rejects documents with unused fragments
("Fragment X is never used"), and missing ones are a syntax error.
"""
import re

import pytest

from pp.api import appointments, attendance, benchmarks, events, preorders, profile, schedule, workouts

MODULES = [appointments, attendance, benchmarks, events, preorders, profile, schedule, workouts]


def _documents():
    for mod in MODULES:
        for name, val in vars(mod).items():
            if isinstance(val, str) and re.search(r"^\s*(query|mutation)\s", val, re.M):
                yield f"{mod.__name__}.{name}", val


@pytest.mark.parametrize("name,doc", list(_documents()))
def test_fragments_defined_equal_spread(name, doc):
    defined = re.findall(r"fragment\s+(\w+)\s+on", doc)
    spread = set(re.findall(r"\.\.\.\s*(\w+)", doc)) - {"on"}
    assert len(defined) == len(set(defined)), f"{name}: duplicate fragment definitions"
    assert set(defined) == spread, f"{name}: defined={sorted(defined)} spread={sorted(spread)}"
