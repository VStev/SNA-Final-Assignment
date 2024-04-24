import requests
import numpy as np
import pandas as pd

setKey = input("Enter SteamWebAPIKey: ")
if (setKey.upper() == 'D'):
    key = "<YOURKEY>"
else:
    key = setKey
if (not setKey):
    raise Exception("SteamWebAPIKey is required. Go to https://steamcommunity.com/dev/ to learn more")

print("I will assume directory is correct.")

try:
    nUser = int(input("Number of users/folder: "))
    if (nUser < 1):
        raise Exception("Number must be greater than zero")
    if (nUser > 5):
        raise Exception("Not too much!")
    conFrame = []
    for i in range(nUser):
        filename = "user-" + str(i) + "/enhancedGameDataNoZero.csv"
        df = pd.read_csv(filename)
        conFrame.append(df)
    cf = pd.concat(conFrame)
except:
    raise Exception("Cant find those folders, make sure you have a valid folder name and check your directory.")

print("check this first, is this ok?")
print(cf.head())
uniqueIds = cf.steamid.unique()
print("Uniques")
for i in uniqueIds:
   print(i)
print("contains " + str(len(uniqueIds)) + " UIDs")
execute = input("Proceed? Type y to continue ")
if (execute.upper() != 'Y'):
    input("Cancelled by user, press enter to continue")
    exit()
max = len(uniqueIds)
cr = 1
print("proceeding. . .")
print("creating files...")
fData = open("personaMapped.csv", 'w')
fData.write("steamid,persona")
print("file created")
for i in uniqueIds:
  print("processing queue. . .")
  print(str(cr) + " out of " + str(max))
  steamid = str(i)
  nameMapUrl = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" \
        + key + '&steamids=' + steamid
  try:
    nameMap = requests.get(nameMapUrl).json()['response']
    for x in nameMap['players']:
      persona = str(x["personaname"]).replace(',','.')
      row = "\n" + steamid + "," + persona
      fData.write(row)
      print("request success, writing to file. . .")
  except:
    row = "\n" + steamid + ",private"
    fData.write(row)
    print("request error, writing to file as private. . .")
  cr += 1
fData.close()
generate = input("Mapping finished. There's some private profiles, enter Z to generate another file without private users. Enter anything to close this program.")
if (generate.upper() != 'Z'):
    input("Process finished.")
    exit()
print("loading files. . .")
prv = pd.read_csv("personaMapped.csv", encoding = 'unicode_escape')
print("deleting private profiles. . .")
prv = prv.drop(prv[prv['persona'] == 'private'].index)
print("dumping into csv")
prv.to_csv("personaMappedNoPrivate.csv")
input("Finished. Press any key to continue")
