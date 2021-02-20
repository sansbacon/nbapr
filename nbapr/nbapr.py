# nbapr/nbapr/nbapr.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import logging
import time
from typing import Iterable, Union

import numpy as np
import pandas as pd


logging.getLogger(__name__).addHandler(logging.NullHandler())


def _timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logging.info('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


@_timeit
def _multidimensional_shifting(elements: Iterable, 
                               num_samples: int, 
                               sample_size: int, 
                               probs: Iterable) -> np.ndarray:
    """Based on https://medium.com/ibm-watson/incredibly-fast-random-sampling-in-python-baf154bd836a
    
    Args:
        elements (iterable): iterable to sample from, typically a dataframe index
        num_samples (int): the number of rows (e.g. initial population size)
        sample_size (int): the number of columns (e.g. team size)
        probs (iterable): is same size as elements

    Returns:
        ndarray: of shape (num_samples, sample_size)
        
    """
    replicated_probabilities = np.tile(probs, (num_samples, 1))
    random_shifts = np.random.random(replicated_probabilities.shape)
    random_shifts /= random_shifts.sum(axis=1)[:, np.newaxis]
    shifted_probabilities = random_shifts - replicated_probabilities
    samples = np.argpartition(shifted_probabilities, sample_size, axis=1)[:, :sample_size]
    return elements[samples]


def rankdata(a: np.ndarray, method: str = 'average', *, axis: Union[None, int] = None) -> np.ndarray:
    """Assign ranks to data, dealing with ties appropriately.
    
    Args:
        a (np.ndarray): the array of values to be ranked.
        method (str): {'average', 'min', 'max', 'dense', 'ordinal'}, optional
        axis: Union[None, int], optional
    
    Returns:
        ndarray
        Size equal to the size of `a`, containing rank scores.

    """
    # NOTE: this is from scipy 1.6.0 to avoid importing full library
    #       not a problem on local machine but slows github builds 

    if method not in ('average', 'min', 'max', 'dense', 'ordinal'):
        raise ValueError('unknown method "{0}"'.format(method))

    if axis is not None:
        a = np.asarray(a)
        if a.size == 0:
            # The return values of `normalize_axis_index` are ignored.  The
            # call validates `axis`, even though we won't use it.
            # use scipy._lib._util._normalize_axis_index when available
            np.core.multiarray.normalize_axis_index(axis, a.ndim)
            dt = np.float64 if method == 'average' else np.int_
            return np.empty(a.shape, dtype=dt)
        return np.apply_along_axis(rankdata, axis, a, method)

    arr = np.ravel(np.asarray(a))
    algo = 'mergesort' if method == 'ordinal' else 'quicksort'
    sorter = np.argsort(arr, kind=algo)

    inv = np.empty(sorter.size, dtype=np.intp)
    inv[sorter] = np.arange(sorter.size, dtype=np.intp)

    if method == 'ordinal':
        return inv + 1

    arr = arr[sorter]
    obs = np.r_[True, arr[1:] != arr[:-1]]
    dense = obs.cumsum()[inv]

    if method == 'dense':
        return dense

    # cumulative counts of each unique value
    count = np.r_[np.nonzero(obs)[0], len(obs)]

    if method == 'max':
        return count[dense]

    if method == 'min':
        return count[dense - 1] + 1

    # average method
    return .5 * (count[dense] + count[dense - 1] + 1)


@_timeit
def _create_player_points(
        pool: pd.DataFrame, 
        teams: np.ndarray,
        n_iterations: int,
        n_teams: int,
        n_players: int,
        team_points: np.ndarray
    ) -> np.ndarray:
    """Calculates playerpoints
       
    Args:
        pool (pd.DataFrame): the player pool
        statscols (Iterable[str]): the statistics columns
        teams (np.ndarray): the teams

    Returns:
        np.ndarray
        
    """

    # now need to link back to players
    players = pool.index.values

    # once we've calculated stats, can remove league dimension from teams
    # is just a 2D array of teams
    # if you flatten teampoints, get 1D array lines up with 2D teams
    teams2d = teams.reshape(n_iterations * n_teams, n_players)
    team_points1d = team_points.ravel()

    # creates array of shape (len(teams2d), len(players))
    # is effectively one hot encoder for player indexes
    # if player index 3 is on team 0, then on_team[0, 3] == 1
    on_team = (players[...,None]==teams2d[:,None,:]).any(-1).astype(int)

    # now we can calculate player points by multiplying
    # matrix of zeroes and ones with team points
    return on_team * team_points1d[:, np.newaxis]


@_timeit
def _create_teams(
        pool: pd.DataFrame, 
        n_iterations: int = 500, 
        n_teams: int = 10, 
        n_players: int = 10,
        probcol: str = 'probs'
    ) -> np.ndarray:
    """Creates initial set of teams
    
    
    Returns:
        np.ndarray of shape
          axis 0 - number of iterations
          axis 1 - number of teams in league
          axis 2 - number of players on team
    """
    # get the teams, which are represented as 3D array
    # axis 0 = number of iterations (leagues)
    # axis 1 = number of teams in league
    # axis 2 = number of players on team   
    arr = _multidimensional_shifting(
        elements=pool.index.values, 
        num_samples=n_iterations, 
        sample_size=n_teams * n_players, 
        probs=pool[probcol]
    )

    return arr.reshape(n_iterations, n_teams, n_players)


@_timeit
def _create_teamstats(
        pool: pd.DataFrame, 
        statscols: Iterable[str],
        teams: np.ndarray
    ) -> np.ndarray:
    """Calculates team statistics
       
    Args:
        pool (pd.DataFrame): the player pool
        statscols (Iterable[str]): the statistics columns
        teams (np.ndarray): the teams

    Returns:
        np.ndarray
        
    """
    # get the player stats as a 2D array
    stats_mda = pool.loc[:, statscols].values

    # now get the team stats
    # has shape (n_iterations, n_teams, n_players, len(statcols))
    team_stats = stats_mda[teams] 
    
    # sum along axis 2 to get team totals
    # has shape (n_iterations, n_teams, len(statcols))
    return np.sum(team_stats, axis=2)


@_timeit
def sim(pool: pd.DataFrame, 
        n_iterations: int = 500, 
        n_teams: int = 10, 
        n_players: int = 10,
        statscols: Iterable[str] = ('WFGP', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS'),
        probcol: str = 'probs'
        ) -> pd.DataFrame:
    """Simulates NBA fantasy season
    
    Args:
        pool (pd.DataFrame): the player pool dataframe
        n_iterations (int): number of leagues to simulate, default 500
        n_teams (int): number of teams per league, default 10
        n_players (int): number of player per team, default 10
        statscols (Iterable[str]): the stats columns
        probcol (str): the column name with probabilities for sampling

    Returns:
        pd.DataFrame with columns
           player[str], pts[float]

    """
    # get the teams, which are represented as 3D array
    # axis 0 = number of iterations (leagues)
    # axis 1 = number of teams in league
    # axis 2 = number of players in team
    teams = _create_teams(pool, n_iterations, n_teams, n_players)
    
    # stats_mda is shape(len(players), len(statcols)
    # so each row is a player's stats in those categories
    # row_index == index in the players dataframe
    team_stats_totals = _create_teamstats(pool, statscols, teams)

    # calculate ranks and sum them
    # team_ranks has same shape as team_totals (n_iterations, n_teams, len(statcols))
    team_ranks = rankdata(team_stats_totals, method='average', axis=1)

    # team_points is sum of team ranks along axis 2
    # has shape (n_iterations, n_teams)
    team_points = np.sum(team_ranks, axis=2)
    
    # now need to link back to players
    player_points = _create_player_points(pool, teams, n_iterations, n_teams, n_players, team_points)

    # have convert 0 to nan so can calculate true average
    player_points[player_points == 0] = np.nan
    player_mean = np.nanmean(player_points, axis=0)

    # return results
    return pd.DataFrame({
        'player': pool.PLAYER_NAME,
        'pos': pool.POS,
        'team': pool.TEAM, 
        'pts': player_mean
    })


if __name__ == '__main__':
    pass
