import json

with open('JSON Files/datetime.txt', 'r') as txt_file:
    print("Reading datetime from txt file")
    timeOfLastUpdate = txt_file.read()

def gettimeOfLastUpdate():
    return timeOfLastUpdate

def settimeOfLastUpdate(newTime):
    timeOfLastUpdate = str(newTime)
