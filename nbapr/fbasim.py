# -*- coding: utf-8 -*-
'''
fbasim.py
functions for simulating fantasy NBA season
'''

import logging
from multiprocessing import Pool
import sys

import click
import numpy as np
import pandas as pd

from nba.nbacom import Scraper, Parser
from nba.season import current_season_code


def load_data(season_code, per_mode, lastn, sincen, thresh_gp, thresh_min,
              adjust_to=False, sortcol=None, fn=None):
    '''
    Loads data from nba.com or csv file

    Args:
        season_code (str): '2017-18', etc.
        per_mode (str): 'Totals', 'PerGame', 'Per48'
        lastn (int): last number of games, default 0
        sincen (str): games since specific date, default ''
        thresh_gp (int): minimum number of games played, default 0
        thresh_min (int): minimum number of minutes played, default 0
        adjust_to (bool): make turnovers negative (for ranking purposes, may be easier)
        sortcol (str): sort, default None
        fn (str): filename of csv, default None

    Returns:
        pandas.DataFrame

    '''
    if fn:    
        logging.info('reading data from file')
        df = pd.read_csv(fn)
    else:
        logging.info('getting data from web')
        scraper = Scraper(cache_name='fbasim')
        parser = Parser()
        content = scraper.playerstats(season_code=season_code, per_mode=per_mode, last_n=lastn, date_from=sincen)
        logging.info('cleaning up dataframe')
        df = pd.DataFrame(parser.playerstats(content, per_mode))       
        df['MIN'] = df['MIN'].astype(int)
        df = df.rename(index=str, columns={"TEAM_ABBREVIATION": "TEAM"})

    # account for gp & minutes thresholds
    logging.info('applying thresholds')
    if thresh_gp and thresh_min:
        crit = (df.GP >= thresh_gp) & (df.MIN >= thresh_min)
        df = df[crit]
    elif thresh_gp:
        crit = df.GP >= thresh_gp
        df = df[crit]
    elif thresh_min:
        crit = df.MIN >= thresh_min
        df = df[crit]

    if adjust_to:
        df['TOV'] = 0 - df['TOV']

    if sortcol:
        return df.sort_values(sortcol, ascending=False)
    else:
        return df

   
def _psim(playersdf, i, chunkn, initialcols, numteams, sizeteams):
    '''
    Function to multiprocess
    
    Args:
        playersdf (DataFrame):
        i (int): simID
        chunkn (int): n for this process
        initialcols (list): str col names
        numteams (int): number of teams in league
        sizeteams (int): number of players per team
        
    '''
    # setup variables
    groupcol = ['simID', 'iterID', 'teamID']
    agg_cols_exclude = ['PLAYER_ID'] # don't want to sum player ids
    nplayers = len(playersdf)


    # preallocate teams
    # have the groupcol (simID, iterID, teamID) + the initial columns
    size = numteams * sizeteams
    teams = np.zeros(shape=(chunkn * size, len(initialcols) + len(groupcol)),
                     dtype=int)

    # this assigns simID to the first column
    teams[:, 0] = i

    # this assigns iterID
    # will have 100 repeats of 0 through n
    teams[:, 1] = np.repeat(np.arange(0, chunkn), size)

    # this assigns teamid to the third column
    # need to repeat 0-9, then tile that 100-element array n times
    teams[:, 2] = np.tile(A=np.repeat(np.arange(0, sizeteams), numteams),
                          reps=chunkn)

    # now assign players to teams
    # use size to determine the slice
    start = 0
    end = size
    for i in range(0, chunkn):
        idx = np.random.randint(0, nplayers, size)
        teams[start:end, 3:] = playersdf.values[idx, :]
        start += size
        end += size

    # setup df for teams from numpy array
    # use pandas b/c not aware of groupby in numpy
    dfteams = pd.DataFrame(teams)
    dfteams.columns = groupcol + initialcols

    # dfteamtot holds the team sums in each category
    # have to calculate FGP and FTP, if needed
    agg_dict = {k:np.sum for k in initialcols if k not in agg_cols_exclude}
    dfteamtot = dfteams.groupby(groupcol).aggregate(agg_dict)
    if 'FGM' in initialcols and 'FGA' in initialcols:
        dfteamtot['FGP'] = dfteamtot['FGM'] / dfteamtot['FGA']
    if 'FTM' in initialcols and 'FTA' in initialcols:
        dfteamtot['FTP'] = dfteamtot['FTM'] / dfteamtot['FTA']

    # figure out the stats columns - have to adjust for %
    statcols = [c for c in initialcols if c not in agg_cols_exclude]
    if 'FGM' and 'FGA' in statcols:
        statcols.append('FGP')
        statcols = [c for c in statcols if c not in ['FGM', 'FGA']]       
    if 'FTM' and 'FTA' in statcols:
        statcols.append('FTP')
        statcols = [c for c in statcols if c not in ['FTM', 'FTA']]
    
    # groupby ranking
    # TODO: this is where all the time goes, can speed up?
    # Might be faster to have one function that does all ranks
    # Can also look at inverting turnovers so can do same for all columns
    rankcols = ['{}_RK'.format(col) for col in statcols]
    for statcol, rankcol in zip(statcols, rankcols):
        if statcol == 'TOV':
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank(ascending=False)
        else:
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank()
    dfteamtot['TOT_RK'] = dfteamtot[rankcols].sum(axis=1)
    rankcols.append('TOT_RK')
    return dfteams.join(dfteamtot[rankcols], on=groupcol, how='left')
    

def parallelsim(dfpool, initialcols, n, numproc, 
                numteams=10, sizeteams=10):
    '''
    Simulate nba fantasy team using pool of workers
    
    Args:
        dfpool (DataFrame): DataFrame of playerpool
        initialcols (list): list of columns, must have int 'PLAYER_ID'
        n (int): number of iterations
        numproc (int): number of processes
        numteams (int): number of teams in league
        sizeteams (int): number of players on team

    Returns:
        DataFrame

    '''   
    # ensure relevant columns are integers (for numpy)
    dfpool.set_index('PLAYER_ID')
    playersdf = dfpool[initialcols].astype(np.int)

    with Pool(processes=numproc) as pool:
        interim = [pool.apply_async(_psim, 
                    (playersdf, i, int(n/numproc), initialcols,
                     numteams, sizeteams))
                    for i in range(numproc)]
        results = pd.concat([result.get() for result in interim]) 
    
   # calculate player mean for each category
    rankcols = [c for c in results.columns if '_RK' in c]
    rank_dict = {k:np.mean for k in rankcols}
    simdf = dfpool.join(results.groupby('PLAYER_ID')
                  .aggregate(rank_dict).round(1), on='PLAYER_ID')
    return simdf.sort_values('TOT_RK', ascending=False)


def sim(dfpool, initialcols, n, numteams=10, sizeteams=10):
    '''
    Simulate nba fantasy season
    
    Args:
        dfpool (DataFrame): DataFrame of playerpool
        initialcols (list): list of columns, must have int 'PLAYER_ID'
        n (int): number of iterations
        numteams (int): number of teams in league
        sizeteams (int): number of players on team

    Returns:
        DataFrame

    '''
    # initial setup
    logging.info('starting sim')
    dfpool.set_index('PLAYER_ID')
    size = numteams * sizeteams
    nplayers = len(dfpool)
    groupcol = ['simID', 'iterID', 'teamID']
    agg_cols_exclude = ['PLAYER_ID'] # don't want to sum player ids
    
    # ensure relevant columns are integers (for numpy)
    playersdf = dfpool[initialcols].astype(np.int)

    # preallocate teams
    # have the groupcol (simID, iterID, teamID) + the initial columns
    teams = np.zeros(shape=(n * size, len(initialcols) + len(groupcol)), dtype=int)

    # this assigns simID to the first column
    teams[:, 0] = 1

    # this assigns iterID
    # will have 100 repeats of 0 through n
    teams[:, 1] = np.repeat(np.arange(0, n), size)

    # this assigns teamid to the third column
    # need to repeat 0-9, then tile that 100-element array n times
    teams[:, 2] = np.tile(A=np.repeat(np.arange(0, sizeteams), numteams), reps=n)

    # now assign players to teams
    # use size to determine the slice
    start = 0
    end = size
    for i in range(0, n):
        idx = np.random.randint(0, nplayers, size)
        teams[start:end, 3:] = playersdf.values[idx, :]
        start += size
        end += size

    # setup df for teams from numpy array
    # use pandas b/c not aware of groupby in numpy
    dfteams = pd.DataFrame(teams)
    dfteams.columns = groupcol + initialcols

    # dfteamtot holds the team sums in each category
    # have to calculate FGP and FTP, if needed
    agg_dict = {k:np.sum for k in initialcols if k not in agg_cols_exclude}
    dfteamtot = dfteams.groupby(groupcol).aggregate(agg_dict)
    if 'FGM' in initialcols and 'FGA' in initialcols:
        dfteamtot['FGP'] = dfteamtot['FGM'] / dfteamtot['FGA']
    if 'FTM' in initialcols and 'FTA' in initialcols:
        dfteamtot['FTP'] = dfteamtot['FTM'] / dfteamtot['FTA']

    # figure out the stats columns - have to adjust for %
    statcols = [c for c in initialcols if c not in agg_cols_exclude]
    if 'FGM' and 'FGA' in statcols:
        statcols.append('FGP')
        statcols = [c for c in statcols if c not in ['FGM', 'FGA']]       
    if 'FTM' and 'FTA' in statcols:
        statcols.append('FTP')
        statcols = [c for c in statcols if c not in ['FTM', 'FTA']]
    
    # groupby ranking
    # TODO: this is where all the time goes, can speed up?
    # Might be faster to have one function that does all ranks
    # Can also look at inverting turnovers so can do same for all columns
    rankcols = ['{}_RK'.format(col) for col in statcols]
    for statcol, rankcol in zip(statcols, rankcols):
        if statcol == 'TOV':
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank(ascending=False)
        else:
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank()
    dfteamtot['TOT_RK'] = dfteamtot[rankcols].sum(axis=1)
    rankcols.append('TOT_RK')
    
    # join rank columns to teams
    results = dfteams.join(dfteamtot[rankcols], on=groupcol, how='left')
    
    # calculate player mean for each category
    rank_dict = {k:np.mean for k in rankcols}
    simdf = dfpool.join(results.groupby('PLAYER_ID').aggregate(rank_dict).round(1),
                    on='PLAYER_ID')
    return simdf.sort_values('TOT_RK', ascending=False)


def html_table(fn, df):
        '''
        Outputs an html table
        
        Args:
            fn (str): filename to save 
            df (DataFrame): the dataframe to create html from

        Returns:
            None

        '''
        page = '''<html>
                  <head>
                    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.css"/>
                    <script src="https://code.jquery.com/jquery-3.3.1.min.js" 
                      integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
                  </head>
                  <body>
                      <script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.js"></script>
                      <script type="text/javascript">
                        $(document).ready(function() {
                          $('#sim').DataTable( {
                            "iDisplayLength": 100,  
                            "order": [|idx|, 'desc'],
                            "columnDefs": [
                                {"className": "dt-center", "targets": "_all"}
                              ]
                          } );
                        } );
                      </script>
                      |TABLE|
                  </body>
                  </html>'''

        # if leave in NaN, then sort will display NaN first
        df = df.fillna(-100)
        html = df.to_html(border=0,
                          index=False,
                          classes='compact display" id = "sim')

        with open(fn, 'w') as outfile:
            outfile.write(page.replace('|TABLE|', html).replace('|idx|', str(len(df.columns) - 1)))


if __name__ == '__main__':
    pass
