


import requests
import csv


motherCSVname = input("Enter name of mother csv file, including extension: ")
motherCSV = open(motherCSVname)
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

URLIndex = int(input("Enter column number containing image URL: "))
nameIndex = int(input("Enter column number containing preferred image filename: "))

for row in rows:
    if row[URLIndex] != '':
        photo = requests.get(row[URLIndex])
        title = (str(row[nameIndex]) + ".jpg")
        file = open(title, "wb")
        file.write(photo.content)
        file.close()
        print(title + " saved successfully.")



#print(header)
#print(rows)

#input()