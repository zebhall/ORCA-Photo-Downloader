# Orca Photo Downloader by ZH 2022/06/08

global versionNum
global versionDate
versionNum = 'v2.2.2'
versionDate = '2022/10/28'

from fileinput import filename
from multiprocessing.sharedctypes import Value
from tkinter.ttk import Progressbar
from unicodedata import name
import requests
import csv
import os
import time
import sys
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font as tkFont
import asyncio
import aiohttp
import aiofiles
import validators
import xlrd



# Preamble
#print("This program will download .jpg files from photo columns in ORCA spreadsheets, \nand title the images using the corresponding value contained in a specified column.\n")
#print("You will need a .csv copy of the sheet, which can be exported from the Orca website.\nThis .csv file should be copied into the same directory as this .py script.\n")
#print("The program will create a folder for all of the images in this directory named using\nthe following format: '/ORCAPhotos_*csv-file-name*_YYYY-MM-DD_HHmmSS/.\n")
#print("This process may take some time, depending on the number of entries.\nThe program will close once it has downloaded all photos listed in the csv file.\n")


def clickBrowseInput():
    motherCSVPath.set(filedialog.askopenfilename(filetypes=[("CSV File", "*.csv")], initialdir = os.getcwd())) # and write into input path text box
    print(f'Input Path: {motherCSVPath.get()}')
    

def clickBrowseOutput():
    outputDirectory.set(filedialog.askdirectory(initialdir = os.getcwd()))
    print(f'Output Directory: {outputDirectory.get()}')


def clickReadCSVData():

    with open(motherCSVPath.get(), encoding='utf-8') as motherCSV:
        motherCSVreader = csv.reader(motherCSV)
        global header
        header = []
        header = next(motherCSVreader)
        headerVar.set(header)


def readRelevantColumns():
    with open(motherCSVPath.get(), encoding='utf-8') as motherCSV:
        motherCSVreader = csv.reader(motherCSV)
        next(motherCSVreader)
        global rows
        rows = []
        global rowCount
        rowCount=1

        invalidChars = ['<','>',':','"','/','\\','|','?','*']
        invalidEndChars = ['.',' ']
        

        for row in motherCSVreader:

            rowCount+=1

            if row[nameIndex] == '' or row[URLIndex] == '':
                continue

            if any(x in row[nameIndex] for x in invalidChars):
                print(f'File name "{row[nameIndex]}" in row {rowCount} contains invalid characters. Program will skip this image.')
                messagebox.showerror(title = 'File Name Error', message = (f'File name "{row[nameIndex]}" in row {rowCount} contains invalid characters. Program will skip this image.'))
                continue

            if any(x in row[nameIndex][-1] for x in invalidEndChars):
                print(f'File name "{row[nameIndex]}" in row {rowCount} contains invalid characters. Filenames cannot end with a space or a period. Program will skip this image.')
                messagebox.showerror(title = 'File Name Error', message = (f'File name "{row[nameIndex]}" in row {rowCount} contains invalid characters. Filenames cannot end with a space or a period. Program will skip this image.'))
                continue
            
            if validators.url(row[URLIndex]) != TRUE:
                print(f'URL in row {rowCount} is invalid. Program will skip this image.')
                messagebox.showerror(title = 'URL Validity Error', message = (f'URL "{row[URLIndex]}" in row {rowCount} is invalid. Program will skip this image.'))
                continue

            newRow = [row[nameIndex], row[URLIndex]]
            rows.append(newRow)
        
    print(f'{len(rows)} valid Name/URL pairs found.')
            


def getPhotoRowCount():
    photoRowCount = 0
    for row in rows:
        if row[1] != '':
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

def monthN(month):
    match month:
        case 'Jan':
            return 1
        case 'Feb':
            return 2
        case 'Mar':
            return 3
        case 'Apr':
            return 4
        case 'May':
            return 5
        case 'Jun':
            return 6
        case 'Jul':
            return 7
        case 'Aug':
            return 8
        case 'Sep':
            return 9
        case 'Oct':
            return 10
        case 'Nov':
            return 11
        case 'Dec':
            return 12


def start_submit_thread(event):
    global submit_thread
    submit_thread = threading.Thread(target=getPhotos)
    submit_thread.daemon = True
    #progressbar.start()
    submit_thread.start()
    gui.after(20, check_submit_thread)


def check_submit_thread():
    if submit_thread.is_alive():
        currentProgress.set(str(completedCount) + "/" + str(totalCount))
        progressb["value"] = completedCount
        gui.after(20, check_submit_thread)
    else:
        progressb.stop()
        currentStatus.set("Completed.")


async def downloadImage(row, session):
    url = row[1]
    #print(url)
    title = (str(row[0]) + ".jpg")
    fileName = outputDIR + '/' + title
    if row[1] != '':
        async with session.get(url) as response:
            async with aiofiles.open(fileName, "wb") as f:
                await f.write(await response.read())
                #print(response.headers.get('Last-Modified'))
                dt = response.headers.get('Last-Modified')
                xldt = xlrd.xldate.xldate_from_datetime_tuple((int(dt[12:16]), monthN(dt[8:11]),int(dt[5:7]), int(dt[17:19]), int(dt[20:22]), int(dt[23:25])),0)
                timestamps.append([row[0],url,xldt,dt])
    updateProgress()



async def downloadAll():
    global timestamps
    timestamps = [['File Name', 'URL', 'Image Uploaded (excel-format)', 'Image Uploaded (plaintext)']]
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[downloadImage(row, session) for row in rows]
        )

    #print(timestamps)
    if (wantsTimestamps.get() == 1):
        with open((outputDIR+'/Timestamps.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            for row in timestamps:
                writer.writerow(row)


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
        totalCount = 0

        readRelevantColumns()

        totalCount = getPhotoRowCount()

        progressb["maximum"] = totalCount

        print("Ready to Download Files.")      #placeholder before error handling
        return 1        # return 1 if ready(no issues)

def updateProgress():
    global completedCount
    if completedCount < totalCount:
        completedCount += 1
        currentProgress.set(str(completedCount) + "/" + str(totalCount))
        progressb["value"] = completedCount
    gui.update_idletasks()

def getPhotos():   
    ready = readyCheck()
    if ready:
        greyAll()
        global outputDIR
        outputDIR = outputDirectory.get()
        currentStatus.set("Downloading and Saving...")
        asyncio.run(downloadAll())

        # for row in rows:
        #     if row[1] != '':
        #         title = (str(row[0]) + ".jpg")
        #         fileName = outputDIR + '/' + title

        #         currentStatus.set(title + " - Accessing Image URL...")
        #         photo = requests.get(row[1])

        #         currentStatus.set(title + " - Creating file...")
        #         file = open(fileName, "wb")

        #         currentStatus.set(title + " - Writing file...")
        #         file.write(photo.content)
        #         file.close()

        #         currentStatus.set(title + " - Saved.")
        #         print(title + " saved.")
        #         updateProgress()
        #     else:
        #         print(row[0]+" - URL Invalid or Missing.") 

        currentStatus.set("Files saved successfully.")
    
def greyAll():
    for child in inputFrame.winfo_children():
        child.configure(state='disable')

    for child in selection1Frame.winfo_children():
        child.configure(state='disable')

    for child in selection2Frame.winfo_children():
        child.configure(state='disable')

    for child in outputFrame.winfo_children():
        child.configure(state='disable')

    for child in optionsFrame.winfo_children():
        child.configure(state='disable')

    for child in ctrlFrame.winfo_children():
        child.configure(state='disable')   

def helpMe():
    messagebox.showinfo("ORCA Photo Downloader - Help", "Help Text goes here")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# UI START
gui = Tk()
gui.title("ORCA Photo Downloader")
#gui.wm_attributes('-toolwindow', 'True')
iconpath = resource_path("pss.ico")
gui.iconbitmap(iconpath)

# Fonts
consolas24 = tkFont.Font(family='Consolas', size=24)
consolas20 = tkFont.Font(family='Consolas', size=20)
consolas18 = tkFont.Font(family='Consolas', size=18)
consolas18B = tkFont.Font(family='Consolas', size=18, weight = 'bold')
consolas16 = tkFont.Font(family='Consolas', size=16)
consolas12 = tkFont.Font(family='Consolas', size=12)
consolas10 = tkFont.Font(family='Consolas', size=10)
consolas10B = tkFont.Font(family='Consolas', size=10, weight = 'bold')
consolas09 = tkFont.Font(family='Consolas', size=9)
consolas08 = tkFont.Font(family='Consolas', size=8)

#Frames

inputFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Input CSV File")
inputFrame.grid(row=1, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)

selection1Frame = LabelFrame(gui, width = 20, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Image Filename Column")
selection1Frame.grid(row=2, column=1, columnspan=1, pady = 0, padx = 5, sticky= EW)

selection2Frame = LabelFrame(gui, width = 20, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Image URL Column")
selection2Frame.grid(row=2, column=2, columnspan=1, pady = 0, padx = 5, sticky= EW)

outputFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Output Folder")
outputFrame.grid(row=3, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)

optionsFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Options")
optionsFrame.grid(row=4, column=1, columnspan=2, pady = 0, padx = 5, sticky= EW)

statusFrame = LabelFrame(gui, width = 200, height = 50, pady = 5, padx = 5, font = consolas10, fg = "#545454", text = "Status")
statusFrame.grid(row=5, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)

ctrlFrame = Frame(gui, width = 200, height = 50, pady = 5, padx = 5)
ctrlFrame.grid(row=6, column=1, columnspan=2, pady = 5, padx = 5, sticky= EW)


# InputFrame Widgets

motherCSVPath = StringVar()
inputEntry = Entry(inputFrame, width = 31, font = consolas10, textvariable = motherCSVPath)
inputEntry.grid(column=1, row=1, padx=5, pady=5, ipadx=20, ipady=1, sticky = EW, columnspan= 3)

inputBrowse = Button(inputFrame, width = 5, text = "Browse", font = consolas10, fg = "#FDFEFE", bg = "#566573", command=clickBrowseInput)
inputBrowse.grid(column=4, row=1, padx=5, pady=5, ipadx=5, ipady=0)

inputGo = Button(inputFrame, width = 8, text = "Read Data", font = consolas10, fg = "#FDFEFE", bg = "#2E86C1",  command=clickReadCSVData)
inputGo.grid(column=5, row=1, padx=5, pady=5, ipadx=5, ipady=0)


# Selection1Frame Widgets
headerVar = StringVar()
nameListbox = Listbox(selection1Frame, width = 26, listvariable = headerVar, exportselection=0, font = consolas10)
nameListbox.grid(column=1, row=1, padx=5, pady=5, sticky = NSEW)


# Selection2Frame Widgets
urlListbox = Listbox(selection2Frame, width = 26, listvariable = headerVar,exportselection=0,  font = consolas10)
urlListbox.grid(column=1, row=1, padx=5, pady=5, sticky = NSEW)


# OutputFrame Widgets
outputDirectory = StringVar()
outputEntry = Entry(outputFrame, width = 43, font = consolas10, textvariable = outputDirectory)
outputEntry.grid(column=1, row=1, padx=5, pady=5, ipadx=20, ipady=1, sticky = EW, columnspan= 3)

outputBrowse = Button(outputFrame, width = 5, text = "Browse", font = consolas10, fg = "#FDFEFE", bg = "#566573", command=clickBrowseOutput)
outputBrowse.grid(column=4, row=1, padx=5, pady=5, ipadx=5, ipady=0)


# OptionsFrame Widgets
wantsTimestamps = IntVar()
timestampCheckBox = Checkbutton(optionsFrame, text = 'Generate Image Timestamps CSV', variable = wantsTimestamps, onvalue = 1, offvalue = 0, font = consolas10, fg = "#566573")
timestampCheckBox.grid(column=1, row=1, padx=0, pady=0, ipadx=5, ipady=1, sticky = EW, columnspan= 2)

# StatusFrame Widgets
progressb = Progressbar(statusFrame, orient = HORIZONTAL, length = 400, mode = "determinate")
progressb.grid(column = 1, columnspan= 2, row = 1, padx=5, pady=5, sticky = EW)

currentStatus = StringVar()
currentStatus.set("...")
currentStatusDisplay = Label(statusFrame, textvariable = currentStatus, anchor = W, font = consolas08, fg = "#545454")
currentStatusDisplay.grid(column = 1, row = 2, padx=5, pady=5, sticky = W)

currentProgress = StringVar()
currentProgress.set("0 / 0")
currentProgressDisplay = Label(statusFrame, textvariable = currentProgress, anchor = W, font = consolas08, fg = "#545454")
currentProgressDisplay.grid(column = 1, row = 3, padx=5, pady=5, sticky = W)


# ctrlFrame Widgets
startDownload = Button(ctrlFrame, width = 13, text = "Start Download", font = consolas12, fg = "#FDFEFE", bg = "#27AE60", command=lambda:start_submit_thread(None))
startDownload.grid(column = 1, row = 1, padx=5, pady=5, ipadx=15, ipady= 2, sticky = NW)

copyrightNotice = Label(ctrlFrame, text = "Created by ZH for Portable Spectral Services", anchor = W, font = consolas08, fg = "#b5b5b5")
copyrightNotice.grid(column = 1, row = 2, padx=5, pady=0, sticky = SW)

versionNotice = Label(ctrlFrame, text = (versionNum + " - " + versionDate), anchor = W, font = consolas08, fg = "#b5b5b5")
versionNotice.grid(column = 1, row = 3, padx=5, pady=0, sticky = SW)

iuoNotice = Label(ctrlFrame, text = "FOR INTERNAL USE ONLY", anchor = W, font = consolas08, fg = "#b5b5b5")
iuoNotice.grid(column = 1, row = 4, padx=5, pady=0, sticky = SW)

#helpButton = Button(ctrlFrame, width = 1, text = " ? ", command=helpMe)
#helpButton.grid(column = 2, row = 1, padx=5, pady=0, ipadx=1, ipady= 1, sticky = W)


gui.mainloop()


#getCSVdata()
#getColumnChoices()
#getPhotos()
