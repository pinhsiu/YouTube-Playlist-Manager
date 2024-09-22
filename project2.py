import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import re

from matplotlib.pyplot import title
from sympy import as_finite_diff, public

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

credentials = flow.run_console()
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# 定義顏色
class colors:
        reset = '\033[0m'
        gray = '\033[90m'
        red = '\033[91m'
        green = '\033[92m'
        yellow = '\033[93m'
        blue = '\033[94m'
        magenta = '\033[95m'
        cyan = '\033[96m'

# 列出所有影片
def show(playlistID):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    for i in range(len(response["items"])):
        print(response["items"][i]["snippet"]["title"])

# 新增影片
def insert(url, playlistID):
    request = youtube.playlistItems().insert(
        part = "snippet",
        body = {
          "snippet" : {
            "playlistId" : playlistID,
            "position" : 0,
            "resourceId" : {
              "kind" : "youtube# video",
              "videoId" : url
            }
          }
        }
    )
    request.execute()
    print(colors.green + "新增成功!!" + colors.reset)

# 刪除影片
def delete(word, playlistID):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    yes = 0 # 判斷播放清單是否有該影片
    one = 0 # 判斷是否只有一個影片符合關鍵字
    for i in range(len(response["items"])):
        if word in response["items"][i]["snippet"]["title"]:
            video = response["items"][i]["snippet"]["title"]
            ID = response["items"][i]["id"]
            yes = 1
            one += 1

    if yes == 0: # 播放清單沒有該影片
        w = input(colors.cyan + "查無相關影片，請重新輸入關鍵字 : " + colors.reset)
        delete(w, playlistID)
    if one > 1: # 不止一個影片符合關鍵字
        w = input(colors.cyan + "多個影片符合關鍵字，請重新輸入關鍵字 : " + colors.reset)
        delete(w, playlistID)
    elif one == 1: # 只有一個影片符合關鍵字
        d = youtube.playlistItems().delete(
            id = ID
        )
        d.execute()
        print(video + colors.green + " 刪除成功!!" + colors.reset)

# 查詢影片
def find(word, playlistID):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    yes = 0 # 判斷播放清單是否有該影片
    for i in range(len(response["items"])):
        if re.search(word, response["items"][i]["snippet"]["title"]): # regular expression
            yes = 1
            print(response["items"][i]["snippet"]["title"])
    if yes == 0: # 播放清單沒有該影片
        print("查無相關影片")

# 更改影片順序
def change(word, playlistID):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    yes = 0 # 判斷播放清單是否有該影片
    one = 0 # 判斷是否只有一個影片符合關鍵字
    for i in range(len(response["items"])):
        if word in response["items"][i]["snippet"]["title"]:
            video = response["items"][i]["snippet"]["title"]
            ID = response["items"][i]["id"]
            videoID = response["items"][i]["snippet"]["resourceId"]["videoId"]
            yes = 1
            one += 1

    if yes == 0: # 播放清單沒有該影片
        w = input(colors.cyan + "查無相關影片，請重新輸入關鍵字 : " + colors.reset)
        change(w, playlistID)
    if one > 1: # 不止一個影片符合關鍵字
        w = input(colors.cyan + "多個影片符合關鍵字，請重新輸入關鍵字 : " + colors.reset)
        change(w, playlistID)
    elif one == 1: # 只有一個影片符合關鍵字
        # 移到第幾個
        while True:
            order = input(video + colors.cyan + " 欲移至第幾個(1 ~ " + str(len(response["items"])) + ") : " + colors.reset)
            try:
                order = int(order)
                if 1 <= order <= len(response["items"]):
                    break
                else:
                    print(colors.red + "不要亂輸入= =" + colors.reset)
            except ValueError:
                print(colors.red + "不要亂輸入= =" + colors.reset)

        c = youtube.playlistItems().update(
            part="snippet",
            body={
            "id": ID,
            "snippet": {
                "playlistId": playlistID,
                "position": order - 1,
                "resourceId": {
                    "kind": "youtube# video",
                    "videoId": videoID
                }
            }
            }
        )
        c.execute()
        print(colors.green + "更改成功!!" + colors.reset)

# 新增播放清單
def newplaylist(name):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": name,
            "description": "",
            "tags": [
              "sample playlist",
              "API call"
            ],
            "defaultLanguage": "en"
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    request.execute()
    print(colors.green + "新增成功!!" + colors.reset)

# 更新標題
def updatetitle(playlistID, name):
    request = youtube.playlists().list(
        part = "snippet",
        id = playlistID
    )
    response = request.execute()

    ut = youtube.playlists().update(
        part = "snippet,status",
        body = {
          "id": playlistID,
          "snippet": {
            "title": name,
            "description": response["items"][0]["snippet"]["description"],
            "tags": [
              "updated playlist",
              "API FTW"
            ]
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    ut.execute()
    print(colors.green + "標題更新成功!!" + colors.reset)

# 更新說明
def updatedescription(playlistID, des):
    request = youtube.playlists().list(
        part = "snippet",
        id = playlistID
    )
    response = request.execute()

    ud = youtube.playlists().update(
        part = "snippet,status",
        body = {
          "id": playlistID,
          "snippet": {
            "title": response["items"][0]["snippet"]["title"],
            "description": des,
            "tags": [
              "updated playlist",
              "API FTW"
            ]
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    ud.execute()
    print(colors.green + "說明更新成功!!" + colors.reset)

# 更新隱私狀態
def updateprivacy(playlistID, status):
    request = youtube.playlists().list(
        part = "snippet",
        id = playlistID
    )
    response = request.execute()

    up = youtube.playlists().update(
        part = "snippet,status",
        body = {
          "id": playlistID,
          "snippet": {
            "title": response["items"][0]["snippet"]["title"],
            "description": response["items"][0]["snippet"]["description"],
            "tags": [
              "updated playlist",
              "API FTW"
            ]
          },
          "status": {
            "privacyStatus": status
          }
        }
    )
    up.execute()
    print(colors.green + "隱私狀態更新成功!!" + colors.reset)

# 刪除播放清單
def deleteplaylist(playlistID):
    request = youtube.playlists().delete(
        id = playlistID
    )
    request.execute()
    print(colors.green + "刪除成功!!" + colors.reset)

# 搬移影片
def move(playlistID, word):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    yes = 0 # 判斷播放清單是否有該影片
    one = 0 # 判斷是否只有一個影片符合關鍵字
    for i in range(len(response["items"])):
        if word in response["items"][i]["snippet"]["title"]:
            video = response["items"][i]["snippet"]["title"]
            ID = response["items"][i]["id"]
            videoID = response["items"][i]["snippet"]["resourceId"]["videoId"]
            yes = 1
            one += 1

    if yes == 0: # 播放清單沒有該影片
        w = input(colors.cyan + "查無相關影片，請重新輸入關鍵字 : " + colors.reset)
        move(playlistID, w)
    if one > 1: # 不止一個影片符合關鍵字
        w = input(colors.cyan + "多個影片符合關鍵字，請重新輸入關鍵字 : " + colors.reset)
        move(playlistID, w)
    elif one == 1: # 只有一個影片符合關鍵字
        moveto = input(colors.cyan + "輸入欲移至之播放清單ID : " + colors.reset)
        # 影片加到新的播放清單
        ad = youtube.playlistItems().insert(
            part = "snippet",
            body = {
            "snippet" : {
                "playlistId" : moveto,
                "position" : 0,
                "resourceId" : {
                "kind" : "youtube# video",
                "videoId" : videoID
                }
              }
            }
        )
        ad.execute()
        # 把原本播放清單的影片刪掉
        d = youtube.playlistItems().delete(
            id = ID
        )
        d.execute()
        print(video + colors.green + " 搬移成功!!" + colors.reset)

# 複製影片
def copy(playlistID, word):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlistID,
        maxResults = 50
    )
    response = request.execute()

    yes = 0 # 判斷播放清單是否有該影片
    one = 0 # 判斷是否只有一個影片符合關鍵字
    for i in range(len(response["items"])):
        if word in response["items"][i]["snippet"]["title"]:
            video = response["items"][i]["snippet"]["title"]
            ID = response["items"][i]["id"]
            videoID = response["items"][i]["snippet"]["resourceId"]["videoId"]
            yes = 1
            one += 1

    if yes == 0: # 播放清單沒有該影片
        w = input(colors.cyan + "查無相關影片，請重新輸入關鍵字 : " + colors.reset)
        copy(playlistID, w)
    if one > 1: # 不止一個影片符合關鍵字
        w = input(colors.cyan + "多個影片符合關鍵字，請重新輸入關鍵字 : " + colors.reset)
        copy(playlistID, w)
    elif one == 1: # 只有一個影片符合關鍵字
        copyto = input(colors.cyan + "輸入欲複製至之播放清單ID : " + colors.reset)
        co = youtube.playlistItems().insert(
            part = "snippet",
            body = {
            "snippet" : {
                "playlistId" : copyto,
                "position" : 0,
                "resourceId" : {
                "kind" : "youtube# video",
                "videoId" : videoID
                }
              }
            }
        )
        co.execute()
        print(video + colors.green + " 複製成功!!" + colors.reset)

while True:
    # 指令
    while True:
        op = input(colors.magenta + "請選擇(1)列出所有影片(2)新增影片(3)刪除影片(4)查詢影片(5)更改影片順序(6)新增播放清單(7)更新播放清單(8)刪除播放清單(9)搬移影片(10)複製影片 : " + colors.reset)

        # 列出所有影片
        if op == '1' or op == "(1)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            show(playlistID)
            break

        # 新增影片
        elif op == '2' or op == "(2)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            url = input(colors.cyan + "輸入欲新增影片之網址 : " + colors.reset).split("v=")
            url = url[-1]
            insert(url, playlistID)
            break

        # 刪除影片
        elif op == '3' or op == "(3)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            word = input(colors.cyan + "輸入欲刪除之影片關鍵字 : " + colors.reset)
            delete(word, playlistID)
            break

        # 查詢影片
        elif op == '4' or op == "(4)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            word = input(colors.cyan + "輸入關鍵字查詢播放清單是否有該影片 : " + colors.reset)
            find(word, playlistID)
            break

        # 更改影片順序
        elif op == '5' or op == "(5)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            word = input(colors.cyan + "輸入欲更改順序之影片關鍵字 : " + colors.reset)
            change(word, playlistID)
            break

        # 新增播放清單
        elif op == '6' or op == "(6)":
            name = input(colors.cyan + "輸入欲新增之播放清單標題 : " + colors.reset)
            newplaylist(name)
            break

        # 更新播放清單
        elif op == '7' or op == "(7)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            # 更新內容
            while True:
                playlistop = input(colors.cyan + "更新(1)標題(2)說明(3)隱私狀態 : " + colors.reset)
                # 標題
                if playlistop == '1' or playlistop == "(1)":
                    name = input(colors.cyan + "輸入欲更新之播放清單標題 : " + colors.reset)
                    updatetitle(playlistID, name)
                    break
                # 說明
                elif playlistop == '2' or playlistop == "(2)":
                    des = input(colors.cyan + "輸入欲更新之播放清單說明 : " + colors.reset)
                    updatedescription(playlistID, des)
                    break
                # 隱私狀態
                elif playlistop == '3' or playlistop == "(3)":
                    while True:
                        status = input(colors.cyan + "(1)公開(2)不公開(3)私人 : " + colors.reset)
                        # 公開
                        if status == '1' or status == "(1)":
                            status = "public"
                            break
                        # 不公開
                        elif status == '2' or status == "(2)":
                            status = "unlisted"
                            break
                        # 私人
                        elif status == '3' or status == "(3)":
                            status = "private"
                            break
                        else:
                            print(colors.red + "不要亂輸入= =" + colors.reset)
                    updateprivacy(playlistID, status)
                    break
                else:
                    print(colors.red + "不要亂輸入= =" + colors.reset)
            break

        # 刪除播放清單
        elif op == '8' or op == "(8)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            deleteplaylist(playlistID)
            break

        # 搬移影片
        elif op == '9' or op == "(9)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            word = input(colors.cyan + "輸入欲搬移之影片關鍵字 : " + colors.reset)
            move(playlistID, word)
            break

        # 複製影片
        elif op == '10' or op == "(10)":
            playlistID = input(colors.yellow + "輸入欲進行之播放清單ID : " + colors.reset)
            word = input(colors.cyan + "輸入欲複製之影片關鍵字 : " + colors.reset)
            copy(playlistID, word)
            break

        else:
            print(colors.red + "不要亂輸入= =" + colors.reset)

    # 是否結束執行
    while True:
        ans = input(colors.magenta + "還要繼續操作嗎(Y/N) : " + colors.reset)
        if ans == 'Y' or ans == 'y':
            break
        elif ans == 'N' or ans == 'n':
            break
        else:
            print(colors.red + "不要亂輸入= =" + colors.reset)
    if ans == 'N' or ans == 'n': # 結束
        break
    else:
        print("----------")