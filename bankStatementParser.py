import csv
import os
import sys


def parseStatements(bankName):
    path = "./Statements/"
    text = ""

    if(bankName == "ING"):
        path += os.listdir(path)[0]
        path += "/" + os.listdir(path)[0]
        with open(path, newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                row = list(filter(None, row))

                #For easier reading
                secondLastElement = row[len(row) - 2]
                LastElement       = row[len(row) - 1]

                if(secondLastElement[0] == "\""): #Sums are between " ", but divided in 2 elements. Bring them together, and remove quatation marks.
                    secondLastElement = ".".join([secondLastElement, LastElement])
                    secondLastElement = secondLastElement.replace("\"","")

                    row[len(row) - 2] = secondLastElement
                    row.pop(len(row) - 1) #Remove last element, as elements are joined

                text += (" ".join(row)) + "\n" #Will remove later TODO

                #If the first character of the csv row is a date without "-", it is the first line of the transaction info.
                if(row[0][0] in str(list(range(0,10))) and row[0][2] != "-"):
                    print(row[0])

        f = open("test.txt", "w")
        f.write(text)
        f.close()


    elif(bankName == "Revo"):
        path += os.listdir(path)[1]
        path += "/" + os.listdir(path)[0]
        with open(path, newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            for row in reader:
                text += (" ".join(row)) + "\n"

        f = open("test.txt", "w")
        f.write(text)
        f.close()

    else:
        print("Not a valid Bank")

if __name__ == "__main__":
    parseStatements(sys.argv[1])
