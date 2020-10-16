import numpy
import pandas

# list of 5.X ratings possible
climbratings = [4, 5, 6, 7, 8, 9, 10, 10.5, 11, 11.5, 12, 12.5, 13]
# dictionary of ratings of the first set of climbs (1A-1D)
# also set the upside span of each climb
# these will be used to estimate the ratings the climber can climb
# e.g. If 1A score is 15 and 1B score is 10 then upside span of 1A is
#      an estimate of the maximum rating a climber can climb on their first
#      attempt, and is estimated as the rating of 1B minus one grade, but
#      must be equal to or greater than the rating of 1A.
firstratings = {'1A': 6, '1B': 9, '1C': 10, '1D': 11.5,
                '1Au': 9, '1Bu': 9, '1Cu': 11, '1Du': 13}
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
    # load climber data
    climberdata = pandas.read_csv('./climberdata.txt', sep='\t', index_col='Climber')
except FileNotFoundError:
    # if there is no climber data create random climber data for testing
    data = {'Climber': [], 'first': [], 'second': [], 'third': [], '1A': [], '1B': [], '1C': [], '1D': [], 'score 1': [], 'score all': []}
    for i in range(1000):
        data['Climber'].append(i)
        # randomly generate the highest ratings a climber can climb on first, second, and third+ attempts
        ifirst = max(0, int(round(numpy.random.normal(5, 2), 0)))
        isecond = min(ifirst + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        ithird = min(isecond + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        data['first'].append(climbratings[ifirst])
        data['second'].append(climbratings[isecond])
        data['third'].append(max(climbratings[ithird], firstratings['1A']))
        # now use the ratings to assign the climber points for climbs 1A-1D
        for climb in ['1A', '1B', '1C', '1D']:
            if data['first'][-1] >= firstratings[climb]:
                data[climb].append(15)
            elif data['second'][-1] >= firstratings[climb]:
                data[climb].append(10)
            elif data['third'][-1] >= firstratings[climb]:
                data[climb].append(5)
            else:
                data[climb].append(0)
        # sum up points from first set
        data['score 1'].append(data['1A'][-1] + data['1B'][-1] + data['1C'][-1] + data['1D'][-1])
        # now add the scores for the 7 simulated sets
        data['score all'].append(data['score 1'][-1])
        for setnumber in sevensets.keys():
            for climb in sevensets[setnumber]:
                if data['first'][-1] >= climb:
                    data['score all'][-1] += 15
                elif data['second'][-1] >= climb:
                    data['score all'][-1] += 10
                elif data['third'][-1] >= climb:
                    data['score all'][-1] += 5

    climberdata = pandas.DataFrame.from_dict(data)
climberdata.set_index('Climber', inplace=True)

# add empty columns that will be used later
climberdata['down first'] = numpy.nan
climberdata['up first'] = numpy.nan
climberdata['median first'] = numpy.nan
climberdata['down second'] = numpy.nan
climberdata['up second'] = numpy.nan
climberdata['median second'] = numpy.nan
climberdata['down third'] = numpy.nan
climberdata['up third'] = numpy.nan
climberdata['median third'] = numpy.nan
climberdata['estimated score all down'] = climberdata['score 1']
climberdata['estimated score all median'] = climberdata['score 1']
climberdata['estimated score all up'] = climberdata['score 1']

# look at climbers one at a time (parse through the rows of climber data)
for climber, climberstats in climberdata.iterrows():
    # keep track of best climbs
    bestfirstclimb = None
    bestsecondclimb = None
    bestthirdclimb = None
    lowestnotclimbed = None
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
            if numpy.isnan(climberdata.loc[climber, 'up first']) or uprating > climberdata.loc[climber, 'up first']:
                bestfirstclimb = climb
                climberdata.loc[climber, 'down first'] = downrating
                climberdata.loc[climber, 'up first'] = uprating
        # climber got this climb on second attempt, adjust rating span of second attempt
        elif score == 10:
            # get up side and down side ratings
            downrating = firstratings[climb]
            uprating = firstratings[climb+'u']
            # check if upside rating is greater than what has already been set, if it has been set
            if numpy.isnan(climberdata.loc[climber, 'up second']) or uprating > climberdata.loc[climber, 'up second']:
                bestsecondclimb = climb
                climberdata.loc[climber, 'down second'] = downrating
                climberdata.loc[climber, 'up second'] = uprating
        # climber got this climb on third+ attempt, adjust rating span of third attempt
        elif score == 5:
            # get up side and down side ratings
            downrating = firstratings[climb]
            uprating = firstratings[climb+'u']
            # check if upside rating is greater than what has already been set, if it has been set
            if numpy.isnan(climberdata.loc[climber, 'up third']) or uprating > climberdata.loc[climber, 'up third']:
                bestthirdclimb = climb
                climberdata.loc[climber, 'down third'] = downrating
                climberdata.loc[climber, 'up third'] = uprating
        # climber did not finish this climb
        else:
            if lowestnotclimbed is None:
                lowestnotclimbed = climb
    # fill in any missing upside and downside ratings
    # climber has no score of 10 or 15
    if bestfirstclimb is None and bestsecondclimb is None:
        # downside is minimum climb rating
        climberdata.loc[climber, 'down first'] = 4
        # upside is one less than easiest climb
        climberdata.loc[climber, 'up first'] = 5
        # downside is minimum climb rating
        climberdata.loc[climber, 'down second'] = 4
        # upside is one less than easiest climb
        climberdata.loc[climber, 'up second'] = 5
    # climber has no score of 15, but does have a score of 10
    if bestfirstclimb is None and bestsecondclimb is not None:
        # downside is minimum climb rating
        climberdata.loc[climber, 'down first'] = 4
        # upside of first attempt is one less than easiest climb
        climberdata.loc[climber, 'up first'] = 5
    # climber has no score of 10, but does have a 15 score
    if bestfirstclimb is not None and bestsecondclimb is None:
        # set downside and upside rating to same as the best first attempt climb
        climberdata.loc[climber, 'down second'] = climberdata.loc[climber, 'down first']
        climberdata.loc[climber, 'up second'] = climberdata.loc[climber, 'up first']
    # climber has no score of 5 but does have a 10 or 15 score
    if (bestfirstclimb is not None or bestsecondclimb is not None) and bestthirdclimb is None:
        # set downside and upside rating to same as the best second attempt climb
        climberdata.loc[climber, 'down third'] = climberdata.loc[climber, 'down second']
        climberdata.loc[climber, 'up third'] = climberdata.loc[climber, 'up second']
    # set median values, rounding up
    climberdata.loc[climber, 'median first'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'down first']) + climbratings.index(climberdata.loc[climber, 'up first'])) / 2))]
    climberdata.loc[climber, 'median second'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'down second']) + climbratings.index(climberdata.loc[climber, 'up second'])) / 2))]
    climberdata.loc[climber, 'median third'] = climbratings[int(numpy.ceil((climbratings.index(climberdata.loc[climber, 'down third']) + climbratings.index(climberdata.loc[climber, 'up third'])) / 2))]
    # finally, estimate the downside, median and upside total scores
    for setnumber in sevensets.keys():
        for climb in sevensets[setnumber]:
            for span in ['down', 'median', 'up']:
                if climberdata.loc[climber, span+' first'] >= climb:
                    climberdata.loc[climber, 'estimated score all '+span] += 15
                elif climberdata.loc[climber, span + ' second'] >= climb:
                    climberdata.loc[climber, 'estimated score all ' + span] += 10
                elif climberdata.loc[climber, span+' third'] >= climb:
                    climberdata.loc[climber, 'estimated score all '+span] += 5

climberdata.to_csv('./processedclimberdata.txt', sep='\t')
