# Orca Photo Downloader by ZH 2022/06/08


import requests
import csv
import os
import time
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog


# Preamble
print("This program will download .jpg files from photo columns in ORCA spreadsheets, \nand title the images using the corresponding value contained in a specified column.\n")
print("You will need a .csv copy of the sheet, which can be exported from the Orca website.\nThis .csv file should be copied into the same directory as this .py script.\n")
print("The program will create a folder for all of the images in this directory named using\nthe following format: '/ORCAPhotos_*csv-file-name*_YYYY-MM-DD_HHmmSS/.\n")
print("This process may take some time, depending on the number of entries.\nThe program will close once it has downloaded all photos listed in the csv file.\n")






def getCSVdata():
    global motherCSVname
    #motherCSVname = input("Enter name of mother csv file, not including extension: ")
    #motherCSVfilename = motherCSVname + ".csv"
    #motherCSVPath = filedialog.askopenfilename()
    motherCSV = open(motherCSVPath)
    motherCSVreader = csv.reader(motherCSV)

    global header
    header = []
    header = next(motherCSVreader)

    global rows
    rows = []
    global rowCount
    rowCount=0
    for row in motherCSVreader:
        rows.append(row)
        rowCount+=1

    motherCSV.close()


def getColumnChoices():
    ind = 0
    for h in header:
        print(str(ind) + ". "+ h)
        ind+=1

    global URLIndex
    global nameIndex
    URLIndex = int(input("Enter the column number containing the image URL: "))
    nameIndex = int(input("Enter the column number containing the preferred image filename: "))



def getPicQuantity():       # Determines the number of photo urls in sheet
    picCount = 0
    for row in rows:
        if row[URLIndex] != '':
            picCount+=1
    
    return picCount


def getDateTime():          #called by getPhotos
    datetimeData = time.localtime()                             # get struct_time
    datetimeString = time.strftime("%Y-%m-%d_%H%M%S", datetimeData)
    return datetimeString



def getPhotos():   
    dts = getDateTime()
    pathAddress = "ORCAPhotos_" + motherCSVname + "_" + dts          # Name for new folder
                 
    if not os.path.isdir(pathAddress):      # Checks if folder to dump photos into already exists (it won't)
        os.makedirs(pathAddress)            # Creates folder 
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



# UI START
gui = Tk()
gui.title("ORCA Photo Downloader")





gui.mainloop()


getCSVdata()
getColumnChoices()
getPhotos()
