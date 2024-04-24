import requests
import numpy as np
import pandas as pd
from time import sleep

setKey = input("Enter SteamWebAPIKey: ")
if (setKey.upper() == 'D'):
    key = "<YOURKEY>"
else:
    key = setKey
if (not setKey):
    raise Exception("SteamWebAPIKey is required. Go to https://steamcommunity.com/dev/ to learn more")

setSteamId = input("Enter seed steamId: ")
if (setSteamId.upper() == 'D'):
    steamid = "<YOURID>"
else:
    steamid = setSteamId
if (not setSteamId):
    raise Exception("steamid is required")

try:
    depth = int(input("Enter search depth: "))
    if (depth < 1):
        raise Exception("Depth must be greater than zero")
except:
    raise Exception("Depth should be an integer")
friendsUrl = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=' \
+ key + '&steamid=' + steamid + '&relationship=friend'
print('got url: ' + friendsUrl)
print('search depth: ' + str(depth))
execute = input("Execute? (Y/N): ")
if (execute.upper() == 'N'):
    exit()

#open a file here
fData = open("friendsData.csv", 'w')
fData.write("steamid,friendId")

gData = open("gameData.csv", 'w')
gData.write("steamid,gameAppId,appname,playtimeAll")

#open a list to queue here
queue = []
queue.append(steamid)

#add list of done requests
done = []

current = 1
while True:
    nextQueue = []
    for i in queue:
        print("current: " + str(current))
        print("currentId: " + str(i))
        print("queue: " + str(len(queue)))
        print("done requests: " + str(len(done)))
        friendsUrl = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=' \
        + key + '&steamid=' + i + '&relationship=friend'
        try:
            if (not i in done):
                steamid = i
                done.append(i)  
                friendsResponse = requests.get(friendsUrl).json()["friendslist"]
                for i in friendsResponse["friends"]:
                    if (current <= depth):
                        nextQueue.append(i["steamid"])
                    row = "\n" + steamid + "," + str(i["steamid"])
                    fData.write(row)
        except:
            continue
    queue.clear()
    queue = nextQueue.copy()
    nextQueue.clear()
    print("queue: " + str(len(queue)))
    print("done requests: " + str(len(done)))
    #check if next depth is greater than limit
    current += 1
    if (current > depth):
        fData.close()
        print("generating game library data...")
        fdd = pd.read_csv("friendsData.csv")
        ufds = fdd.steamid.unique()
        ffds = fdd.friendId.unique()
        cf = []
        for i in ufds:
            cf.append(i)
        for i in ffds:
            if (i not in cf):
                cf.append(i)
        zeta = 1
        for i in cf:
            zeta += 1
            print("step " + str(zeta) + " of " + str(len(cf)))
            try:
                gamesOwnedUrl = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' \
                + key + '&steamid=' + str(i) + '&include_appinfo=true'
                gamesOwnedResponse = requests.get(gamesOwnedUrl).json()["response"]
                for x in gamesOwnedResponse["games"]:
                    appname = str(x["name"]).replace(',','.')
                    row = "\n" + str(i) + "," + str(x["appid"]) + "," + appname + "," + str(x["playtime_forever"])
                    gData.write(row)
                print("user not private, continuing") 
            except:
                print("user is private")
                row = "\n" + str(i) + ",private,private,private"
                gData.write(row)
        print("game library data generated")
        gData.close()
        print("cleaning up...")
        sleep(1)
        dfs = pd.read_csv("gameData.csv", encoding = 'unicode_escape')
        print("removing private games...")
        dfsp = dfs.drop(dfs[dfs['playtimeAll'] == 'private'].index)
        print("removing 0 minutes playtime. . .")
        dfspz = dfsp.drop(dfsp[dfsp['playtimeAll'] == '0'].index)
        dfspz.to_csv("enhancedGameDataNoZero.csv")
        print("Successfully processed queue of " + str(len(done)) + " requests")
        break
print("You run personaMapper.py to generate a persona dataset")
input("Press any key to continue")