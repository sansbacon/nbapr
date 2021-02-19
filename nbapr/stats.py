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


def _fetch(season: str, per_mode: str, last_n: int, timeout: float = 3.05) -> pd.DataFrame:
    """Fetches nba.com stats - does not implement vast majority of API

    Args:
        season (str): in YYYY-YY format, e.g. '2020-21'
        per_mode (st): can be 'Totals', 'PerGame', or 'Per48'
        last_n (int): limit to last_n games
        timeout (float): raise error after timeout so request won't hang

    Returns:
        pd.DataFrame

    """
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Referer': 'https://stats.nba.com/',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true'
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
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    headers = data['resultSets'][0]['headers']
    players = data['resultSets'][0]['rowSet']
    items = [dict(zip(headers, p)) for p in players]
    return pd.DataFrame(items)


def _clean_doug(df):
    """Cleans dougstats df"""

    # rename columns
    mapping = {
       'Player': 'PLAYER_NAME', 
       'Team': 'TEAM', 
       'PS': 'POS', 
       'Min': 'MIN',
       '3M': 'FG3M', 
       '3A': 'FG3A', 
       'TR': 'REB', 
       'AS': 'AST', 
       'ST': 'STL', 
       'TO': 'TOV',
       'BK': 'BLK',
    }

    df = df.rename(columns=mapping)

    # address empty rows
    df = df.dropna(thresh=3)

    # make numeric columns
    for c in df.columns[3:]:
        df.loc[:, c] = pd.to_numeric(df.loc[:, c], errors='coerce').fillna(0)

    # fix turnovers
    df['TOV'] = 0 - df['TOV']

    # add fantasy points column
    df['NBA_FANTASY_PTS'] = df['PTS'] + df['TOV'] + (1.2 * df['REB']) + (1.5 * df['AST']) + (2 * (df['STL'] + df['BLK']))   

    # add percentage & probs columns
    df = (
      df
      .assign(FG_PCT=df['FGM'] / df['FGA'])
      .assign(FT_PCT=df['FTM'] / df['FTA'])
    )
    
    df = (
      df
      .assign(WFGP=df['FG_PCT'] * (df['FGA'] / df['FGA'].sum()))
      .assign(WFTP=df['FT_PCT'] * (df['FTA'] / df['FTA'].sum()))
      .assign(probs=df['NBA_FANTASY_PTS'] / df['NBA_FANTASY_PTS'].sum())
    )
    
    # filter columns
    # need to reset index for sampling to work correctly
    wanted = ['PLAYER_NAME', 'TEAM', 'GP', 'MIN', 'FGM', 'FGA', 
              'FG_PCT', 'WFGP', 'FG3M', 'FG3A', 'FTM', 'FTA', 
              'FT_PCT', 'WFTP', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS', 'probs']

    return df.loc[:, wanted].reset_index(drop=True)


def _fetch_doug(season):
    """Gets dougstats
    
    Args:
        season (str): in YY-YY format, e.g. '20-21'

    Returns:
        pd.DataFrame

    """
    url = f'http://www.dougstats.com/{season}RD.txt'
    r = requests.get(url)
    lines = r.text.split('\n')
    headers = lines[0].split()
    results = [dict(zip(headers, line.split())) for line in lines[1:]]
    return pd.DataFrame(results)


def get_stats(season: str, per_mode: str = 'Totals', last_n: int = 0) -> pd.DataFrame:
    """Fetches stats from NBA stats API.

    Args:
        season (str): in YYYY-YY format, default '2020-21'
        per_mode (st): default 'Totals', can be 'Totals', 'PerGame', or 'Per48'
        last_n (int): limit to last_n games, default 0 (all games)

    Returns:
        pd.DataFrame

    """
    if len(season) == 7:
        df = _fetch(season, per_mode, last_n)
        return _clean_stats(df)
    else:
        df = _fetch_doug(season)
        return _clean_doug(df)


if __name__ == '__main__':
    pass
