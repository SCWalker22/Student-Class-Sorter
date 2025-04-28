# Class Sort V2.1 
# By Stanley Walker
import pandas as pd
import random
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# priority = ['Gender', 'Exlcuded', 'Friend 1', 'Friend 2', 'Friend 3', 'SEND', 'Academic Ability', 'Behaviour']
cycles = 5
numAttempts = 10
before = True
after = False

welcomeMessage = 'Welcome to Class Sorter V2, by Stanley Walker.\n\n\nPlease select the spreadsheet of students you would like to sort on the window that appears.\n' \
'You will then be prompted to fill in a table, if this is not your first time, it should automatically fill, but please check this first.\n' \
'Please enter the number of classes you want, and fill the table from the options listed at the top, exactly as they appear, and in order (either from best to worst, or worst to best).\n' \
'The programme will then attempt to sort the students, and then save an output file in the same place. This can take up to a few minutes.\n' \
'Feel free to make manual changes to the output, or re-run this code, it is not guaranteed to give perfect results every time \n' \
'If the programme is crashing before showing an output, please find the file "config.csv" and delete it - This will cause the programme to reset to defaults, and can solve issues. If further issues arise, please contact stanthewalker@hotmail.com.'
print(welcomeMessage)

def initial(numClasses, df, classCounts = []):
    """
    Shuffle the classes randomly to give an initial sorting, this allows for different solutions to be generated
    Args:
        numClasses: Desired number of classes
        df: Dataframe of students and their attributes
        classCounts: Array of desired students per class, can be left as an empty array, or as none, in whihc case it will automatically be defined to have an even spread
    
        Returns:
            df: Returns original dataframe, with extra column 'Class', defined by randomly picking students for each class
    """
    # for index, row in df.iterrows():
    #     df.at[index, "Class"] = random.randint(1, numClasses) # Pick a random value to assign each student to, by WLLN, and CLT, this should give equal(ish) numbers in each classes
    #Turns out this isn't that great, so we will assign differently
    if len(classCounts) < numClasses:# If classCounts array is not properly filled, reassign it
        classCounts = []
        for i in range (numClasses):#Loop through classes, to see if they need more than students (integer divided by) num classes
            if len(df)%numClasses > i:
                classCounts.append(len(df)//numClasses + 1)#This class has one extra student
            else:
                classCounts.append(len(df)//numClasses)#Normal number of students
    unassigned = [i for i in range(len(df))] # Create a list of unnasigned students by index in df
    classes = []#Set up empty array to be added as column
    #This could probably be made more efficient, could set up array as correct length, all values = 0, then reasign as chosen, and remove from list
    #At present, we choose val students from the remaining list to be added to each class, with val from our classCounts array
    for val in classCounts:
        classTemp = []
        for i in range (val):
            num = random.choice(unassigned)
            classTemp.append(num)
            unassigned.remove(num)#Remove student from the remaining list
        classes.append(classTemp)
    indexToGroup = {}#Now turn the assignments from a 2d array to a column, then add to df
    for i, group in enumerate(classes, start=1):
        for idx in group:
            indexToGroup[idx] = i
    df['Class'] = df.index.map(indexToGroup)
    return df

def scoreNorm(df, colName, options):
    """
    Scores a 'normal' column of a dataframe - containing attributes, rather than names - for a given class

    Args:
        df: Dataframe containing student data (for a specific class)
        colName: The desired column to score
        options: Dictionary of options and their scores
    
    Returns:
        score: Integer of the sum of 'points' based off mapping in options
    """
    score = 0# Start a counter
    for index, row in df.iterrows():# Loop through by row
        score += options.get(row[colName], 0)# 0 is the default value
        #Map the attribute to their score, have 0 as a fallback value (cannot map)
    # print(score)
    return score

def scoreSpecial(df, colName, options):
    """
    Scores a special column of a dataframe for a given class

    Args:
        df: Dataframe containing student data (for a specific class)
        colName: The desired column to score
        options: Dictionary of options and their scores
    
    Returns:
        score: Integer of sum of points (number of students also in the class) - follows sign in options column
    """
    score = 0
    for index, row in df.iterrows():
        if row[colName] in df['Name'].values: # If the name of the student in the desired column is in this df, then that student is in this class
            score += 1*int(options)#Positive when +, negative when - in options list
    return score

def scoreTotal(df, options, numClasses):
    """
    Scores all columns of dataframe

    Args:
        df: Dataframe of students and their classes
        options: Dictionary of options and their mappings
        numClasses: Number of classes - Could be derived later instead?
    
    Returns:
        scoresDF: Dataframe of scores, each row is a class, and each column is a column in df
    """
    scores = {col: [] for col in df.columns if col not in ['Name', 'Class']} # Create a dict of scores, for non-name columns
    for col in options.keys(): # If col is in our dict (We should score it) - then loop through this column
        #Now decide if this column is 'special' or not
        if str(options[col]) in ['-1', '1']: # We have a 'special' column, as there is only one value, there is not a map
            for i in range(numClasses): # Score each class
                scores[col].append(scoreSpecial(df[df['Class'] == i+1], col, options[col]))
        elif len(options[col]) > 1:
            for i in range(numClasses): # Score each class
                scores[col].append(scoreNorm(df[df['Class'] == i+1], col, options[col]))
    # print(scores) # Print scores to console to see progress, can be ignored or removed
    scoresDF = pd.DataFrame(scores) # Convert scores to df
    return scoresDF


def findRange(scores):
    """
    Find the range of scores between different classes for each column

    Args:
        scores: Dataframe of scores
    
    Returns:
        ranges: Not sure the data type, but somehow a list/df of the range of scores
    """
    ranges = scores.max() - scores.min()
    return ranges

def pickRandomStudents(df, count):
    """
    Picks count random students from the dataframe

    Args:
        df: Dataframe to chose from
        count: Number of students to chose

    Returns:
        randStudentList: Array of indexes of students
    """
    randStudentList = []
    for j in range (count):
        randStudent = random.randint(0, len(df) - 1)
        while randStudent in randStudentList:
            randStudent = random.randint(0, len(df) - 1)
    return randStudentList

def swapFriends(df, orig, new, origNum, newNum):
    """
    Swaps students between classes

    Args:
        df: Dataframe of students
        orig: List of indexes of first class
        new: List of indexes of second class
        origNum: Class number of first class
        newNum: Class number of second class

    Returns:
        df: Dataframe with the studens swapped
    """
    for i in range (len(orig)):
        df.loc[orig[i], 'Class'] = newNum
        df.loc[new[i], 'Class'] = origNum
    return df

def anneal(df, tempDF, numClasses, options, threshold = 0.75):
    """
    Analyse score of 2 dataframes, and chose the better one, with some annealing
    Args:
        df: First DF
        tempDF: Second DF
        numClasses: Number of classes
        options: Options df
        threshold: Random threshold (1 = no random)

    Returns:
        df: Dataframe, depending on score, and annealing
    """
    randomNum = random.random()
    if mse(findRange(scoreTotal(df, options, numClasses))) > mse(findRange(scoreTotal(tempDF, options, numClasses))):
        if randomNum > threshold:
            return df
        else:
            return tempDF
    elif randomNum < threshold:
        return tempDF
    else:
        return df

def maximiseSpecial(df, colName, options, numClasses):
    """
    'Improve' the score of a 'special' column, by moving the student to a different class

    Args:
        df: Dataframe of students with classes
        colName: The column to improve the score of
        options: Dict of options mapping
        numClasses: Number of classes

    Returns:
        df: Dataframe of students with classes, slightly rearranged to improve the score
    """
    if str(options[colName]) == '-1': # If this is a negative special column, try to remove student from this class
        for index in range (len(df)): # Loop through by index to allow for changes to this dataframe in the for loop
        # for index, row in df.iterrows():
        #     if df[df['Name'] == row[colName]]['Class'].squeeze() == row['Class']:# The excluded person is in this class, we will randomise a new class, then swap with a random person
        #         # print('hi')
        #         previousClass = row['Class']
        #         newClass = previousClass + 1
        #         if newClass > numClasses:
        #             newClass = 1
            if df[df['Name'] == df.iloc[index][colName]]['Class'].squeeze() == df.iloc[index]['Class']: # Loop through student, and if the name is in their class, try to move them
                previousClass = df.iloc[index]['Class'] # Find their current class
                newClass = previousClass + 1 # Increment class by 1
                if newClass > numClasses: # Reset to class 1 if this number is not valid
                    newClass = 1
                toSwap = df[df['Class'] == newClass].sample(n=1).index[0] # Find a random student in this class to swap with
                #This could be changed, but at the cost of time
                df.loc[toSwap, 'Class'] = previousClass # Set the students to now be in their new classes
                df.loc[index, 'Class']  = newClass
    elif str(options[colName]) == '1': # If this is a positive column, do something else, this is not yet done
        for i in range (numClasses): # Loop through Classes
            dfOriginalClass = df[df['Class'] == i+1] # Create a new DF of just students in this class
            previousClass = i+1
            newClass = previousClass + 1 # Increment class by 1
            if newClass > numClasses: # Reset to class 1 if this number is not valid
                newClass = 1
            dfNewClass = df[df['Class'] == newClass] # Create a new DF of new ckass
            count = int(len(dfOriginalClass)/5)# We want to pick about 1/5 of the students
            orignalStudentList = pickRandomStudents(dfOriginalClass, count) # Chose some random, unique students from this old class
            newStudentList = pickRandomStudents(dfNewClass, count) # Chose some randome, unique students from the new class too
            tempDF = swapFriends(df, orignalStudentList, newStudentList, previousClass, newClass) # Create a temporary new df, where the students have been swapped
            df = anneal(df, tempDF, numClasses, options) # Conditionally accept this new temporary df
    return df

def shuffle(df, scores, options, ranges, numClasses):
    """
    Shuffle df to improve scores

    Args:
        df: Dataframe of students and their class
        scores: Dataframe of scores for the current df
        options: Dict of options for each column
        ranges: Ranges of scores between columns
        numClasses: Number of classes

    Returns:
        df: Original df with modifications to improve the score
    """
    if before:
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
    if after:
        for col in options.keys():
            if str(options[col]) in ['-1', '1']:
                df = maximiseSpecial(df, col, options, numClasses)
            # classCount = []
            # for i in range (numClasses):
            #     classCount.append(len(df[df['Class'] == i+1]))
            # print(max(classCount) - min(classCount))
            # print(mse(ranges))
    return df

def mse(ranges):
    """
    Find the Squared Error of the ranges for the columns

    Args:
        ranges: Data for the range of values for each column
    
    Returns:
        meanSE: Integer value for the squared error
    """
    meanSE = 0
    for i in range (len(ranges.values)): # Loop trhough by column, and add to a counter
        meanSE += (ranges.values[i])**2
    return meanSE

def export(df, filepath):
    """
    Export completed df to given filepath

    Args:
        df: Dataframe to export
        filepath: Full file location to export to (end in (eg) .xlsx)
    """
    with pd.ExcelWriter(filepath) as writer:
        df.to_excel(writer, sheet_name = 'All students', index = False)
        for i in range (numClasses):
            df[df['Class'] == i + 1].to_excel(writer, sheet_name = f'Class {i+1}', index = False)

#Set up a default windows file dialogue window, and prompt to select input file
root = tk.Tk()
root.withdraw()
filePath = filedialog.askopenfilename(title="Select a file")
sheet = pd.read_excel(filePath) # Read date from file
directory = os.path.dirname(filePath) # Find the directory for this file
#Insert gui code here (call for code at least)

#==========================================================GUI Config=====================================================
class ConfigEntryApp:
    def __init__(self, master, dataframe, dir):
        self.master = master
        self.master.title('Class Sorter - By Stan Walker')
        self.dataframe = dataframe

        self.csv_path = f'{dir}\config.csv'

        if os.path.exists(self.csv_path):
            self.load_csv()
            self.columns = self.df.columns[1:]
            # print(self.columns)
            self.exist = True
        else:
            self.df = dataframe.copy()
            self.columns = self.df.columns[1:]
            self.exist = False
            
        self.num_classes = tk.IntVar()

        if pd.notna(self.df.iloc[0,0]) and type(self.df.iloc[0,0]) in [int, float]:
            # print(self.df.iloc[0,0])
            self.num_classes.set(int(self.df.iloc[0,0]))

        top_frame = ttk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text='Number of Classes:').pack(side=tk.LEFT, padx=5, pady=5)
        self.num_classes = ttk.Entry(top_frame, textvariable=self.num_classes)
        self.num_classes.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(top_frame, text='Instructions: Enter the possible options into the table (Exactly as the appear at the top), the number of classes desired, and a + or - if it contains names').pack(side=tk.LEFT, padx=5, pady=5)

        grid_frame = ttk.Frame(self.master)
        grid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.num_rows = 5

        for i, col in enumerate(self.columns):
            label = ttk.Label(grid_frame, text=col)
            label.grid(row=0, column=i, padx=5, pady=5)

        for i, col in enumerate(self.columns):
            uniqueValues = self.df[col].dropna().unique()
            if len(uniqueValues) <= 5 and len(uniqueValues) != 1:
                uniqueValuesText = ', '.join(map(str, uniqueValues)) if len(uniqueValues) > 0 else 'No Data'
            elif len(uniqueValues) != 1:
                uniqueValuesText = '+ or -'

            uniqueLabel = ttk.Label(grid_frame, text=uniqueValuesText)
            uniqueLabel.grid(row=1, column=i, padx=5, pady=5)

        self.entries = {}
        for row in range(self.num_rows):
            for col in range(len(self.columns)):
                entry = ttk.Entry(grid_frame)
                if row < len(self.df) and not pd.isna(self.df.iloc[row, col+1]) and self.exist:
                    entry.insert(0, self.df.iloc[row, col+1])
                entry.grid(row=row+2, column=col, padx=5, pady=5)
                self.entries[(row, col)] = entry
        
        self.submit_button = ttk.Button(self.master, text='Submit', command = self.submit_data)
        self.submit_button.pack(side=tk.BOTTOM, pady=10)

    def load_csv(self):
        self.df = pd.read_csv(self.csv_path)

    def submit_data(self):
        self.num_classes_val = int(self.num_classes.get())
        new_data = []
        for row in range (self.num_rows):
            row_data = []
            for col in range (len(self.columns)):
                row_data.append(self.entries[(row,col)].get())
            new_data.append(row_data)
        self.new_df = pd.DataFrame(new_data, columns=self.columns)
        self.new_df.at[0, 'Name'] =  self.num_classes_val
        cols = self.new_df.columns.tolist()
        cols.remove('Name')
        cols = ['Name'] + cols
        self.new_df = self.new_df[cols]
        self.new_df = self.new_df.dropna(how='all')
        self.new_df.to_csv(self.csv_path, index=False)
        # print(self.new_df)
        self.master.quit()

root = tk.Tk()
app = ConfigEntryApp(root, sheet, directory)
root.mainloop()

try: # Attempt to read confing file from same location, if failed, create the config file
    config = pd.read_csv(f"{directory}\config.csv")# Should be modified to allow editing now when implemented
except:
    FileNotFoundError
    print('Config not found :(((((')

# Organise the data from the config folder
config = config.fillna("")
#Set the name of the output document for later
outName = 'SortedClass.xlsx'

#Create mapping
# print(config)
columnDicts = {}
for col in config.columns: # Loop through columns of the config dic
    if col not in ['numClasses', 'Name', 'numAttempts', 'Firstname', 'Surname']:
        if config[col].iloc[0] not in ['+', '-']: # Not a special column
            colDict = {}
            for i in config.index:
                colDict[config.at[i, col]] = i + 1 # Score based on order in table
        # else:
        #     if config[col].iloc[0] == '+':
        #         colDict[config.at[i, col]] = 1
        #     else:
        #         colDict[config.at[i, col]] = -1
            colDict = {key: value for key, value in colDict.items() if not key == ''}
        elif config[col].iloc[0] == '+': # If special value, decide if it should be positive or negative
            colDict = '1'
        elif config[col].iloc[0] == '-':
            colDict = -1
        columnDicts[col] = colDict

options = columnDicts#pd.DataFrame(columnDicts)
# print(options)
#Set up some values, we should be able to read these from the config file when fully implemented, but this could take some time
numClasses = int(config['Name'][0])
dfList = [] # Create a list to later store the different attempts

for i in range (numAttempts): # Start the loop for each attempt
    df = initial(numClasses, sheet) # Shuffle the dataframe
    scores = scoreTotal(df, options, numClasses)# Score our new dataframe
    ranges = findRange(scores)
    # meanSE = mse(ranges)
    # print(scores)
    #Shuffle df
    for j in range (cycles):# Loop through improving the df by the number of cycles decided above (optimal values and analysis listed elsewhere)
        df = shuffle(df, scores, options, ranges, numClasses) # USe the shuffle function to improve df
        print(f'{int((j/cycles + i)/numAttempts*100)}% Completed')
    dfList.append([df, mse(findRange(scores))]) # Once done, add this df to our list, with the MSE as a total score indicator

# print(dfList)
bestSort, minMSE = min(dfList, key = lambda x: x[1]) # Find the best sort based on the lowest MSE
# print(bestSort)#Print this best sort, and its score
# print(minMSE)
print(scoreTotal(bestSort, options, numClasses))#Print the score for each column for this df
#Export df to drive
export(bestSort, f'{directory}\{outName}') # Include output name
#Prevent window from closing until enter is pressed
wait = input(f'Thank you for using Class Sorter, please now press enter to close Class Sorter, your file has been saved as {directory}/{outName} \n')