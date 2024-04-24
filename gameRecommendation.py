
import json
import requests
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from node2vec import Node2Vec #To run node2vec algorithm
from gensim.models import Word2Vec #To load trained model
from bs4 import BeautifulSoup as B

EMBEDDING_FILENAME = './embeddings.emb'
EMBEDDING_MODEL_FILENAME = './embeddings.model'
GAME_DETAIL_LINK = "http://store.steampowered.com/api/appdetails?appids={}&cc=tw"
STORE_PAGE_LINK = "https://store.steampowered.com/app/{}"
COOKIES = {'birthtime': '568022401'}
gamesOwnedUrl = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}'
key = '<YOURKEY>'
maxGameCount = 3

# get steam id from input
steamId = "<YOURID>"
if (not steamId):
    raise Exception("steamid is required")

gamesOwnedResponse = requests.get(gamesOwnedUrl.format(key, steamId)).json()["response"]
gameOwned = pd.json_normalize(gamesOwnedResponse['games'])
gameOwned = gameOwned.sort_values(by=['playtime_forever'], ascending=False)

# Generate similiar games to given tag
model = Word2Vec.load(EMBEDDING_MODEL_FILENAME)
similarGames = []
favoriteGame = []
finalResult = []
counter = 0

def similarGame(appid):
    counter = 0
    for node, prob in model.wv.most_similar(appid):
        similarGames.append(node)
        counter += 1
        if(counter == 3):
            break
        
def getGameDetail(game):
    try:
        gameDetailResponse = requests.get(GAME_DETAIL_LINK.format(game)).json()
    except:
        print("Abnormal response from steam with gameid:{}", game)
    
    if (not gameDetailResponse[str(game)]['success']):
        return False
    return gameDetailResponse[str(game)]['data']

def buildGameDetail(game, parent):
    gameDetailResponse = getGameDetail(game)

    if(not gameDetailResponse):
        return False

    gameDetail = {}
    gameDetail['isFree'] = gameDetailResponse['is_free']
    gameDetail['releaseDate'] = gameDetailResponse['release_date']
    gameDetail['image'] = gameDetailResponse['header_image']
    gameDetail['gameName'] = gameDetailResponse['name']
    gameDetail['id'] = gameDetailResponse['steam_appid']

    if (not gameDetailResponse['is_free'] and 'price_overview' in gameDetailResponse):
        gameDetail['price'] = gameDetailResponse['price_overview']['final_formatted']
    if ('genres' in gameDetailResponse):
        gameDetail['genre'] = "_".join([str(genre['description']) for genre in gameDetailResponse['genres']])
    if ('developers' in gameDetailResponse):
        gameDetail['developer'] = gameDetailResponse['developers'][0]
    if ('publishers' in gameDetailResponse):
        gameDetail['publisher'] = gameDetailResponse['publishers'][0]
    if (parent is not None):
        gameDetail['parent'] = parent

    try:
        htmlTags = requests.get(STORE_PAGE_LINK.format(game), cookies=COOKIES).text
        bs = B(htmlTags, "html.parser")
        gameTags = bs.find_all(class_ = "app_tag")
        gameDetail['tags'] = ",".join([tags.text.strip() for tags in gameTags])[:-2]
    except:
        print("Steam didnt reply on game {} store page".format(game))

    return gameDetail

for index, game in gameOwned.iterrows():
    appid = "{:0.0f}".format(game['appid'])
    try:
        similarGame(appid)
        favoriteGame.append(appid)
        print("{} selected as favorite game".format(appid))
        if(len(favoriteGame) == maxGameCount):
            break
    except:
        print("{} not available in dataset".format(appid))

for game in similarGames:
    parentData = buildGameDetail(favoriteGame[0], None)
    finalResult.append(buildGameDetail(game, parentData))
    print(favoriteGame)
    if(len(finalResult) % maxGameCount == 0):
        favoriteGame.pop(0)

with open("games.json", "w", encoding='utf-8') as f:
    json.dump(finalResult, f)
    f.close()