'''
run-fbasim.py
'''

import logging
import sys

import click
import pandas as pd
from nbapr import sim


EIGHT_CAT_STATS = ['WFGP', 'WFTP', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS']
NINE_CAT_STATS = ['WFGP', 'WFTP', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS', 'TOV']
NINE_CAT_ALT_STATS = ['WFGP', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS', 'TOV']


@click.command()
@click.option('-f', '--pool_file', type=str, help='Pool file. Can be csv or pickle.')
@click.option('-i', '--n_iterations', default=500, type=int, help='Number of iterations (leagues)')
@click.option('-n', '--n_teams', default=10, type=int, help='Number of teams in league')
@click.option('-p', '--n_players', default=10, type=int, help='Number of players on team')
@click.option('-l', '--league_type', default='9cata', type=str, help='League stat categories')
def run(pool_file, n_iterations, n_teams, n_players, league_type):
    '''
    \b
    run-fbasim.py -i 50000 -n 10 -p 12

    '''
    # get categories
    if league_type == '8cat':
        statscols = EIGHT_CAT_STATS
    elif league_type == '9cat':
        statscols = NINE_CAT_STATS
    else:
        statscols = NINE_CAT_ALT_STATS
    
    # load datafile
    try:
        pool = pd.read_csv(pool_file)
    except:
        pool = pd.read_pickle(pool_file)        
    
    # run sim with specified parameters
    results = sim(
        pool=pool, 
        n_iterations=n_iterations, 
        n_teams=n_teams, 
        n_players=n_players, 
        statscols=statscols
    )
    
    print(results)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    run()
