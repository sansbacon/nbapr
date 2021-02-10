import numpy as np
from scipy.stats import rankdata

# third dimension
n_leagues = 50

# rows in each rank operation
n_teams = 12

# rows columns in each split
n_players = 10
n_categories = 8

# create initial teams
# is ndarray with shape (n_leagues, n_players * n_teams, n_categories)
teamstats = np.random.randint(1, 10, size=n_leagues * n_teams * n_categories * n_players).reshape(n_leagues, n_teams * n_players, n_categories)

# teamarr is a 3d array 10 (arrays) x 10 (rows) x 8 (cols)
teamsums = teamstats.reshape(-1, n_players, teamstats.shape[-1]).sum(1).reshape(-1, n_teams, n_categories)

# get team ranks
teamranks = rankdata(teamsums, axis=1)

# get team scores
teamscores = teamranks.sum(axis=-1)

# get average score
teamscores.mean(axis=0)
