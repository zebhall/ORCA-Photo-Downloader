# Orca Photo Downloader by ZH 2022/06/08


import requests
import csv
import os
import time


print("This program will download .jpg files from photo columns in ORCA spreadsheets, \nand title the images using the corresponding value contained in a specified column.\n")
print("You will need a .csv copy of the sheet, which can be exported from the Orca website.\nThis .csv file should be copied into the same directory as this .py script.\n")
print("The program will create a folder for all of the images in this directory named using\nthe following format: '/ORCAPhotos_*csv-file-name*_YYYY-MM-DD_HHmmSS/.\n")
print("This process may take some time, depending on the number of entries.\nThe program will close once it has downloaded all photos listed in the csv file.\n")

motherCSVname = input("Enter name of mother csv file, not including extension: ")
motherCSVfilename = motherCSVname + ".csv"
motherCSV = open(motherCSVfilename)
motherCSVreader = csv.reader(motherCSV)

header = []
header = next(motherCSVreader)

rows = []
for row in motherCSVreader:
    rows.append(row)

motherCSV.close()

ind = 0
for h in header:
    print(str(ind) + ". "+ h)
    ind+=1

URLIndex = int(input("Enter the column number containing the image URL: "))
nameIndex = int(input("Enter the column number containing the preferred image filename: "))

datetimeData = time.localtime()                             # get struct_time
datetimeString = time.strftime("%Y-%m-%d_%H%M%S", datetimeData)

pathAddress = "ORCAPhotos_"+ motherCSVname+"_"+datetimeString
dir = pathAddress
if not os.path.isdir(dir): 
    os.makedirs(dir)
    print("/"+ pathAddress + " directory created in parent folder.")

for row in rows:
    if row[URLIndex] != '':
        photo = requests.get(row[URLIndex])
        title = (str(row[nameIndex]) + ".jpg")
        fileName = str(pathAddress+'/'+title)
        file = open(fileName, "wb")
        file.write(photo.content)
        file.close()
        print(title + " saved successfully.")
