import numpy
import pandas

# list of 5.X ratings possible
climbratings = [4, 5, 6, 7, 8, 9, 10, 10.5, 11, 11.5, 12, 12.5, 13]
# dictionary of ratings of the first set of climbs (1A-1D)
firstratings = {'1A': 6, '1B': 10, '1C': 10, '1D': 11.5}
# create random climb ratings for the next 7 sets
sevensets = {2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
for key in sevensets.keys():
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
    print(sevensets[key])

try:
    # load climber data
    climberdata = pandas.read_csv('./climberdata.txt', sep='\t', index_col='Climber')
except FileNotFoundError:
    # if there is no climber data create random climber data for testing
    data = {'Climber': [], 'first': [], 'second': [], 'third': [], '1A': [], '1B': [], '1C': [], '1D': [], 'score 1': [], 'score all': []}
    for i in range(50):
        data['Climber'].append(i)
        # randomly generate the ratings a climber can climb on first, second, and third+ attempts
        ifirst = int(round(numpy.random.normal(5, 2), 0))
        isecond = min(ifirst + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        ithird = min(isecond + max(0, int(round(numpy.random.normal(1, 0.5), 0))), len(climbratings) - 1)
        data['first'].append(climbratings[ifirst])
        data['second'].append(climbratings[isecond])
        data['third'].append(climbratings[ithird])
        # now use the ratings to assign the climber points for climbs 1A-1D
        for climb in firstratings.keys():
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
print(climberdata)
# add empty columns that will be used later
climberdata['lowfirst'] = numpy.nan
climberdata['highfirst'] = numpy.nan
climberdata['medianfirst'] = numpy.nan
climberdata['lowsecond'] = numpy.nan
climberdata['highsecond'] = numpy.nan
climberdata['mediansecond'] = numpy.nan
climberdata['lowthird'] = numpy.nan
climberdata['highthird'] = numpy.nan
climberdata['medianthird'] = numpy.nan

# look at climbers one at a time (parse through the rows of climber data)
for climber, climberstats in climberdata.iterrows():
    # estimate lower and upper values of 5.X rating obtainable on first attempt
    if climberstats['1D'] == 15:
        climberdata.loc[climber, 'lowfirst'] = firstratings['1D']
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1D']) + 2]
    elif climberstats['1C'] == 15:
        climberdata.loc[climber, 'lowfirst'] = firstratings['1C']
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1D']) -1]
    elif climberstats['1B'] == 15:
        climberdata.loc[climber, 'lowfirst'] = firstratings['1B']
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1C']) -1]
    elif climberstats['1A'] == 15:
        climberdata.loc[climber, 'lowfirst'] = firstratings['1A']
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1B']) -1]
    elif climberstats['1A'] == 10:
        climberdata.loc[climber, 'lowfirst'] = climbratings[climbratings.index(firstratings['1A']) - 1]
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1A'])]
    else:
        climberdata.loc[climber, 'lowfirst'] = climbratings[climbratings.index(firstratings['1A']) - 2]
        climberdata.loc[climber, 'highfirst'] = climbratings[climbratings.index(firstratings['1A']) - 1]
    # estimate lower and upper values of 5.X rating obtainable on third attempt
    if climberstats['1D'] == 5:
        climberdata.loc[climber, 'lowthird'] = firstratings['1D']
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1D']) + 2]
    elif climberstats['1C'] == 5:
        climberdata.loc[climber, 'lowthird'] = firstratings['1C']
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1D']) - 1]
    elif climberstats['1B'] == 5:
        climberdata.loc[climber, 'lowthird'] = firstratings['1B']
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1C']) - 1]
    elif climberstats['1A'] == 5:
        climberdata.loc[climber, 'lowthird'] = firstratings['1A']
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1B']) - 1]
    elif climberstats['1A'] == 0:
        climberdata.loc[climber, 'lowthird'] = climbratings[climbratings.index(firstratings['1A']) - 2]
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1A']) - 1]
    elif climberstats['1B'] == 0:
        climberdata.loc[climber, 'lowthird'] = climbratings[climbratings.index(firstratings['1A']) + 1]
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1B']) - 1]
    elif climberstats['1C'] == 0:
        climberdata.loc[climber, 'lowthird'] = climbratings[climbratings.index(firstratings['1B']) + 1]
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1C']) - 1]
    elif climberstats['1D'] == 0:
        climberdata.loc[climber, 'lowthird'] = climbratings[climbratings.index(firstratings['1C']) + 1]
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1D']) - 1]
    else:
        climberdata.loc[climber, 'lowthird'] = climbratings[climbratings.index(firstratings['1D']) + 1]
        climberdata.loc[climber, 'highthird'] = climbratings[climbratings.index(firstratings['1D']) + 2]
    # estimate lower and upper values of 5.X rating obtainable on second attempt
    if climberstats['1D'] == 10:
        climberdata.loc[climber, 'lowsecond'] = firstratings['1D']
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1D']) + 2]
    elif climberstats['1C'] == 10:
        climberdata.loc[climber, 'lowsecond'] = firstratings['1C']
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1D']) - 1]
    elif climberstats['1B'] == 10:
        climberdata.loc[climber, 'lowsecond'] = firstratings['1B']
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1C']) - 1]
    elif climberstats['1A'] == 10:
        climberdata.loc[climber, 'lowsecond'] = firstratings['1A']
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1B']) - 1]
    elif climberstats['1C'] == 15 and climberstats['1D'] in [0, 5]:
        climberdata.loc[climber, 'lowsecond'] = climbratings[climbratings.index(firstratings['1C']) + 1]
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1D']) - 1]
    elif climberstats['1B'] == 15 and climberstats['1C'] in [0, 5]:
        climberdata.loc[climber, 'lowsecond'] = climbratings[climbratings.index(firstratings['1B']) + 1]
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1C']) - 1]
    elif climberstats['1A'] == 15 and climberstats['1B'] in [0, 5]:
        climberdata.loc[climber, 'lowsecond'] = climbratings[climbratings.index(firstratings['1A']) + 1]
        climberdata.loc[climber, 'highsecond'] = climbratings[climbratings.index(firstratings['1B']) - 1]
    else:
        climberdata.loc[climber, 'lowsecond'] = min(climberdata.loc[climber, 'lowfirst'], climberdata.loc[climber, 'lowthird'])
        climberdata.loc[climber, 'highsecond'] = max(climberdata.loc[climber, 'highfirst'], climberdata.loc[climber, 'highthird'])
    # set median values
    climberdata.loc[climber, 'medianfirst'] = climbratings[int(numpy.floor((climbratings.index(climberdata.loc[climber, 'lowfirst'])+climbratings.index(climberdata.loc[climber, 'highfirst']))/2))]
    climberdata.loc[climber, 'mediansecond'] = climbratings[int(numpy.floor((climbratings.index(climberdata.loc[climber, 'lowsecond'])+climbratings.index(climberdata.loc[climber, 'highsecond']))/2))]
    climberdata.loc[climber, 'medianthird'] = climbratings[int(numpy.floor((climbratings.index(climberdata.loc[climber, 'lowthird'])+climbratings.index(climberdata.loc[climber, 'highthird']))/2))]

climberdata.to_csv('./processedclimberdata.txt', sep='\t')
print(climberdata)