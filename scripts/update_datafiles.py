# nbapr/scripts/update_datafiles.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import json
from pathlib import Path

from nbapr import sim
from nbapr.stats import get_stats


def run():
    """Runs update script"""
    
    mapping = {
      '8cat': ['WFGP', 'WFTP', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS'],
      '9cat': ['WFGP', 'WFTP', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS', 'TOV'],
      '9catftm': ['WFGP', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'PTS', 'TOV']
    }

    pool = get_stats(season='20-21')        

    for catname, catstats in mapping.items():
        results = sim(
            pool=pool,
            n_iterations=20000, 
            n_teams=10, 
            n_players=12,
            statscols=catstats
        )

        results = results.dropna().sort_values('pts', ascending=False)

        # address rounding issue
        results.loc[:, 'pts'] = results.loc[:, 'pts'].round(2).astype(str)

        # fix names
        names = results['player'].str.split(',', expand=True)
        results.loc[:, 'player'] = names[1].str[0].str.upper() + ' ' + names[0].str.title()

        # save to disk
        pth = Path(__file__).parent.parent / 'data' / f'player-rater-{catname}.json'
        with pth.open('w') as f:
            data = {'data': results.dropna().values.tolist()}
            json.dump(data, f)


if __name__ == '__main__':
    run()
