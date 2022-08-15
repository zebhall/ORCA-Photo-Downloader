# Orca Photo Downloader by ZH 2022/06/08

global versionNum
global versionDate
versionNum = 'v2.0.3'
versionDate = '2022/08/15'

from fileinput import filename
from tkinter.ttk import Progressbar
from unicodedata import name
import requests
import csv
import os
import time
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog


# Preamble
#print("This program will download .jpg files from photo columns in ORCA spreadsheets, \nand title the images using the corresponding value contained in a specified column.\n")
#print("You will need a .csv copy of the sheet, which can be exported from the Orca website.\nThis .csv file should be copied into the same directory as this .py script.\n")
#print("The program will create a folder for all of the images in this directory named using\nthe following format: '/ORCAPhotos_*csv-file-name*_YYYY-MM-DD_HHmmSS/.\n")
#print("This process may take some time, depending on the number of entries.\nThe program will close once it has downloaded all photos listed in the csv file.\n")


def clickBrowseInput():
    motherCSVPath.set(filedialog.askopenfilename(filetypes=[("CSV File", "*.csv")], initialdir = os.getcwd())) # and write into input path text box
    print(motherCSVPath)
    

def clickBrowseOutput():
    outputDirectory.set(filedialog.askdirectory(initialdir = os.getcwd()))
    print(outputDirectory)


def clickReadCSVData():

    motherCSV = open(motherCSVPath.get())
    motherCSVreader = csv.reader(motherCSV)

    global header
    header = []
    header = next(motherCSVreader)
    headerVar.set(header)

    global rows
    rows = []

    global rowCount
    rowCount=0

    for row in motherCSVreader:
        rows.append(row)
        rowCount+=1

    motherCSV.close()


def getPhotoRowCount():
    photoRowCount = 0
    for row in rows:
        if row[URLIndex] != '':
            photoRowCount+=1
    return photoRowCount


def getColumnChoices():
    ind = 0
    for h in header:
        print(str(ind) + ". "+ h)
        ind+=1

    global URLIndex
    global nameIndex
    URLIndex = int(input("Enter the column number containing the image URL: "))
    nameIndex = int(input("Enter the column number containing the preferred image filename: "))


def getDateTime():          #called by getPhotos
    datetimeData = time.localtime()                             # get struct_time
    datetimeString = time.strftime("%Y-%m-%d_%H%M%S", datetimeData)
    return datetimeString


def start_submit_thread(event):
    global submit_thread
    submit_thread = threading.Thread(target=getPhotos)
    submit_thread.daemon = True
    #progressbar.start()
    submit_thread.start()
    gui.after(20, check_submit_thread)


def check_submit_thread():
    if submit_thread.is_alive():
        gui.after(20, check_submit_thread)
    else:
        progressb.stop()
        currentStatus.set("Completed.")


def readyCheck():
    global URLIndex
    global nameIndex

    #if not os.path.isdir(outputDirectory.get):      # Checks if folder to dump photos into already exists (it won't)
        #os.makedirs(outputDirectory.get)            # Creates folder 
        #print(outputDirectory.get + " directory created.")

    if urlListbox.curselection() != '' and nameListbox.curselection() != '':
        URLCurSel = urlListbox.curselection()
        nameCurSel = nameListbox.curselection()
        URLIndex = int(URLCurSel[0])
        nameIndex = int(nameCurSel[0])

        global completedCount
        completedCount = 0
        global totalCount
        totalCount = getPhotoRowCount()
        progressb["maximum"] = totalCount

        print("ready")      #placeholder before error handling
        return 1        # return 1 if ready(no issues)

def updateProgress():
    global completedCount
    completedCount += 1
    currentProgress.set(str(completedCount) + "/" + str(totalCount))
    progressb["value"] = completedCount
    gui.update_idletasks()

def getPhotos():   
    ready = readyCheck()
    if ready:
        greyAll()
        outputDIR = outputDirectory.get()
        for row in rows:
            if row[URLIndex] != '':
                title = (str(row[nameIndex]) + ".jpg")
                fileName = outputDIR + '/' + title

                currentStatus.set(title + " - Accessing Image URL...")
                photo = requests.get(row[URLIndex])

                currentStatus.set(title + " - Creating file...")
                file = open(fileName, "wb")

                currentStatus.set(title + " - Writing file...")
                file.write(photo.content)
                file.close()

                currentStatus.set(title + " - Saved.")
                print(title + " saved.")
                updateProgress()
        
        currentStatus.set("All Files saved successfully.")
    
def greyAll():
    for child in inputFrame.winfo_children():
        child.configure(state='disable')

    for child in selection1Frame.winfo_children():
        child.configure(state='disable')

    for child in selection2Frame.winfo_children():
        child.configure(state='disable')

    for child in outputFrame.winfo_children():
        child.configure(state='disable')

    for child in ctrlFrame.winfo_children():
        child.configure(state='disable')   

def helpMe():
    messagebox.showinfo("ORCA Photo Downloader - Help", "Help Text goes here")

# UI START
gui = Tk()
gui.title("ORCA Photo Downloader")
gui.wm_attributes('-toolwindow', 'True')

#Frames

inputFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, fg = "#545454", text = "Input CSV File")
inputFrame.grid(row=1, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)

selection1Frame = LabelFrame(gui, width = 20, height = 50, pady = 5, padx = 5, fg = "#545454", text = "Image Filename Column")
selection1Frame.grid(row=2, column=1, columnspan=1, pady = 0, padx = 5, sticky= EW)

selection2Frame = LabelFrame(gui, width = 20, height = 50, pady = 5, padx = 5, fg = "#545454", text = "Image URL Column")
selection2Frame.grid(row=2, column=2, columnspan=1, pady = 0, padx = 5, sticky= EW)

outputFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, fg = "#545454", text = "Output Folder")
outputFrame.grid(row=3, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)

statusFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, fg = "#545454", text = "Status")
statusFrame.grid(row=4, column=1, columnspan=2, pady = 0, padx = 5, sticky= EW)

ctrlFrame = Frame(gui, width = 200, height = 50, pady = 5, padx = 5)
ctrlFrame.grid(row=5, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)


# InputFrame Widgets

motherCSVPath = StringVar()
inputEntry = Entry(inputFrame, width = 31, textvariable = motherCSVPath)
inputEntry.grid(column=1, row=1, padx=5, pady=5, ipadx=20, ipady=1, sticky = EW, columnspan= 3)

inputBrowse = Button(inputFrame, width = 5, text = "Browse", command=clickBrowseInput)
inputBrowse.grid(column=4, row=1, padx=5, pady=5, ipadx=5, ipady=0)

inputGo = Button(inputFrame, width = 11, text = "Read CSV Data", fg = "green", command=clickReadCSVData)
inputGo.grid(column=5, row=1, padx=5, pady=5, ipadx=5, ipady=0)


# Selection1Frame Widgets
headerVar = StringVar()
nameListbox = Listbox(selection1Frame, width = 30, listvariable = headerVar, exportselection=0)
nameListbox.grid(column=1, row=1, padx=5, pady=5, sticky = NSEW)


# Selection2Frame Widgets
urlListbox = Listbox(selection2Frame, width = 30, listvariable = headerVar,exportselection=0)
urlListbox.grid(column=1, row=1, padx=5, pady=5, sticky = NSEW)


# OutputFrame Widgets
outputDirectory = StringVar()
outputEntry = Entry(outputFrame, width = 48, textvariable = outputDirectory)
outputEntry.grid(column=1, row=1, padx=5, pady=5, ipadx=20, ipady=1, sticky = EW, columnspan= 3)

outputBrowse = Button(outputFrame, width = 5, text = "Browse", command=clickBrowseOutput)
outputBrowse.grid(column=4, row=1, padx=5, pady=5, ipadx=5, ipady=0)


# StatusFrame Widgets
progressb = Progressbar(statusFrame, orient = HORIZONTAL, length = 400, mode = "determinate")
progressb.grid(column = 1, columnspan= 2, row = 1, padx=5, pady=5, sticky = EW)

currentStatus = StringVar()
currentStatus.set("...")
currentStatusDisplay = Label(statusFrame, textvariable = currentStatus, anchor = W, fg = "#545454")
currentStatusDisplay.grid(column = 1, row = 2, padx=5, pady=5, sticky = W)

currentProgress = StringVar()
currentProgress.set("0 / 0")
currentProgressDisplay = Label(statusFrame, textvariable = currentProgress, anchor = W, fg = "#545454")
currentProgressDisplay.grid(column = 1, row = 3, padx=5, pady=5, sticky = W)


# ctrlFrame Widgets
startDownload = Button(ctrlFrame, width = 11, text = "Start Download", fg = "green", command=lambda:start_submit_thread(None))
startDownload.grid(column = 1, row = 1, padx=5, pady=5, ipadx=15, ipady= 2, sticky = NW)

copyrightNotice = Label(ctrlFrame, text = "Created by ZH for Portable Spectral Services", anchor = W, fg = "#b5b5b5")
copyrightNotice.grid(column = 1, row = 2, padx=5, pady=0, sticky = SW)

versionNotice = Label(ctrlFrame, text = (versionNum + " - " + versionDate), anchor = W, fg = "#b5b5b5")
versionNotice.grid(column = 1, row = 3, padx=5, pady=0, sticky = SW)

iuoNotice = Label(ctrlFrame, text = "FOR INTERNAL USE ONLY", anchor = W, fg = "#b5b5b5")
iuoNotice.grid(column = 1, row = 4, padx=5, pady=0, sticky = SW)

#helpButton = Button(ctrlFrame, width = 1, text = " ? ", command=helpMe)
#helpButton.grid(column = 2, row = 1, padx=5, pady=0, ipadx=1, ipady= 1, sticky = W)


gui.mainloop()


#getCSVdata()
#getColumnChoices()
#getPhotos()
