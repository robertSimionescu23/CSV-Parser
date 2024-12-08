import csv
import os
import sys


def monthStringToNumber(month): #Turn the romanian name of a month into it's corresponding number
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

def monthNumberToString(month): #Turn the name of a month into it's corresponding number
    match month:
        case ("01"):
            return "ianuarie"
        case ("02"):
            return "februarie"
        case ("03"):
            return "martie"
        case ("04"):
            return "aprilie"
        case ("05"):
            return "mai"
        case ("06"):
            return "iunie"
        case ("07"):
            return "iulie"
        case ("08"):
            return "august"
        case ("09"):
            return "septembrie"
        case ("10"):
            return "octombrie"
        case ("11"):
            return "noiembrie"
        case ("12"):
            return "decembrie"


transactionTypesEnum = ("Incasare ", "Cumparare", "Transfer ", "Schimb   ") #Make all the same length for better formatting.
#Incasare  - Any monmey coming in, from an account other than mine
#Cumparare - Any money spent
#Transfer  - Money sent to another account. TODO:Check if the account is mine, depricate transfer to the other 2.

########################
### CSV FILE PARSERS ###
########################

#Only get the relevant information from the csv file, leaving another function to format it
def parseINGCSVFile(file):
    statementFilesPath = "./Statements/ING/"

    #Info to be extracted
    transactionDate   = ""
    transcationType   = ""
    transcationValue  = ""
    transactionVendor = ""

    #Full transaction list
    transcationList = []

    checkInNRows = -1 # -1 is normal functioning, no future vendor info sampling planned.

    filePath = statementFilesPath + file

    with open(filePath, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        for row in reader:
            row = list(filter(None, row)) #Remove all empty elements

            if(checkInNRows != -1): #Get the vendor type in N rows
                checkInNRows -= 1

            #For easier reading
            secondLastElement = row[len(row) - 2]
            LastElement       = row[len(row) - 1]

            if(secondLastElement[0] == "\""): #Sums are between " " characters, but divided in 2 elements. Bring them together, and remove quatation marks and decimal point.
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

    return transcationList

def parseRevolutCSVFile(file):
    statementFilesPath = "./Statements/Revolut/"

    #Info to be extracted
    transactionDate   = ""
    transcationType   = ""
    transcationValue  = ""
    transactionVendor = ""

    #Full transaction list
    transcationList = []

    filePath = statementFilesPath + file

    with open(filePath, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        for row in reader:
            if row[0] == "Type": #Skip the first line
                continue

            # -- Date -- #
            transactionDate = row[2].split(" ")[0] #There is also a time refrence, which is not needed.

            # -- Type -- #
            transcationType = row[0]

            # -- Value -- #
            transcationValue = row[5]

            #  -- Vendor -- #
            transactionVendor = row[4]

            transcationList.append([transactionDate, transcationType, transcationValue, transactionVendor])

    return transcationList

#################################
### DATA FORMATTING FUNCTIONS ###
#################################

def formatINGMonthlyReport(monthReport):
    for entry in monthReport:

        for transaction in entry[2]:
        # Formatting the data
            # --- Date --- #
            date = transaction[0].split()
            day = date[0]
            month = monthStringToNumber(date[1])
            year = date[2]

            transaction[0] = "/".join([day, month, year])

            transaction[0] = transaction[0].replace(" ", "/")

            #  --- Type ---  #
            match(transaction[1]):
                case("Incasare"):
                    transaction[1] = transactionTypesEnum[0]
                case ("Cumparare POS"):
                    transaction[1] = transactionTypesEnum[1]
                case("Transfer Home'Bank"):
                    transaction[1] = transactionTypesEnum[2]

            #  --- Value ---
            if(len(transaction[2]) < 7): #Add whitespace
                for i in range (7 - len(transaction[2])):
                    transaction[2] += " "

            #  --- Vendor ---  #
            vendorComponents = transaction[3].split(":")

            if(vendorComponents[0] == "Terminal"): #First component is info on where the transaction took place. Depending on that further processing may be required.
                transaction[3] = vendorComponents[1].split()[0]
            else:
                transaction[3] = vendorComponents[1]

    return monthReport


def formatRevolutMonthlyReport(monthReport):
    for entry in monthReport:

        for transaction in entry[2]:
            # -- Date -- #
            date = transaction[0].replace("-", " ").split(" ")
            year  = date[0]
            month = date[1]
            day   = date[2]

            date = "/".join([day, month, year])

            transaction[0] = date

            # -- Type -- #
            match(transaction[1]):
                case("TOPUP"):
                    transaction[1] = transactionTypesEnum[0]
                case ("CARD_PAYMENT"):
                    transaction[1] = transactionTypesEnum[1]
                case("TRANSFER"):
                    transaction[1] = transactionTypesEnum[2]
                case("EXCHANGE"):
                    transaction[1] = transactionTypesEnum[3]

            # -- Value -- #
            value = float(transaction[2])
            if(value < 0):
                transaction[2] = str(value * (- 1))

            if(len(transaction[2]) < 7): #Add whitespace
                for i in range (7 - len(transaction[2])):
                    transaction[2] += " "
            #  -- Vendor -- # TODO
        entry[2].sort() #sort by day.
        entry[2].sort(key = sortByMonth) #sort by month after sorting by day, thus transactions in the previous day will be at the top.

    monthReport = lintRevolutReport(monthReport)

    return monthReport

### Supporting Functions ###
def sortByMonth(e): #sort the transaction by month, instead of day
    return e[0].split("/")[1]

def lintRevolutReport(revolutMonthlyReports):
    for monthReportNumber, monthlyTransactionList in enumerate(revolutMonthlyReports):

        monthString = monthlyTransactionList[1] # Report has year on pos 0, month on pos 1, full list of month's transactions on 2
        transactionList = monthlyTransactionList[2]

        correctMonthNum = monthStringToNumber(monthString)
        entriesToDelete = 0 # Due to previous formatting, all transactions from previous months are at the top. This function will relocate/remove them.

        for transaction in transactionList:
            transactionMonth = transaction[0].split("/")[1] #The date is formatted as dd/mm/yyyy. By splitting we can get the month, on index 1.
            if (transactionMonth != correctMonthNum):
                if(monthReportNumber > 0): #If the report is not the first a.k.a. we can relocate the transactions to the previous month they belong
                    revolutMonthlyReports[monthReportNumber - 1][2].append(transaction)
                    entriesToDelete += 1
                else:
                    entriesToDelete += 1

        for entry in range(entriesToDelete): #Delete the number of entries needed
            revolutMonthlyReports[monthReportNumber][2].pop(0)

    return revolutMonthlyReports


### CONCATENATE MONTHS INTO A FULL REPORT ###
def createMonthlyReport(bankName):
    statementFilesPath = "./Statements/" + bankName + "/"
    monthreport = [] # A list that will contain, the month, year and transaction of said month
    for file in os.listdir(statementFilesPath): #Iterate to every statement file (CSV) in the ING reports
        if (bankName == "ING"):
            transactionList = parseINGCSVFile(file)
            #We can get the month and year from the first element, as it is always the same format
            date = transactionList[0][0].split(" ")
            month = date[1]
            year  = date[2]
        elif (bankName == "Revolut"):
            transactionList = parseRevolutCSVFile(file)
            date = transactionList[0][0].replace("-", " ").split(" ") #Split by "-" was not working...
            month = monthNumberToString(date[1]) # Get a month string
            year  = date[0]

        monthreport.append([year, month, transactionList])

    return monthreport

### WRITE TO FILES ###
def writeMonthlyReportToFiles(bankName, monthReport):
    for entry in monthReport:

        year  = entry[0]
        month = entry[1]

        fileName = "./" + bankName + " " + "Reports/" + bankName + " " + year + " " + monthStringToNumber(month) + " - " + month + " report.txt" #format it i.e ING 2024 11 noiembrie report.txt
        transactionText = ""

        for transaction in entry[2]:
            transactionText += " | ".join(transaction) + "\n"

        if(os.path.isfile(fileName)):
            with open(fileName, "r") as out:
                previousFileText = out.read()
                out.close()
        else:
            print(bankName + " " + month + " " + year + " report has been created.")
            previousFileText = "This file does not exist yet" #It is safer to assign a random string than a blank one. If the file was already blank, by an accident, the repor would not be generated.

        if (previousFileText != transactionText): # Do not rewrite file if it is already the same
            print(bankName + " " + month + " " + year + " report has been updated.")
            with open(fileName, "w") as out:
                out.write(transactionText)
                out.close()
        else:
            print(bankName + " " + month + " " + year + " report is still the same.")



def processStatements(bankanme):
    monthlyReport = createMonthlyReport(bankanme)
    if(bankanme == "ING"):
        monthlyReport = formatINGMonthlyReport(monthlyReport)
        writeMonthlyReportToFiles(bankanme, monthlyReport)
    elif(bankanme == "Revolut"):
        monthlyReport = formatRevolutMonthlyReport(monthlyReport)
        writeMonthlyReportToFiles(bankanme, monthlyReport)

    for date in monthlyReport: #process into a easy to sort format. Reports will be merged by month basis
        date[0] = date[0] + " " + date[1] #Merge the year and month into a single element, as they do not need to be separate anymore
        date.pop(1)

    return monthlyReport


def parseStatements():
    INGReports = processStatements("ING")
    RevolutReports = processStatements("Revolut")

if __name__ == "__main__":
    parseStatements()
