rope_league_teams.py  
A script for assigning climbers in the East Peak Rope league to teams based on their score for the first set.
written by Trevor Brown in consultation with East Peak

Climber data is read in from a tab delimited .txt file, the following headers are required (case sensitive):
- climber : anonymized climber id  
- 1A, 1B, 1C, 1D : scores for the climbs in the first set  
- score1 : total score for first set

If climberdata.txt is not present then randomized climber data is generated for testing. The final results are output
to the file processedclimberdata.txt.

The script first estimates the minimum, median, and maximum total score each climber might get in the season.
This is done by estimating the 5.X climb rating each climber can climb on their first, second and third+ attempts,
the estimate is based on their scores for the first set. A hypothetical season is simulated by generating reasonable,
but random, climb ratings for set numbers 2 through 8. Each climber is then assigned minimum, median, and maximum
probable scores for the hypothetical season.

Climbers are then assigned to teams. The teams are balanced as much as is possible so that each team has about the
same sum of minimum, median, and maximum total scores. This is done by first adding one of the top climbers to each
team, and then adding the rest of the climbers to teams in order of their estimated total score. Each climber is
assigned to a team based on how well they balance out their team's total probable score in comparison to the other teams.

