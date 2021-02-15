![nbapr](img/nbapr.png)

nbapr is a python-based player rater for nba fantasy. It uses simulation rather than the typical z-score approach used by ESPN and other sites. The output is the average amount of fantasy points a player contributes to a team (or in a specific category). This information is much more useful than a sum of z-scores which are not tied to any real values. It also accounts for the fact that a player's effect on a team is capped by the bounds of being first or last in a category. Z-scores know nothing about fantasy scoring rules, so they continue to penalize or reward a player in a category beyond the practical effect the player could have on team results.

---

**Documentation**: <a href="https://sansbacon.github.io/pangadfs/">https://sansbacon.github.io/pangadfs/</a>

**Source Code**: <a href="https://github.com/sansbacon/pangadfs" target="_blank">https://github.com/sansbacon/pangadfs</a>

---

The key nbapr features are:

* **Fast**: takes advantage of pandas and numpy to run 50,000 simulations in less than 30 second.
* **Interpretable results**: nbapr ties stats to fantasy points by simulating numerous leagues of players. This is a more useful and comprehensible metric than a sum of z-scores across categories.
* **Better results**: Z-score based player raters are very sensitive to outliers and the initial selection of the player pool and tend to assign too much weight to players who dominate or tank a single category. 
* **Positional value**: future iterations of nbapr will enforce position constraints, and thus give more insight than z-scores into relative position value.
* **Pythonic**: library is easy to use and extend as long as you are familiar with data analysis in python (pandas and numpy).


## Requirements

* Python 3.8+
* pandas 1.0+
* numpy 1.19+
* requests 2.0+

## Installation

<div class="termy">

```console
$ pip install nbapr

```

</div>

## Example

### Create It

```python

# example python code

```

## License

This project is licensed under the terms of the MIT license.