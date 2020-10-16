"""
rope_league_teams.py
A script for assigning climbers in the East Peak Rope league to teams based on their score for the first set.
written by Trevor Brown in consultation with East Peak
"""

import numpy
import pandas

# list of 5.X ratings possible
# starting at 5.10, 10 means 10- and 10.5 means 10+, etc.
climbratings = [4, 5, 6, 7, 8, 9, 10, 10.5, 11, 11.5, 12, 12.5, 13]
# dictionary of ratings of the first set of climbs (1A-1D)
# also set the upside span of each climb
# these will be used to estimate the ratings the climber can climb
# e.g. If 1A score is 15 and 1B score is 10 then upside span of 1A is
#      an estimate of the maximum rating a climber can climb on their first
#      attempt, and is estimated as the rating of 1B minus one grade, but
#      must be equal to or greater than the rating of 1A.
firstratings = {'1A': 6, '1B': 10, '1C': 10, '1D': 11.5,
                '1Au': 9, '1Bu': 11, '1Cu': 11, '1Du': 13}
# create random climb ratings for sets 3 through 8,
# insert the real preliminary ratings from set 2
sevensets = {2: [5, 8, 9, 10.5], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
for key in range(3, 9):
    # generate random ratings for climbs in this set
    # A: rating average is 5.7, mostly in the range 5.6 to 5.8
    sevensets[key].append(climbratings[min(max(0, int(round(numpy.random.normal(3, 1), 0))), len(climbratings) - 1)])
    # B: rating average is 5.9, mostly in the range 5.8 to 5.10-
    sevensets[key].append(climbratings[min(max(0, int(round(numpy.random.normal(5, 1), 0))), len(climbratings) - 1)])
    # C: rating average is 5.10+, mostly in the range 5.10- to 5.11-
    sevensets[key].append(climbratings[min(max(0, int(round(numpy.random.normal(7, 1), 0))), len(climbratings) - 1)])
    # D: rating average is 5.11+, mostly in the range 5.11- to 5.12-
    sevensets[key].append(climbratings[min(max(0, int(round(numpy.random.normal(9, 1), 0))), len(climbratings) - 1)])
    sevensets[key].sort()

try:
    testrun = False
    # load climber data
    climberdata = pandas.read_csv('./climberdata.txt', sep='\t', index_col='climber')
except FileNotFoundError:
    testrun = True
    # if there is no climber data create random climber data for testing
    data = {'climber': [], '1A': [], '1B': [], '1C': [], '1D': [], 'score1': [], 'first attempt': [], 'second attempt': [], 'third attempt': [], 'total score': []}
    for i in range(50):
        data['climber'].append(i)
        # randomly generate the highest ratings a climber can climb on first, second, and third+ attempts
        ifirst = max(0, int(round(numpy.random.normal(5, 2), 0)))
        isecond = min(ifirst + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        ithird = min(isecond + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        data['first attempt'].append(climbratings[ifirst])
        data['second attempt'].append(climbratings[isecond])
        data['third attempt'].append(max(climbratings[ithird], firstratings['1A']))
        # now use the ratings to assign the climber points for climbs 1A-1D
        for climb in ['1A', '1B', '1C', '1D']:
            if data['first attempt'][-1] >= firstratings[climb]:
                data[climb].append(15)
            elif data['second attempt'][-1] >= firstratings[climb]:
                data[climb].append(10)
            elif data['third attempt'][-1] >= firstratings[climb]:
                data[climb].append(5)
            else:
                data[climb].append(0)
        # sum up points from first set
        data['score1'].append(data['1A'][-1] + data['1B'][-1] + data['1C'][-1] + data['1D'][-1])
        # now add the scores for the 7 simulated sets
        data['total score'].append(data['score1'][-1])
        for setnumber in sevensets.keys():
            for climb in sevensets[setnumber]:
                if data['first attempt'][-1] >= climb:
                    data['total score'][-1] += 15
                elif data['second attempt'][-1] >= climb:
                    data['total score'][-1] += 10
                elif data['third attempt'][-1] >= climb:
                    data['total score'][-1] += 5

    climberdata = pandas.DataFrame.from_dict(data)
    climberdata.set_index('climber', inplace=True)

# add empty columns that will be used later
climberdata['downside first attempt'] = numpy.nan
climberdata['upside first attempt'] = numpy.nan
climberdata['median first attempt'] = numpy.nan
climberdata['downside second attempt'] = numpy.nan
climberdata['upside second attempt'] = numpy.nan
climberdata['median second attempt'] = numpy.nan
climberdata['downside third attempt'] = numpy.nan
climberdata['upside third attempt'] = numpy.nan
climberdata['median third attempt'] = numpy.nan
climberdata['estimated total score min'] = climberdata['score1']
climberdata['estimated total score median'] = climberdata['score1']
climberdata['estimated total score max'] = climberdata['score1']

# look at climbers one at a time (parse through the rows of climber data)
for climber, climberstats in climberdata.iterrows():
    # keep track of best climbs
    bestfirstclimb = None
    bestsecondclimb = None
    bestthirdclimb = None
    # go through the climbs from the first set and estimate upside and downside ratings for climber
    for climb in ['1A', '1B', '1C', '1D']:
        # get score the climber got on this climb
        score = climberdata.loc[climber, climb]
        # climber got this climb on first attempt, adjust rating span of first attempt
        if score == 15:
            # get up side and down side ratings for this climb
            downrating = firstratings[climb]
            uprating = firstratings[climb+'u']
            # check if upside rating is greater than what has already been set, if it has been set
            if numpy.isnan(climberdata.loc[climber, 'upside first attempt']) or uprating > climberdata.loc[climber, 'upside first attempt']:
                bestfirstclimb = climb
                climberdata.loc[climber, 'downside first attempt'] = downrating
                climberdata.loc[climber, 'upside first attempt'] = uprating
        # climber got this climb on second attempt, adjust rating span of second attempt
        elif score == 10:
            # get up side and down side ratings
            downrating = firstratings[climb]
            uprating = firstratings[climb+'u']
            # check if upside rating is greater than what has already been set, if it has been set
            if numpy.isnan(climberdata.loc[climber, 'upside second attempt']) or uprating > climberdata.loc[climber, 'upside second attempt']:
                bestsecondclimb = climb
                climberdata.loc[climber, 'downside second attempt'] = downrating
                climberdata.loc[climber, 'upside second attempt'] = uprating
        # climber got this climb on third+ attempt, adjust rating span of third attempt
        elif score == 5:
            # get up side and down side ratings
            downrating = firstratings[climb]
            uprating = firstratings[climb+'u']
            # check if upside rating is greater than what has already been set, if it has been set
            if numpy.isnan(climberdata.loc[climber, 'upside third attempt']) or uprating > climberdata.loc[climber, 'upside third attempt']:
                bestthirdclimb = climb
                climberdata.loc[climber, 'downside third attempt'] = downrating
                climberdata.loc[climber, 'upside third attempt'] = uprating
    # fill in any missing upside and downside ratings
    # climber has no score of 10 or 15
    if bestfirstclimb is None and bestsecondclimb is None:
        # downside is minimum climb rating
        climberdata.loc[climber, 'downside first attempt'] = 4
        # upside is one less than easiest climb
        climberdata.loc[climber, 'upside first attempt'] = 5
        # downside is minimum climb rating
        climberdata.loc[climber, 'downside second attempt'] = 4
        # upside is one less than easiest climb
        climberdata.loc[climber, 'upside second attempt'] = 5
    # climber has no score of 15, but does have a score of 10
    if bestfirstclimb is None and bestsecondclimb is not None:
        # downside is minimum climb rating
        climberdata.loc[climber, 'downside first attempt'] = 4
        # upside of first attempt is one less than easiest climb
        climberdata.loc[climber, 'upside first attempt'] = 5
    # climber has no score of 10, but does have a 15 score
    if bestfirstclimb is not None and bestsecondclimb is None:
        # set downside and upside rating to same as the best first attempt climb
        climberdata.loc[climber, 'downside second attempt'] = climberdata.loc[climber, 'downside first attempt']
        climberdata.loc[climber, 'upside second attempt'] = climberdata.loc[climber, 'upside first attempt']
    # climber has no score of 5 but does have a 10 or 15 score
    if (bestfirstclimb is not None or bestsecondclimb is not None) and bestthirdclimb is None:
        # set downside and upside rating to same as the best second attempt climb
        climberdata.loc[climber, 'downside third attempt'] = climberdata.loc[climber, 'downside second attempt']
        climberdata.loc[climber, 'upside third attempt'] = climberdata.loc[climber, 'upside second attempt']
    # set median values, rounding up
    climberdata.loc[climber, 'median first attempt'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'downside first attempt']) + climbratings.index(climberdata.loc[climber, 'upside first attempt'])) / 2))]
    climberdata.loc[climber, 'median second attempt'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'downside second attempt']) + climbratings.index(climberdata.loc[climber, 'upside second attempt'])) / 2))]
    climberdata.loc[climber, 'median third attempt'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'downside third attempt']) + climbratings.index(climberdata.loc[climber, 'upside third attempt'])) / 2))]
    # finally, estimate the downside, median and upside total scores
    for setnumber in sevensets.keys():
        for climb in sevensets[setnumber]:
            for scoretype, attempt in [('min', 'downside'), ('median', 'median'), ('max', 'upside')]:
                if climberdata.loc[climber, attempt + ' first attempt'] >= climb:
                    climberdata.loc[climber, 'estimated total score ' + scoretype] += 15
                elif climberdata.loc[climber, attempt + ' second attempt'] >= climb:
                    climberdata.loc[climber, 'estimated total score ' + scoretype] += 10
                elif climberdata.loc[climber, attempt+' third attempt'] >= climb:
                    climberdata.loc[climber, 'estimated total score ' + scoretype] += 5

# now assign the climbers to teams
# set the number of teams
numberofteams = 10
# add a column for team membership
climberdata['team'] = numpy.nan

# add climbers to teams. the idea is to balance the teams so that every
# team has about the same total downside, median and upside estimated
# total scores. this way each team has about the same odds of winning.
# first sort the climber data by score so the highest scores are first
climberdata.sort_values('estimated total score median', inplace=True, ascending=False)
# parse through climber list again, this time adding them to teams
seedteam = 0
for climber, climberstats in climberdata.iterrows():
    # first add one top ranked climber to each team, so that
    # every team is seeded with one climber to begin with
    if seedteam < 10:
        climberdata.loc[climber, 'team'] = seedteam + 1
        seedteam += 1
        continue
    # all teams now have one climber each. try adding this climber to each team
    # track the effect on total scores for adding this climber to each team
    bestteam = (numpy.nan, numpy.nan)
    for tryteam in reversed(range(1, numberofteams+1)):
        # temporarily add player to this team
        climberdata.loc[climber, 'team'] = tryteam
        # get the sum of downside, median and upside total scores for all teams
        downsidescores = []
        medianscores = []
        upsidescores = []
        for sumteam in range(1, numberofteams+1):
            teamlist = climberdata.loc[climberdata['team'] == sumteam, :]
            downsidescores.append(numpy.sum(teamlist['estimated total score min']))
            medianscores.append(numpy.sum(teamlist['estimated total score median']))
            upsidescores.append(numpy.sum(teamlist['estimated total score max']))
        # calculate the standard deviation, a measure of how different the scores are from each other,
        # the team with the lowest sum of the three standard deviations is selected
        # this will make the teams more similar, or at least more different by a smaller amount
        totalstdev = numpy.std(downsidescores) + numpy.std(medianscores) + numpy.std(upsidescores)
        # check if this total standard deviation is the lowest so far
        if numpy.isnan(bestteam[0]) or totalstdev < bestteam[1]:
            bestteam = (tryteam, totalstdev)
    # now add the climber to the best team
    climberdata.loc[climber, 'team'] = bestteam[0]

# output team stats
print('team results')
print('team\tdown\tmedian\tup', end='')
if testrun:
    print('\t"actual"')
else:
    # remove extraneous internal columns
    climberdata = climberdata[['1A', '1B', '1C', '1D', 'score1', 'team', 'estimated total score min', 'estimated total score median', 'estimated total score max']]
    print()
for team in range(1, numberofteams + 1):
    teamlist = climberdata.loc[climberdata['team'] == team, :]
    print('\t'.join([str(team),
                     str(numpy.sum(teamlist['estimated total score min'])),
                     str(numpy.sum(teamlist['estimated total score median'])),
                     str(numpy.sum(teamlist['estimated total score max']))]), end='')
    if testrun:
        print('\t' + str(numpy.sum(teamlist['total score'])))
    else:
        print()

# output hypothetical season
print(' climb ratings')
print('set#\tA\tB\tC\tD')
print('\t'.join(['1', str(firstratings['1A']), str(firstratings['1B']), str(firstratings['1C']), str(firstratings['1D'])]))
for setnumber in range(2, 9):
    print('\t'.join([str(setnumber),
                     str(sevensets[setnumber][0]),
                     str(sevensets[setnumber][1]),
                     str(sevensets[setnumber][2]),
                     str(sevensets[setnumber][3])]))

# save the processed data to file
climberdata.to_csv('./processedclimberdata.txt', sep='\t')
