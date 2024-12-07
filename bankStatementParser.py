import csv
import os
import sys


def monthStringToNumber(month): #Turn the name of a month into it's corresponding number
    match month:
        case "ianuarie":
            return ("01")
        case "februarie":
            return ("02")
        case "martie":
            return ("03")
        case "aprilie":
            return ("04")
        case "mai":
            return ("05")
        case "iunie":
            return ("06")
        case "iulie":
            return ("07")
        case "august":
            return ("08")
        case "septembrie":
            return ("09")
        case "octombrie":
            return ("10")
        case "noiembrie":
            return ("11")
        case "decembrie":
            return ("12")


transactionTypesEnum = ("Incasare ", "Cumparare", "Transfer ")


def parseStatements(bankName, filePath):
    checkInNRows = -1
    transactionText = ""

    #Info to be extracted
    transactionDate   = ""
    transcationType   = ""
    transcationValue  = ""
    transactionVendor = ""

    #Full transaction list
    transcationList = []

    if(bankName == "ING"):
        with open(filePath, newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            for row in reader:
                row = list(filter(None, row)) #Remove all empty elements

                if(checkInNRows != -1): #Get the vendor type in N rows
                    checkInNRows -= 1

                #For easier reading
                secondLastElement = row[len(row) - 2]
                LastElement       = row[len(row) - 1]

                if(secondLastElement[0] == "\""): #Sums are between " ", but divided in 2 elements. Bring them together, and remove quatation marks and decimal point.
                    secondLastElement = secondLastElement.replace(".","") #Remove the decimal point as it is uneeded.
                    secondLastElement = ".".join([secondLastElement, LastElement]) #Join elements.
                    secondLastElement = secondLastElement.replace("\"","") #remove quatation.

                    row[len(row) - 2] = secondLastElement
                    transcationValue = secondLastElement #Add the value to the info list
                    row.pop(len(row) - 1) #Remove last element, as elements are joined

                if(checkInNRows == 0):
                    if(row[0][0 : 9] != "Referinta"): #Case that deviates from the usual. Need to check next row to get the vendor.
                        transactionVendor = row[0]
                        checkInNRows = -1
                        ### Adding the value to the transaction list ###
                        transcationList.append([transactionDate, transcationType, transcationValue, transactionVendor])
                    else:
                        checkInNRows = 1

                #If the first character of the csv row is a date without "-", it is the first line of the transaction info.
                if(row[0][0] in str(list(range(0,4))) and row[0][2] != "-"):
                    transactionDate = row[0]           #This is the date in a word format
                    transcationType = row[1] #This is the type, "incasare", "transfer", "cumparare"
                    if(row[1] == "Incasare"): #If the type matches, get the vendor type in N rows
                        checkInNRows = 1
                    elif(row[1] == "Transfer Home'Bank"):
                        checkInNRows = 2
                    elif(row[1] == "Cumparare POS"):
                        checkInNRows = 2

        #After reading through the csv file, raw data will be saved to the transcationList list. It will need to be processed.
        #  --- Processing the data ---  #

        for transaction in transcationList:
            #  --- Date ---   #
            date = transaction[0].split()
            month = date[1]
            year  = date[2]

            transaction[0] = transaction[0].replace(month, monthStringToNumber(month)) # e.g. november --> 11

            transaction[0] = transaction[0].replace(" ", "/")

            #  --- Type ---  #

            match(transaction[1]):
                case("Incasare"):
                    transaction[1] = transactionTypesEnum[0]
                case ("Cumparare POS"):
                    transaction[1] = transactionTypesEnum[1]
                case("Transfer Home'Bank"):
                    transaction[1] = transactionTypesEnum[2]

            #  --- Value --- #

            if(len(transaction[2]) < 7):
                for i in range (7 - len(transaction[2])):
                    transaction[2] += " "

            #  --- Vendor ---  #

            vendorComponents = transaction[3].split(":")

            if(vendorComponents[0] == "Terminal"): #First component is info on where the transaction took place. Depending on that further processing may be required.
                transaction[3] = vendorComponents[1].split()[0]
            else:
                transaction[3] = vendorComponents[1]

            transactionText += " | ".join(transaction) + "\n"

        fileName = "./Ing Reports/" + year + " " + month + " report.txt"

        if(os.path.isfile(fileName)):
            with open(fileName, "r") as out:
                previousFileText = out.read()
                out.close()
        else:
            print("ING " + month + " " + year + " report has been created.")
            previousFileText = "This file does not exist yet" #It is safer to assign a random string than a blank one. If the file was already blank, by an accident, the repor would not be generated.

        if (previousFileText != transactionText): # Do not rewrite file if it is already the same
            print("ING " + month + " " + year + " report has been updated.")
            with open(fileName, "w") as out:
                out.write(transactionText)
                out.close()
        else:
            print("ING "  + month + " " + year + " report is still the same.")


    # elif(bankName == "Revolut"):
    #     path += os.listdir(path)[1]
    #     path += "/" + os.listdir(path)[0]
    #     with open(path, newline = '') as csvfile:
    #         reader = csv.reader(csvfile, delimiter=',', quotechar='|')

    #         for row in reader:
    #             transactionText += (" ".join(row)) + "\n"

    #     f = open("test.txt", "w")
    #     f.write(transactionText)
    #     f.close()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        if(sys.argv[1] == "ING" or sys.argv[1] == "Revolut"):
            bankStatementFolderPath = "./Statements/" + sys.argv[1]
            for statementFile in os.listdir(bankStatementFolderPath):
                parseStatements(sys.argv[1], bankStatementFolderPath + "/" + statementFile)
        else:
            print("Not a valid command")
    else:
        print(" Provide a Bank (ING or Revolut) \n or \n Request a general report (add report at the end of command)")
