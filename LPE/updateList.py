import requests
import sys
import json
import pyperclip

response = requests.get("https://www.loldrivers.io/api/drivers.json") # make request to api endpoint for loldrivers

if response.status_code != 200:
    print("Error retrieving list of loldrivers, please try again.")
    sys.exit(0)

raw = response.json()

driverList = []

for i in range(len(raw)):
    data = raw[i]

    # extract information
    driverCategory = data['Category']
    driverName = data['Tags'][0]
    useCase = data['Commands']['Usecase']
    mitreID = data['MitreID']
    description = data['Commands']['Description']
    operatingSystem = data['Commands']['OperatingSystem']

    driverDict = {
        "DriverName" : driverName,
        "DriverCategory" : driverCategory,
        "UseCase" : useCase,
        "OperatingSystem" : operatingSystem,
        "Description" : description,
        "MitreID" : mitreID
    }

    driverList.append(driverDict)

json_output = json.dumps(driverList, indent=4)
pyperclip.copy(json_output)

print("Data copied to clipboard, paste it on driverchecker.ps1!")



