# nbapr/tests/test_stats.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import pytest

import pandas as pd
from nbapr.stats import _clean_stats, _fetch, get_stats


def test_clean_stats(pool):
    #df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_stats(pool)
    assert 'WFGP' in df.columns


def test_fetch():
    #season: str = '2020-21', per_mode: str ='Totals') -> pd.DataFrame:
    df = _fetch(season='2020-21', per_mode='Totals', last_n=0)
    assert 'FGM' in df.columns


def test_get_stats():
    #season: str = '2020-21', per_mode: str = 'Totals') -> pd.DataFrame:
    df = get_stats()
    assert 'WFGP' in df.columns
