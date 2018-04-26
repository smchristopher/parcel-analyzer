#Python3 script for calculating parcel vacancy for consecutive years 

#This code was written as a project for GIS Programming.
#The customer is Dr. Galen Newman, a professor in Urban Planning at TAMU.
#Dr. Newman is utilizing this code for researching property vacancy in Detroit, MI.

#Inputs: .csv containing Parcel ID and property vacancy
#Outputs: .csv with Parcel ID and value for consecutive vacant years

import os, arcpy, re

allParcels = {}  # global dict for all parcels
ws = raw_input(
    'Path example: C:\Users\Sean\Downloads\Minn_Parcels\\test.gdb\nPlease enter the path for the .gdb that contains parcel feature classes: ')
arcpy.env.workspace = ws  # sets workspace to input
outFile = raw_input(
    'Please specify the name of the output csv: ')  # specify name of output file, outputs to same .gdb as parcels


def find_year(gdb_files):  # verifies each file as a parcel file and returns a name with the year
    list_years = []
    year = 0
    file_name = gdb_files.split('_')

    if re.match(r'parcel\d{2}$', file_name[1]):
        parcel_yr = file_name[1]
        current_year = 2025
        year = int(parcel_yr[-2:]) + 2000
        if year > current_year:
            year = year - 100
        list_years.append(year)
        list_years.append(True)
    else:
        list_years.append(0)
        list_years.append(False)
    #return list_years
    return list_years


def writeParcels(fc):  # creates the list of parcels that are vacant in each year
    parcelDict = []
    expression = "USE1_DESC LIKE 'Vacant%'"  #sql expression
    cursor = arcpy.da.SearchCursor(fc, ['PIN', 'USE1_DESC'], where_clause=expression)

    for row in cursor:
        if row[0] not in allParcels.keys():
            tempParc = {row[0]: []}
            allParcels.update(tempParc)
        parcelDict.append(row[0])
    return parcelDict


def writeDict():  # creates dictionary with keys for each year. each key has a value that is another dict with the parcel and land value
    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []
    yearDict = {}

    for fc in sorted(arcpy.ListFeatureClasses()):
        verify = []
        verify = find_year(fc)
        tempDict = {}
        if verify[1]:
            tempList = writeParcels(fc)
            yearDict[verify[0]] = tempList
            print('Processing ' + fc + '...')
        else:
            continue
    return yearDict


def vacantYears(years):  # main function to calculate years parcel is vacant
    print('Finding vacant years....')
    for parcel in sorted(allParcels.keys()):  # for each parcel in all parcels
        for year in sorted(years.keys()):  # for each year
            if parcel in years[year]:  # checks if a parcel is in each year
                allParcels[parcel].append(year)
            else:
                continue


def consecutiveAnalysis():  # checks for consecutive years
    print('Calculating vacancy periods for each parcel.....')
    for key in sorted(allParcels.keys()):  # for each parcel in list of parcels
        count = 0  # counter for consecutive years
        for i in range(1, len(allParcels[key])):
            if allParcels[key][i - 1] == (allParcels[key][i] - 1):
                count += 1
            else:
                count += 1
                writeOut(count, str(allParcels[key][i - count]), str(key))
                count = 0
        writeOut(count + 1, str(allParcels[key][0]), str(key))


def writeOut(cnt, year, parcel):  # writes output to file
    outputFile = open(ws + '/' + outFile + '.csv', 'a')
    outputFile.write(parcel + ',' + year + ',' + str(cnt) + '\n')
    outputFile.close


def main():  # main driver
    parcelDictionary = writeDict()
    vacantYears(parcelDictionary)
    consecutiveAnalysis()

    print('\n\nAll done! The .csv is located in the input geodatabase. Thanks!')


main()