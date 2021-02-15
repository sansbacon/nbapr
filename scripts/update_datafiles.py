# nbapr/scripts/update_datafiles.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from pathlib import Path
import pandas as pd
from nbapr import sim
from nbapr.stats import get_stats


def run():
    """Runs update script"""
    
    pool = get_stats()        

    # run sim with specified parameters
    results = sim(
        pool=pool, 
        n_iterations=500, 
        n_teams=10, 
        n_players=12
    )
    
    pth = Path(__file__).parent.parent / 'data' / 'results.csv'
    results.sort_values('pts', ascending=False).to_csv(pth, index=False)


if __name__ == '__main__':
    run()