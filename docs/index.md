![nbapr](img/nbapr.png)

nbapr is a python-based player rater for nba fantasy. It uses simulation rather than the typical z-score approach used by ESPN and other sites. [explain shortcomings with approach]

---

**Documentation**: <a href="https://sansbacon.github.io/pangadfs/">https://sansbacon.github.io/pangadfs/</a>

**Source Code**: <a href="https://github.com/sansbacon/pangadfs" target="_blank">https://github.com/sansbacon/pangadfs</a>

---

The key nbapr features are:

* **Fast**: takes advantage of pandas and numpy to run 50,000 simulations in less than 30 second.
* **Better results**: Z-score based player raters are very sensitive to outliers and the initial selection of the player pool and tend to overrate players who dominate a single category. nbapr ties stats to fantasy points by simulating numerous leagues of players, which is a more realistic assessment of player value. 
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