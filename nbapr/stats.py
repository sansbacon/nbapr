# nbapr/nbapr/stats.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import logging

import pandas as pd
import requests


logging.getLogger(__name__).addHandler(logging.NullHandler())


def _clean_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares stats from nba.com for nbapr.sim

    Args:
        df (pd.DataFrame): dataframe from nba.com stats

    Returns:
        pd.DataFrame

    """
    # filter out unwanted players
    df = df.loc[df.NBA_FANTASY_PTS >= df.NBA_FANTASY_PTS.mean(), :]

    # add percentage & probs columns
    df = (
      df
      .assign(WFGP=df['FG_PCT'] * (df['FGA'] / df['FGA'].sum()))
      .assign(WFTP=df['FT_PCT'] * (df['FTA'] / df['FTA'].sum()))
      .assign(probs=df['NBA_FANTASY_PTS'] / df['NBA_FANTASY_PTS'].sum())
    )
    
    # fix turnovers
    df['TOV'] = 0 - df['TOV']

    # filter columns
    # need to reset index for sampling to work correctly
    wanted = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'AGE', 'GP',
              'MIN', 'FGM', 'FGA', 'FG_PCT', 'WFGP', 'FG3M', 'FG3A', 'FTM', 'FTA', 
              'FT_PCT', 'WFTP', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS', 'probs']

    return df.loc[:, wanted].reset_index(drop=True)


def _fetch(season: str, per_mode: str, last_n: int) -> pd.DataFrame:
    """Fetches nba.com stats - does not implement vast majority of API

    Args:
        season (str): in YYYY-YY format, e.g. '2020-21'
        per_mode (st): can be 'Totals', 'PerGame', or 'Per48'
        last_n (int): limit to last_n games
        
    Returns:
        pd.DataFrame

    """
    headers = {
        'authority': 'stats.nba.com',
        'accept': 'application/json, text/plain, */*',
        'x-nba-stats-token': 'true',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)',
        'x-nba-stats-origin': 'stats',
        'origin': 'https://www.nba.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.nba.com/',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
    }

    params = (
        ('College', ''),
        ('Conference', ''),
        ('Country', ''),
        ('DateFrom', ''),
        ('DateTo', ''),
        ('Division', ''),
        ('DraftPick', ''),
        ('DraftYear', ''),
        ('GameScope', ''),
        ('GameSegment', ''),
        ('Height', ''),
        ('LastNGames', last_n),
        ('LeagueID', '00'),
        ('Location', ''),
        ('MeasureType', 'Base'),
        ('Month', '0'),
        ('OpponentTeamID', '0'),
        ('Outcome', ''),
        ('PORound', '0'),
        ('PaceAdjust', 'N'),
        ('PerMode', per_mode),
        ('Period', '0'),
        ('PlayerExperience', ''),
        ('PlayerPosition', ''),
        ('PlusMinus', 'N'),
        ('Rank', 'N'),
        ('Season', season),
        ('SeasonSegment', ''),
        ('SeasonType', 'Regular Season'),
        ('ShotClockRange', ''),
        ('StarterBench', ''),
        ('TeamID', '0'),
        ('TwoWay', '0'),
        ('VsConference', ''),
        ('VsDivision', ''),
        ('Weight', ''),
    )
    
    url = 'https://stats.nba.com/stats/leaguedashplayerstats'
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    headers = data['resultSets'][0]['headers']
    players = data['resultSets'][0]['rowSet']
    items = [dict(zip(headers, p)) for p in players]
    return pd.DataFrame(items)


def get_stats(season: str = '2020-21', per_mode: str = 'Totals', last_n: int = 0) -> pd.DataFrame:
    """Fetches stats from NBA stats API.

    Args:
        season (str): in YYYY-YY format, default '2020-21'
        per_mode (st): default 'Totals', can be 'Totals', 'PerGame', or 'Per48'
        last_n (int): limit to last_n games, default 0 (all games)

    Returns:
        pd.DataFrame

    """
    df = _fetch(season, per_mode, last_n)
    return _clean_stats(df)


if __name__ == '__main__':
    pass