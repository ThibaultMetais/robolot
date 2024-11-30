import pandas as pd
import pytest

from robolot.engine import CoincheEngine

@pytest.mark.parametrize(
    ("memory", "bid_value", "bid_color", "has_coinched", "has_surcoinched", "result"),
    [
         (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [80, 100],
                "bid_color": ["spades", "hearts"],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            90,
            "clubs",
            0,
            0,
            False
         ),
         (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [80, 100],
                "bid_color": ["spades", "hearts"],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            110,
            "clubs",
            0,
            0,
            True
         ),
         (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [80, 100],
                "bid_color": ["spades", "hearts"],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            115,
            "clubs",
            0,
            0,
            False
         )
    ]
)
def test_check_bid_validity__bid(
    memory,
    bid_value,
    bid_color,
    has_coinched,
    has_surcoinched,
    result
):
    assert CoincheEngine._check_bid_validity(
        memory=memory,
        player_bid_value=bid_value,
        player_bid_color=bid_color,
        has_coinched=has_coinched,
        has_surcoinched=has_surcoinched
    ) is result


@pytest.mark.parametrize(
    ("memory", "bid_value", "bid_color", "has_coinched", "has_surcoinched", "result"),
    [
        (
            pd.DataFrame({
                "player_index": [1, 2],
                "team_index": [1, 0],
                "bid_value": [None, None],
                "bid_color": [None, None],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            None,
            None,
            1,
            0,
            False
        ),
        (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [None, 80],
                "bid_color": [None, "hearts"],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            None,
            None,
            1,
            0,
            True
        )
    ]
)
def test_check_bid_validity__coinche(
    memory,
    bid_value,
    bid_color,
    has_coinched,
    has_surcoinched,
    result
):
    assert CoincheEngine._check_bid_validity(
        memory=memory,
        player_bid_value=bid_value,
        player_bid_color=bid_color,
        has_coinched=has_coinched,
        has_surcoinched=has_surcoinched
    ) is result


@pytest.mark.parametrize(
    ("memory", "bid_value", "bid_color", "has_coinched", "has_surcoinched", "result"),
    [
        (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [None, None],
                "bid_color": [None, None],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            None,
            None,
            0,
            1,
            False
        ),
        (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [None, 80],
                "bid_color": [None, "hearts"],
                "has_coinched": [0, 0],
                "has_surcoinched": [0, 0]
            }),
            None,
            None,
            0,
            1,
            False
        ),
        (
            pd.DataFrame({
                "player_index": [0, 1],
                "team_index": [0, 1],
                "bid_value": [80, None],
                "bid_color": ["hearts", None],
                "has_coinched": [0, 1],
                "has_surcoinched": [0, 0]
            }),
            None,
            None,
            0,
            1,
            True
        )
    ]
)
def test_check_bid_validity__surcoinche_without_previous_bid(
    memory,
    bid_value,
    bid_color,
    has_coinched,
    has_surcoinched,
    result
):
    assert CoincheEngine._check_bid_validity(
        memory=memory,
        player_bid_value=bid_value,
        player_bid_color=bid_color,
        has_coinched=has_coinched,
        has_surcoinched=has_surcoinched
    ) is result