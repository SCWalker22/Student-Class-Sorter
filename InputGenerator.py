import pandas as pd
import random

nameList = [
    'Alice Carter', 'Benjamin Stone', 'Chloe West', 'Daniel Ford', 'Eva Brooks', 'Finn Harvey', 'Grace Nolan', 'Henry Adams', 'Isla Chambers', 'Jack Foster',
    'Katie Monroe', 'Liam Douglas', 'Maya Collins', 'Noah Blake', 'Olivia Price', 'Patrick Sinclair', 'Quinn Rivers', 'Ruby Hayes', 'Samuel Bennett', 'Tessa Reed',
    'Uma Hart', 'Victor Jennings', 'Willow Banks', 'Xander Flynn', 'Yasmine Abbott', 'Zachary Holt', 'Amelia Jordan', 'Blake Sheridan', 'Clara Webb', 'Dylan Parks',
    'Eliza Vaughn', 'Felix Martin', 'Gemma Cross', 'Hudson Lowe', 'Ivy Tate', 'Jonah Briggs', 'Keira Donovan', 'Lucas Frost', 'Madeline Sharp', 'Nate Rowe',
    'Ophelia Sutton', 'Preston Mills', 'Quincy Ellis', 'Rosie Durham', 'Sebastian Glover', 'Talia Kemp', 'Uriel Westbrook', 'Vivian Drake', 'Wyatt Hale', 'Xenia Rhodes',
    'Yara Whitman', 'Zane Preston', 'Avery Steele', 'Brady Knowles', 'Camilla Hartley', 'Dominic Reeves', 'Eleanor Flynn', 'Freddie McCoy', 'Georgia Pratt', 'Harrison Cain',
    'Ines Shepherd', 'Jasper Booth', 'Kendall Lowe', 'Leo Barrett', 'Morgan Fields', 'Naomi Griffith', 'Owen Clarke', 'Piper Vaughan', 'Quentin Moore', 'Riley Nash',
    'Sienna Thornton', 'Theo Ramsey', 'Una Baird', 'Valerie Knox', 'Wesley Scott', 'Ximena Boyd', 'Yvette Maddox', 'Zavier Hunt', 'Abigail Dean', 'Bryce Winters',
    'Cora Sutton', 'Declan Forbes', 'Emilia Brooks', 'Flynn Chambers', 'Greta Wallace', 'Holden Blair', 'Isabel Carr', 'Jude Harding', 'Kira Dalton', 'Logan Tate'
]

count = len(nameList)

genderList = ['Male', 'Female']
sendList = ['No SEND', 'SEND']
acList = ['High', 'Medium', 'Low']
beList = ['Good', 'Average', 'Poor']

listOlists = [genderList, sendList, acList, beList]

df = pd.DataFrame(nameList)
df.rename(columns={df.columns.tolist()[0]: 'Name'}, inplace=True)
for arr in listOlists:
    newList = []
    for i in range (count):
        newList.append(random.choice(arr))
    df[arr[0]] = newList

for i in range (3):
    arr = []
    for j in range (count):
        choice = random.choice(nameList)
        existsBefore = choice == df['Name'][j]
        if i == 2:
            if choice == df['Friend 1'][j]:
                existsBefore = True
        elif i == 3:
            if choice == df['Friend 1'][j] or choice == df['Friend 2'][j]:
                existsBefore = True
        while existsBefore:
            choice = random.choice(nameList)
            existsBefore = choice == df['Name'][j]
            if i == 2:
                if choice == df['Friend 1'][j]:
                    existsBefore = True
            elif i == 3:
                if choice == df['Friend 1'][j] or choice == df['Friend 2'][j]:
                    existsBefore = True
        arr.append(choice)
    df[f'Friend {i+1}'] = arr

arr = []
for i in range (count):
    choice = random.choice(nameList)
    existsBefore = choice == df['Name'][j]
    if choice in [df['Friend 1'][j], df['Friend 2'][j], df['Friend 3'][j]]:
        existsBefore = True
    while existsBefore:
        choice = random.choice(nameList)
        existsBefore = choice == df['Name'][j]
        if choice in [df['Friend 1'][j], df['Friend 2'][j], df['Friend 3'][j]]:
            existsBefore = True
    arr.append(choice)
df['Excluded'] = arr

df.columns = ['Name', 'Gender', 'SEND', 'Academic Ability', 'Behaviour', 'Friend 1', 'Friend 2', 'Friend 3', 'Excluded']

with pd.ExcelWriter('Students.xlsx') as writer:
    df.to_excel(writer, sheet_name = 'Sheet 1', index = False)