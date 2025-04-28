#Class sorter analysis
# Class Sort V2.1 
# By Stanley Walker
import pandas as pd
import random
import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# root = tk.Tk()
# root.withdraw()
# filePath = filedialog.askopenfilename(title="Select a file")
filePath = r'Z:\Python\ClassSorter\input.xlsm'
sheet = pd.read_excel(filePath)
directory = os.path.dirname(filePath)
#Insert gui code here (call for code at least)
try:
    config = pd.read_csv(f"{directory}\config.csv")
except:
    FileNotFoundError
    print('Config not found :(((((')

config = config.fillna("")
outName = 'SortedClass'

# priority = ['Gender', 'Exlcuded', 'Friend 1', 'Friend 2', 'Friend 3', 'SEND', 'Academic Ability', 'Behaviour']
# cycles = 20
numClasses = int(3)#config['numClasses']
# numAttempts = int(10)#config['numAttempts']

cyclesRange = [i for i in range (1, 10)]
numAttemptsRange = [i for i in range (1, 30)]
analysis = []

for cycles in cyclesRange:
    for numAttempts in numAttemptsRange:

        dfList = []

        def initial(numClasses, df, classCounts):
            """
            Shuffle the classes randomly to give an initial sorting, this allows for different solutions to be generated
            Args:
                numClasses: Desired number of classes
                df: 
            """
            # for index, row in df.iterrows():
            #     df.at[index, "Class"] = random.randint(1, numClasses) # Pick a random value to assign each student to, by WLLN, and CLT, this should give equal(ish) numbers in each classes
            #Turns out this isn't that great, so we will assign differently
            if len(classCounts) < numClasses:
                classCounts = []
                for i in range (numClasses):
                    if len(df)%numClasses > i:
                        classCounts.append(len(df)//numClasses + 1)
                    else:
                        classCounts.append(len(df)//numClasses)
            unassigned = [i for i in range(len(df))]
            classes = []
            for val in classCounts:
                classTemp = []
                for i in range (val):
                    num = random.choice(unassigned)
                    classTemp.append(num)
                    unassigned.remove(num)
                classes.append(classTemp)
            indexToGroup = {}
            for i, group in enumerate(classes, start=1):
                for idx in group:
                    indexToGroup[idx] = i
            df['Class'] = df.index.map(indexToGroup)
            return df

        def scoreNorm(df, colName, options):
            score = 0
            for index, row in df.iterrows():
                score += options.get(row[colName], 0)# 0 is the default value
            # print(score)
            return score

        def scoreSpecial(df, colName, options):
            score = 0
            for index, row in df.iterrows():
                if row[colName] in df['Name'].values:
                    score += 1*int(options)# 1 is default
            return score

        def scoreTotal(df, options, numClasses):
            scores = {col: [] for col in df.columns if col not in ['Name', 'Class']}
            for col in options.keys():
                if str(options[col]) in ['-1', '1']: # We have a 'special' column, as there is only one value, there is not a map
                    for i in range(numClasses):
                        scores[col].append(scoreSpecial(df[df['Class'] == i+1], col, options[col]))
                elif len(options[col]) > 1:
                    for i in range(numClasses):
                        scores[col].append(scoreNorm(df[df['Class'] == i+1], col, options[col]))
            # print(scores)
            scoresDF = pd.DataFrame(scores)
            return scoresDF


        def findRange(scores):
            ranges = scores.max() - scores.min()
            return ranges

        def maximiseSpecial(df, colName, options, numClasses):
            if str(options[colName]) == '-1':
                for index in range (len(df)):
                # for index, row in df.iterrows():
                #     if df[df['Name'] == row[colName]]['Class'].squeeze() == row['Class']:# The excluded person is in this class, we will randomise a new class, then swap with a random person
                #         # print('hi')
                #         previousClass = row['Class']
                #         newClass = previousClass + 1
                #         if newClass > numClasses:
                #             newClass = 1
                    if df[df['Name'] == df.iloc[index][colName]]['Class'].squeeze() == df.iloc[index]['Class']:
                        previousClass = df.iloc[index]['Class']
                        newClass = previousClass + 1
                        if newClass > numClasses:
                            newClass = 1
                        toSwap = df[df['Class'] == newClass].sample(n=1).index[0]
                        # print('-------------------------')
                        # print(f'Previous class {previousClass}, new class {newClass}')
                        # # print(row.tolist())
                        # print(df.iloc[index].tolist())
                        # print(df.iloc[toSwap].tolist())
                        df.loc[toSwap, 'Class'] = previousClass
                        df.loc[index, 'Class']  = newClass
            elif str(options[colName]) == '1':
                # print('Need to figure out how to do this for friends')
                i = 1
            return df

        def shuffle(df, scores, options, ranges, numClasses):
            for col in options.keys():
                if str(options[col]) in ['-1', '1']:
                    df = maximiseSpecial(df, col, options, numClasses)
            for col in options.keys():
                if True:#col not in ['numClasses', 'Name', 'numAttempts', 'Firstname', 'Surname', 'Class']:
                    for i in range (int(ranges[col]/2)):#Loop through each column range/2
                        maxClass = scores[col].idxmax() + 1
                        minClass = scores[col].idxmin() + 1
                        if maxClass == minClass:
                            minClass = (maxClass + 1)//numClasses + 1 # If we somehow collect the same class twice, swap to the next one, this can probably be ignored
                        maxIndex = df[df['Class'] == maxClass][col].idxmax()
                        minIndex = df[df['Class'] == minClass][col].idxmin()
                        # print(f'Swapping {maxIndex} in {maxClass} for {minIndex} in {minClass} in column {col}')
                        df.at[maxIndex, 'Class'], df.at[minIndex, 'Class'] = df.at[minIndex, 'Class'], df.at[maxIndex, 'Class']
                    #Now recalculate
                    scores = scoreTotal(df, options, numClasses)
                    ranges = findRange(scores)
                    # classCount = []
                    # for i in range (numClasses):
                    #     classCount.append(len(df[df['Class'] == i+1]))
                    # print(max(classCount) - min(classCount))
                    # print(mse(ranges))
            return df

        def mse(ranges):
            meanSE = 0
            for i in range (len(ranges.values)):
                meanSE += (ranges.values[i])**2
            return meanSE

        def export(df, filepath):
            with pd.ExcelWriter(filepath) as writer:
                df.to_excel(writer, sheet_name = 'All students', index = False)
                for i in range (numClasses):
                    df[df['Class'] == i + 1].to_excel(writer, sheet_name = f'Class {i+1}', index = False)

        #Create mapping
        # print(config)
        columnDicts = {}
        for col in config.columns:
            if col not in ['numClasses', 'Name', 'numAttempts', 'Firstname', 'Surname']:
                if config[col].iloc[0] not in ['+', '-']:
                    colDict = {}
                    for i in config.index:
                        colDict[config.at[i, col]] = i + 1
                # else:
                #     if config[col].iloc[0] == '+':
                #         colDict[config.at[i, col]] = 1
                #     else:
                #         colDict[config.at[i, col]] = -1
                    colDict = {key: value for key, value in colDict.items() if not key == ''}
                elif config[col].iloc[0] == '+':
                    colDict = '1'
                elif config[col].iloc[0] == '-':
                    colDict = -1
                columnDicts[col] = colDict

        options = columnDicts#pd.DataFrame(columnDicts)
        # print(options)



        for i in range (numAttempts):
            df = initial(numClasses, sheet, [])
            scores = scoreTotal(df, options, numClasses)
            ranges = findRange(scores)
            meanSE = mse(ranges)
            # print(scores)
            #Shuffle df
            for j in range (cycles):
                df = shuffle(df, scores, options, ranges, numClasses)
            dfList.append([df, mse(findRange(scores))])

        # print(dfList)
        bestSort, minMSE = min(dfList, key = lambda x: x[1])
        # print(bestSort)
        # print(minMSE)
        #print(scoreTotal(bestSort, options, numClasses))
        #export(bestSort, f'{directory}\{outName}.xlsx') # Include output name
        print(f'Cycle: {cycles}, Attemps: {numAttempts}, MSE = {minMSE}')
        analysis.append([cycles, numAttempts, minMSE])

x = [p[0] for p in analysis]
y = [p[0] for p in analysis]
z = [p[0] for p in analysis]
data = pd.DataFrame(analysis, columns=['x', 'y', 'z'])
with pd.ExcelWriter(r'Z:\Python\ClassSorter\AnalysisData.xlsx') as writer:
    data.to_excel(writer, sheet_name = 'Data', index = False)


plt.figure(figsize=(16, 9))
ax = plt.axes(projection='3d')
ax.plot_surface(x, y, z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()
plt.savefig(r'Z:\Python\ClassSorter\fig.png', dpi = 1200)