'''
run-fbasim.py
'''

import logging
import sys

import click
import pandas as pd
from nbafantasy.fbasim import load_data, sim, parallelsim, html_table

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

EIGHT_CAT_RANK_COLS = ['FGP_RK', 'FTP_RK', 'FG3M_RK', 'REB_RK', 'AST_RK',
                   'STL_RK', 'BLK_RK', 'PTS_RK', 'TOT_RK']

EIGHT_CAT_INITIAL_COLS = ['PLAYER_ID', 'FGM', 'FGA', 'FTM', 'FTA', 'FG3M',
                       'REB', 'AST', 'STL', 'BLK', 'PTS']

NINE_CAT_INITIAL_COLS = ['PLAYER_ID', 'FGM', 'FGA', 'FTM', 'FTA', 'FG3M',
               'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']

NINE_CAT_RANK_COLS = ['FGP_RK', 'FTP_RK', 'FG3M_RK', 'REB_RK', 'AST_RK',
           'STL_RK', 'BLK_RK', 'TOV_RK', 'PTS_RK', 'TOT_RK']

TIM_INITIAL_COLS = ['PLAYER_ID', 'FGM', 'FGA', 'FTM', 'FG3M', 'REB',
               'AST', 'STL', 'BLK', 'TOV', 'PTS']

TIM_RANK_COLS = ['FGP_RK', 'FTM_RK', 'FG3M_RK', 'REB_RK', 'AST_RK',
           'STL_RK', 'BLK_RK', 'TOV_RK', 'PTS_RK', 'TOT_RK']


@click.command()
@click.option('--n', default=500, type=int, help='Number of Teams')
@click.option('--season_code', default='2019-20', type=str, help='YYYY-YY, e.g. 2019-20')
@click.option('--league_type', default='Tim', type=str, help='Tim, 8Cat, 9Cat')
@click.option('--thresh_min', default=0, type=int, help='Minimum minutes played')
@click.option('--thresh_gp', default=0, type=int, help='Minimum minutes played')
@click.option('--last_n', default=0, type=int, help='Last Number of Games')
@click.option('--since_n', default='', type=str, help='Stats since particular date')
@click.option('--per_mode', default='Totals', type=str, help='Totals, PerGame, Per48')
@click.option('--numteams', default=10, type=int, help='Number of teams in league')
@click.option('--sizeteams', default=10, type=int, help='Number of players on team')
@click.option('--parallel/--no_parallel', default=False, help='Use parallel processing')
@click.option('--vorp/--no_vorp', default=False, help='Compare to league average')
@click.option('--width', default=1000, type=int, help='Screen Width')
@click.option('--maxrows', default=100, type=int, help='Maximum number of rows to print')
@click.option('--maxcols', default=30, type=int, help='Maximum number of columns to print')
@click.option('--html_template', default=None, type=str, help='HTML template to use')
@click.option('--save_sim', default=None, type=str, help='File to save results')
def run(n, season_code, league_type, thresh_min, thresh_gp, last_n, since_n, per_mode, numteams,
        sizeteams, parallel, vorp, width, maxrows, maxcols, html, save_sim):
    '''
    \b
    run-fbasim.py --n=25000 --per_mode='PerGame' --parallel=4 --league_type='8Cat' --vorp
    run-fbasim.py --n=25000 --per_mode='Totals' --league_type='9Cat'
    run-fbasim.py --n=25000 --per_mode='Per48' --league_type='Tim' --thresh_min=500

    '''
    # display sim results
    if league_type == '8Cat':
        initialcols = EIGHT_CAT_INITIAL_COLS
        rk_cols = EIGHT_CAT_RANK_COLS
    elif league_type == '9Cat':
        initialcols = NINE_CAT_INITIAL_COLS
        rk_cols = NINE_CAT_RANK_COLS
    else:
        initialcols = TIM_INITIAL_COLS
        rk_cols = TIM_RANK_COLS

    logging.info('getting players')
    players = load_data(season_code=season_code,
                        per_mode=per_mode,
                        lastn=last_n,
                        sincen=since_n,
                        thresh_gp=thresh_gp,
                        thresh_min=thresh_min)
    logging.info('found {} players'.format(len(players)))

    logging.info('getting results')
    if parallel:
        results = parallelsim(players, initialcols, n, parallel, 
                              numteams, sizeteams)                             
    else:
        results = sim(players, initialcols, n, numteams, sizeteams)
    
    displaycol = ['PLAYER_NAME', 'TEAM', 'GP', 'MIN'] + rk_cols
    if vorp:
        colavg = float((numteams+1)/2)
        for col in rk_cols:
            if col == 'TOT_RK':
                results[col] = results[col] - (len(rk_cols)-1)*colavg               
            else:
                results[col] = results[col] - colavg

    if not width:
        try:
            import tkinter
            root = tkinter.Tk()
            width = root.winfo_screenwidth()
        except:
            width = 1000

    if html:
        logging.info('creating web page')
        import webbrowser
        import os
        from urllib.request import pathname2url

        html_table(html, results[displaycol])
        url = 'file:{}'.format(pathname2url(os.path.abspath(html)))
        webbrowser.open_new(url)

    logging.info('creating dataframe')
    with pd.option_context( 'display.max_rows', maxrows, 'display.max_columns', maxcols, 'display.width', width):
        print(results[displaycol].to_string())

    if save_sim:
        logging.info('saving to file')
        results[displaycol].to_csv(save_sim)


if __name__ == '__main__':
    run()
