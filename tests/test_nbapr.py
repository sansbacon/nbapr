# nbapr/tests/test_nbapr.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import numpy as np
import pytest

from nbapr.nbapr import _create_teams, _create_teamstats


def test_create_teams(clean_pool):
    """Tests _create_teams"""
    teams = _create_teams(clean_pool)
    assert isinstance(teams, np.ndarray)


def test_create_teamstats(clean_pool):
    """Tests _create_teamstats"""
    statscols = ('WFGP', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS', 'TOV')
    teams = _create_teams(clean_pool)
    ts = _create_teamstats(clean_pool, statscols, teams)
    assert isinstance(ts, np.ndarray)


@pytest.mark.skip
def test_create_player_points(clean_pool):
    """
    (
        pool: pd.DataFrame, 
        teams: np.ndarray,
        n_iterations: int,
        n_teams: int,
        n_players: int,
        team_points: np.ndarray
    ) -> np.ndarray:
    """
    teams = _create_teams(clean_pool)


@pytest.mark.skip
def test_sim():
    """
        pool: pd.DataFrame, 
        n_iterations: int = 500, 
        n_teams: int = 10, 
        n_players: int = 10,
        statscols: Iterable[str] = ('WFGP', 'WFTP', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS'),
        probcol: str = 'probs'
        ) -> pd.DataFrame:
    """
    assert True
