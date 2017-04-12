import csv
import numpy as np

def main():
    B4 = generate4thorderbases()
    measuredData = {}
    with open('dataset.csv', mode='r') as file:
        reader = csv.reader(file)
        for rows in reader:
            measuredData[int(float(rows[0])*100)+100] = float(rows[1])
    #print(measuredData)

    bestBases = B4
    fittedCurve = [sum(row[i] for row in B4) for i in range(len(B4[0]))]
    #minError = calculateError(measuredData, fittedCurve);
    step = 0.2;
    '''
    for i1 in np.arange(0.0, 1.0, step):
        for i2 in np.arange(0.0, 1.0, step):
            print('check point i2')
            for i3 in np.arange(0.0, 1.0, step):
                for i4 in np.arange(0.0, 1.0, step):
                    for i5 in np.arange(0.0, 1.0, step):
                        for i6 in np.arange(0.0, 1.0, step):
                            for i7 in np.arange(0.0, 1.0, step):
                                for i8 in np.arange(0.0, 1.0, step):
                                    for i9 in np.arange(0.0, 1.0, step):
                                        for i10 in np.arange(0.0, 1.0, step):
                                            for i11 in np.arange(0.0, 1.0, step):
                                                for i12 in np.arange(0.0, 1.0, step):
                                                    for i13 in np.arange(0.0, 1.0, step):
                                                        amp = [i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13];
                                                        #ampedB4 = multAmplitude(amp, B4);
                                                        ampedB4 = [[B4[y][x]*amp[y] for x in range(len(B4[0]))] for y in range(len(B4))]

                                                        currentFittedCurve = [sum(row[i] for row in ampedB4) for i in range(len(ampedB4[0]))]
                                                        currentError = calculateError(measuredData, currentFittedCurve);
                                                        if currentError < 25.0:
                                                            #print('new error: ', minError)
                                                            #minError = currentError
                                                            fittedCurve = currentFittedCurve
                                                            bestBases = ampedB4
                                                            bestBases.append(fittedCurve)
                                                            print("min error: ", minError)
                                                            with open("b4.csv", "wb") as file:
                                                                writer = csv.writer(file)
                                                                writer.writerows(bestBases)
                                                            return
    '''
    upBound = [1.2 for i in range(len(B4))]  # initial upper bound
    lowBound = [0 for i in range(len(B4))]   # initial lower bound


    upBound, lowBound, step = findBoundaries(measuredData, B4, upBound, lowBound, step)
    upBound, lowBound, step = findBoundaries(measuredData, B4, upBound, lowBound, step)
    #upBound, lowBound, step = findBoundaries(measuredData, B4, upBound, lowBound, step)

    ampedB4 = [[B4[y][x] * upBound[y] for x in range(len(B4[0]))] for y in range(len(B4))]
    upperCurve = [sum(row[i] for row in ampedB4) for i in range(len(ampedB4[0]))]

    ampedB4 = [[B4[y][x] * lowBound[y] for x in range(len(B4[0]))] for y in range(len(B4))]
    lowerCurve = [sum(row[i] for row in ampedB4) for i in range(len(ampedB4[0]))]

    exportToFile(measuredData, upperCurve, lowerCurve, ampedB4)

    return

def findBoundaries(dataset, B4matrix, inputUpper, inputLower, inStep):
    # To return lower and upper boundary to speed up convergence
    outUpper = inputUpper
    outLower = inputLower

    for i in range(0, len(B4matrix)):
        currentBspline = B4matrix[i]

        for j in np.arange(inputLower[i], inputUpper[i], inStep):
            ampedCurrentBspline = [j*x for x in currentBspline]
            if checkIfLarger(dataset, ampedCurrentBspline):
                outUpper[i] = j
                outLower[i] = j - 2*inStep
                break
    outStep = inStep/5.0
    return outUpper, outLower, outStep

def checkIfLarger(dataset, ampedBspline):
    #larger = False
    startTimeForMeasuredData = min(dataset.iterkeys())
    endTimeForMeasuredData = max(dataset.iterkeys())
    for i in range(len(ampedBspline)):
        if ampedBspline[i] == 0 or (i > startTimeForMeasuredData and i < endTimeForMeasuredData and i not in dataset):
            continue
        else:
            if i <= startTimeForMeasuredData:
                pointToCompare = dataset.get(startTimeForMeasuredData)
            elif i >= endTimeForMeasuredData:
                pointToCompare = dataset.get(endTimeForMeasuredData)
            else:
                pointToCompare = dataset.get(i)

            if pointToCompare - ampedBspline[i] <= 0:
                return True
    return False

def calculateError(dataDict, fittedValue):
    error = 0
    for x,y in dataDict.items():
        error += abs(y - fittedValue[int(x)])
    return error

#def multAmplitude(amplitudeArr, basesArray):
#    ampedArray = basesArray
#    for i in range(0, len(basesArray)):
#        for j in range(0, len(basesArray[0])):
#           ampedArray[i][j] = basesArray[i][j] * amplitudeArr[i]
#    return ampedArray

def generate4thorderbases():
    maxRow, maxCol = 16, 1600

    # Time points
    T = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    # Populate B1 with impulse of amplitude 1
    B1 = [[0 for x in range(maxCol)] for y in range(maxRow)]
    for i in range(0, maxRow):
        for j in range(0, maxCol):
           if j/100 == i:
               B1[i][j] = 1

    # Create fake continous timescale
    time = [0 for i in range(0, maxCol)]
    start = 0.00
    for i in range(0, maxCol):
        time[i] = start
        start += 0.01

    B2 = generatenextorderbasis(B1, 2, time, T, 15, maxCol)
    B3 = generatenextorderbasis(B2, 3, time, T, 14, maxCol)
    B4 = generatenextorderbasis(B3, 4, time, T, 13, maxCol)

    return B4

def generatenextorderbasis(currentBasis, order, TC, T, numOfBases, maxCol):
    nextB = [[0 for x in range(maxCol)] for y in range(numOfBases)]
    for i in range(0, numOfBases):
        for j in range(0, maxCol):
            if T[i + order - 1] == T[i]:
                firstValue = 0
            else:
                firstValue = ((TC[j] - T[i]) / (T[i + order - 1] - T[i])) * currentBasis[i][j]
            if T[i + order] == T[i]:
                secondValue = 0
            else:
                secondValue = (1 - ((TC[j] - T[i + 1]) / (T[i + order] - T[i + 1]))) * currentBasis[i + 1][j];
            value = firstValue + secondValue
            nextB[i][j] = value;
    return nextB

def exportToFile(measuredData, upBound, lowBound, basis):
    file = open('out.csv', 'w')

    for i in range(len(upBound)):
        file.write(str(upBound[i]))
        if i != len(upBound) - 1:
            file.write(',')
        else:
            file.write('\n')
    for i in range(len(lowBound)):
        file.write(str(lowBound[i]))
        if i != len(lowBound) - 1:
            file.write(',')
        else:
            file.write('\n')
    for i in range(len(upBound)):
        if i not in measuredData:
            file.write('')
        else:
            file.write(str(measuredData.get(i)))
        if i != len(upBound) - 1:
            file.write(',')
        else:
            file.write('\n')
    file.close()
    return

main()