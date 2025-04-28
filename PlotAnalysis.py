import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_excel(r'Z:\Python\ClassSorter\AnalysisData.xlsx')

x = df['x']
y = df['y']
z = df['z']

rotations = 2

plt.figure(figsize=(16, 9))
ax = plt.axes(projection='3d')
ax.scatter(x, y, z)
ax.set_xlabel('Cycles')
ax.set_ylabel('Number of Attempts')
ax.set_zlabel('Minimum MSE')
plt.savefig(r'Z:\Python\ClassSorter\fig.png', dpi = 1200)
plt.show()

fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111, projection='3d')

ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='none')
ax.set_xlabel('Cycles')
ax.set_ylabel('Number of Attempts')
ax.set_zlabel('Minimum MSE')
for angle in range(360*rotations):
    ax.view_init(30, angle%360, 0)
    plt.draw()
    plt.pause(0.001)
plt.show()

minimum = min(df['x'].unique())
maximum = max(df['x'].unique())
numPoints = maximum - minimum

def mean(arr):
    return sum(arr)/len(arr)

sampleSize = 5

plt.figure(figsize=(16,9))
for i in df['x'].unique():
    tempDF = df[df['x'] == i]
    if i < minimum + numPoints//3 + 1:
        colourX = int(256*(i-minimum)/numPoints)
        colourY = int(0)
        colourZ = int(0)
    elif i < minimum + 2*(numPoints//3) + 1:
        colourY = int(256*(i-minimum)/numPoints)
        colourX, colourZ = int(0), int(0)
    else:
        colourZ = int(256*(i-minimum)/numPoints)
        colourX, colourY = int(0), int(0)
    colour = f'#{colourX & 0xFF:02x}{colourY & 0xFF:02x}{colourZ & 0xFF:02x}'
    xArr, yArr = [], []
    for j in range (len(tempDF)//sampleSize):
        newX = tempDF.iloc[sampleSize*j + sampleSize//2, 1]
        vals = []
        for k in range (sampleSize):
            vals.append(tempDF.iloc[sampleSize*j + k, 2])
        newY = mean(vals)
        xArr.append(newX)
        yArr.append(newY)
    xExtra, yExtra = [], []
    for j in range(len(tempDF) - len(tempDF)//sampleSize):
        xExtra.append(tempDF.iloc[len(tempDF)//sampleSize + j, 1])
        yExtra.append(tempDF.iloc[len(tempDF)//sampleSize + j, 2])
    xArr.append(mean(xExtra))
    yArr.append(mean(yExtra))
    plt.plot(xArr, yArr, label = i, color = colour)
    # plt.plot(tempDF['y'], tempDF['z'], label = i, color = colour)

plt.legend(loc = 'upper right')
plt.grid(True)
plt.ylim(50,150)
plt.show()