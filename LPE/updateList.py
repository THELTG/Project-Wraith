import requests
import sys
import json

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
    description = data['Commands']['Description']
    operatingSystem = data['Commands']['OperatingSystem']
    resources = data['Resources']
    driverDict = {
        "DriverName" : driverName,
        "DriverCategory" : driverCategory,
        "UseCase" : useCase,
        "OperatingSystem" : operatingSystem,
        "Description" : description,
    }
    driverList.append(driverDict)

json_output = json.dumps(driverList)

origin = open("driverchecker.ps1",'r').read()
replacetext = "###landingzone###" + origin.split("###landingzone###")[1] + "###landingzone###"
newtext = f"###landingzone###\n$driver = @\"\n{json_output}\n\"@\n###landingzone###"
open("driverchecker.ps1",'w').write(origin.replace(replacetext,newtext))

