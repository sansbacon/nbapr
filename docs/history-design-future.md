# Inspiration and Design

nbapr was inspired by a mid-2000s article written by Dan Rosenbaum, who was then an economics professor at UNC-Greensboro. He was playing fantasy basketball for the first time and decided to simulate the results of a season to assess the value of different players. At the time, the only measure was the ESPN Player Rater, which uses z-scores to assess player value by category, and then sums those z-scores to get an overall rating.

The problem with z-scores is that they are sensitive to outliers and the initial composition of the player pool. Consider the following example for blocked shots during the 2019-20 NBA season.

| player             | bpg | btot | bpgz  | btotz |
|--------------------|-----|------|-------|-------|
| Hassan Whiteside   | 2.9 | 196  | 2.18  | 2.11  |
| Brook Lopez        | 2.4 | 163  | 0.90  | 1.09  |
| Anthony Davis      | 2.3 | 143  | 0.64  | 0.48  |
| Myles Turner       | 2.1 | 132  | 0.13  | 0.14  |
| Kristaps Porzingis | 2   | 115  | -0.13 | -0.38 |
| Rudy Gobert        | 2   | 135  | -0.13 | 0.23  |
| Mitchell Robinson  | 2   | 119  | -0.13 | -0.26 |
| LaMarcus Aldridge  | 1.6 | 87   | -1.15 | -1.24 |
| Andre Drummond     | 1.6 | 93   | -1.15 | -1.06 |
| Jaren Jackson Jr.  | 1.6 | 92   | -1.15 | -1.09 |

