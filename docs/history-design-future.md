# Inspiration and Design

nbapr was inspired by a mid-2000s article written by Dan Rosenbaum, who was then an economics professor at UNC-Greensboro. He was playing fantasy basketball for the first time and decided to simulate the results of a season to assess the value of different players. At the time, the only measure was the ESPN Player Rater, which uses z-scores to assess player value by category, and then sums those z-scores to get an overall rating.

The problem with z-scores is that they are sensitive to outliers and the initial composition of the player pool. Consider the following example for blocked shots during the 2019-20 NBA season, which shows how the values vary substantially by changing the composition of the player pool.

If we calculate z-scores for the entire player population, the values look like this

|              player |  blk |     blkz |
|---------------------|------|----------|
|    Hassan Whiteside | 196  | 7.16     |
|         Brook Lopez | 163  | 5.82     |
|       Anthony Davis | 143  | 5.01     |
|         Rudy Gobert | 135  | 4.68     |
|        Myles Turner | 132  | 4.56     |
|   Mitchell Robinson | 119  | 4.03     |
|  Kristaps Porzingis | 115  | 3.87     |
|        Jakob Poeltl | 95   | 3.06     |
|        JaVale McGee | 94   | 3.02     |
|    Robert Covington | 93   | 2.98     |
|      Andre Drummond | 93   | 2.98     |
|         Bam Adebayo | 93   | 2.98     |
|       Jarrett Allen | 92   | 2.94     |
|   Jaren Jackson Jr. | 92   | 2.94     |
|        Nerlens Noel | 91   | 2.90     |
|   LaMarcus Aldridge | 87   | 2.74     |
|            Mo Bamba | 86   | 2.69     |
|        Daniel Theis | 84   | 2.61     |
|         Maxi Kleber | 83   | 2.57     |
|       Dwight Howard | 79   | 2.41     |

If we limit the player pool to those who have played at least 500 minutes, the values look like this

|              player |  blk |     blkz |
|---------------------|------|----------|
|    Hassan Whiteside | 196  | 6.23     |
|         Brook Lopez | 163  | 5.01     |
|       Anthony Davis | 143  | 4.27     |
|         Rudy Gobert | 135  | 3.97     |
|        Myles Turner | 132  | 3.86     |
|   Mitchell Robinson | 119  | 3.37     |
|  Kristaps Porzingis | 115  | 3.23     |
|        Jakob Poeltl | 95   | 2.48     |
|        JaVale McGee | 94   | 2.45     |
|         Bam Adebayo | 93   | 2.41     |
|      Andre Drummond | 93   | 2.41     |
|    Robert Covington | 93   | 2.41     |
|       Jarrett Allen | 92   | 2.37     |
|   Jaren Jackson Jr. | 92   | 2.37     |
|        Nerlens Noel | 91   | 2.34     |
|   LaMarcus Aldridge | 87   | 2.19     |
|            Mo Bamba | 86   | 2.15     |
|        Daniel Theis | 84   | 2.08     |
|         Maxi Kleber | 83   | 2.04     |
|       Dwight Howard | 79   | 1.89     |

And if we limit the player pool to 1500 minutes (~20 MPG), they are as follows

|                 player |  blk |      blkz |
|------------------------|------|-----------|
|       Hassan Whiteside | 196  | 5.08      |
|            Brook Lopez | 163  | 4.04      |
|          Anthony Davis | 143  | 3.41      |
|            Rudy Gobert | 135  | 3.16      |
|           Myles Turner | 132  | 3.06      |
|     Kristaps Porzingis | 115  | 2.53      |
|         Andre Drummond | 93   | 1.83      |
|            Bam Adebayo | 93   | 1.83      |
|       Robert Covington | 93   | 1.83      |
|          Jarrett Allen | 92   | 1.80      |
|      Jaren Jackson Jr. | 92   | 1.80      |
|      LaMarcus Aldridge | 87   | 1.64      |
|           Daniel Theis | 84   | 1.55      |
|            Maxi Kleber | 83   | 1.52      |
|      Jonas Valanciunas | 76   | 1.30      |
|       Montrezl Harrell | 72   | 1.17      |
|           Steven Adams | 67   | 1.01      |
|  Giannis Antetokounmpo | 66   | 0.98      |
|            Joel Embiid | 65   | 0.95      |
|             Al Horford | 61   | 0.83      |