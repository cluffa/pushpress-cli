from __future__ import annotations

from pp.api.scores import leaderboard, history


def test_scores_re_exports():
    assert leaderboard is not None
    assert history is not None
