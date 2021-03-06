import os
from itertools import chain

import numpy
from PIL import Image
import sys as System
import re as REEEEE
from Letter import Letter

# Script Parameters defined globally
try:
    globeImagePath = System.argv[1]  # Path to captcha image
    globeXLength = int(System.argv[2])  # Width of Captcha Image
    globeYLength = int(System.argv[3])  # Height of Captcha Image
except IndexError:
    # No command line args provided
    pass


# Parses image file and returns array of (X,Y,Z) tuples corresponding to pixel color codes
def parseImageFile():
    # If no input arguments were provided check std::in
    if len(System.argv) == 1:
        return parseConsoleInputRGBCodes()
    # If the path provided is for a txt file with color codes then run the parseRGBCodeFile otherwise return list of
    # pixel colours straight from PIL
    try:
        global globeXLength, globeYLength, globeImagePath
        captchaImage = Image.open(globeImagePath, 'r').convert('RGB')
        arrayOfPixels = numpy.array(captchaImage)
        globeXLength, globeYLength = captchaImage.size
        arrayOfPixels = list(chain.from_iterable(arrayOfPixels.tolist()))
        arrayOfPixels = [tuple(x) for x in arrayOfPixels]
        # Find a better way to format the output string in the future
        outputString = '[{0}]'.format(','.join(map(str, arrayOfPixels)))
        outputString = outputString.replace('[', '')
        outputString = outputString.replace(']', '')
        outputString = outputString.replace('),(', ' ')
        outputString = outputString.replace('(', '')
        outputString = outputString.replace(')', '')
        outputString = outputString.replace(', ', ',')
        outputString = outputString.replace(', ', ',')

        # Create textfile that will contain the RGB codes of the image and parse it via parseRGBCodeFile
        globeImagePath = os.path.dirname(globeImagePath) + "\\" + os.path.basename(
            os.path.splitext(globeImagePath)[0]) + ".txt"
        outputFile = open(globeImagePath, 'w')
        outputFile.write(outputString)
        outputFile.close()
    except OSError:
        # Do nothing
        pass
    return parseRGBCodeFile(globeImagePath)
    pass


# Parses txt file path containing RGB list provided in the argument and returns array of (X,Y,Z) tuples corresponding to pixel
# color codes
def parseRGBCodeFile(fileName=str()):
    # read file
    file = open(fileName, "r")
    lines = file.readlines()
    file.close()
    # Strip all new lines and whitespace replace spaces with ","
    return readLines(lines)


# read input lines and return readLines(lines) list
def parseConsoleInputRGBCodes():
    global globeXLength, globeYLength  # First line must be size (Y,X)
    globeYLength, globeXLength = [int(size) for size in input().split(" ")]
    if not (globeYLength or globeXLength):
        print("No input has been provided")
        exit(1)
    lines = list()  # Get RGB list input
    for y in range(globeYLength):
        lines.append(input())
    return readLines(lines)


# Reads raw input of lines
def readLines(lines):
    listedLines = list()
    for index, line in enumerate(lines):
        lines[index] = line.replace('\n', ',')
        lines[index] = line.replace(' ', ',')
        listedLines.extend(lines[index].split(","))

    imageLines = list()
    for entry in listedLines:
        entry = REEEEE.sub("[^0-9]", "", entry)  # Strip non numerics
        imageLines.append(entry)

    imageLines = list(map(int, imageLines))
    zipImageIterable = zip(*[imageLines[i::3] for i in range(3)])  # Group into 3 sized tuples representing RGB code
    return list(zipImageIterable)


# Clean values of all non-letter related pixels
def cleanLetters(arrayOfPixels=list()):
    # Clean RGB codes @Update improve this for captchas with wider colour diversity
    oneDimensionArrayOfPixels = [(255, 255, 255) if (n > (100, 100, 100)) else (0, 0, 0) for n in arrayOfPixels]
    twoDimensionArrayOfPixels = [oneDimensionArrayOfPixels[(n * globeXLength):(n * globeXLength + globeXLength)] for n
                                 in
                                 range(0, globeYLength)]

    # for row in twoDimensionArrayOfPixels:
    #     print([row[i] for i in range(len(row))])

    return oneDimensionArrayOfPixels, twoDimensionArrayOfPixels


# Seperates letters and removes additional whitespace
def separateLetters(twoDimensionArrayOfPixels=list(list())):
    # Separate the list of pixels into an iterable of letter objects
    listOfLetters = list()

    global globeXLength, globeYLength
    # Remove top and bottem whitespace from pixel array
    while set(twoDimensionArrayOfPixels[0]).__eq__({(255, 255, 255)}):
        del twoDimensionArrayOfPixels[0]
        globeYLength -= 1

    while set(twoDimensionArrayOfPixels[-1]).__eq__({(255, 255, 255)}):
        del twoDimensionArrayOfPixels[-1]
        globeYLength -= 1

    # Remove left and right white space FIX: Find a cleaner way of deleting columns in 2D arrays
    while set([row[0] for row in twoDimensionArrayOfPixels]).__eq__({(255, 255, 255)}):
        for row in twoDimensionArrayOfPixels:
            del row[0]
        globeXLength -= 1

    while set([row[-1] for row in twoDimensionArrayOfPixels]).__eq__({(255, 255, 255)}):
        # print([row[-1] for row in twoDimensionArrayOfPixels])
        for row in twoDimensionArrayOfPixels:
            del row[-1]
        globeXLength -= 1

    # Iterate through all the columns, if a column that is completely whitespace is encountered, create a letter object
    # with the sub array of colour codes and append it to the letter list, remove white space columns until you reach a
    # column with no white space, then repeat, stop iterating once xColumnIterator = globeXLength
    xStartLetterColumn = 0
    xColumnIterator = 0
    while xColumnIterator < globeXLength:  # Assuming the shape is uniform
        if set([row[xColumnIterator] for row in twoDimensionArrayOfPixels]).__eq__(
                {(255, 255, 255)}) or (
                    xColumnIterator == globeXLength - 1):  # Encountered whitespace column or capturing last letter
            listOfLetters.append(Letter([row[xStartLetterColumn:xColumnIterator] for row in twoDimensionArrayOfPixels],
                                        (xColumnIterator - xStartLetterColumn, globeYLength)))
            # Iterate past useless whitespace
            xStartLetterColumn = xColumnIterator
            xColumnIterator += 1 if (xColumnIterator != globeXLength - 1) else 0  # Only increment if there are more columns
            while set([row[xColumnIterator] for row in twoDimensionArrayOfPixels]).__eq__({(255, 255, 255)}):
                xColumnIterator += 1
                xStartLetterColumn += 1
            xStartLetterColumn += 1
        xColumnIterator += 1
    return listOfLetters


def createImage(arrayOfRGBs=list(tuple())):
    output = Image.new("RGB", (globeXLength, globeYLength))
    output.putdata(arrayOfRGBs)
    return output


def writeImage(image=Image.Image):
    # Write file
    try:
        image.save(
            "{0}\\{1}-output.png".format(os.path.dirname(globeImagePath), os.path.basename(
                os.path.splitext(globeImagePath)[0])))
    except IOError or NameError:
        print("Path to output file not specified or does not exist")


def main():
    arrayOfPixels = parseImageFile()
    oneDimensionArrayOfPixels, twoDimensionArrayOfPixels = cleanLetters(arrayOfPixels)

    outputImage = createImage(oneDimensionArrayOfPixels)
    writeImage(
        outputImage)  # Outputs the cleaned version of the Captcha with only the letter of interest (Used for testing and viewing purposes)

    listOfLetters = separateLetters(twoDimensionArrayOfPixels)
    finalWord = [letter.identify() for letter in listOfLetters]
    print(''.join(finalWord))


main()
