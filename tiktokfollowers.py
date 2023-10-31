import json
import os
from datetime import datetime
import requests
import time

# There is literally no error checking anywhere here...
# I wrote this kinda quickly...
# API key is retrieved from environment variables.

countikstub = "https://countik.com/api/userinfo"



def getuserdata(userid,sec_uid):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }

    countikurl = countikstub + "?sec_user_id=" + sec_uid
    tries = range(10)

    userobject = {'followerCount': 0, 'followingCount': 0, 'heartCount': 0, 'status': 'error', 'videoCount': 0}

    for count in tries:
        time.sleep(1)
        print(f'Try {count} user {userid}...')
        response = requests.get(url=f'{countikurl}',
                             headers=headers)
        if response.status_code == 200:
            userobject = json.loads(response.text)
            if userobject["status"] == "success":
                break
            else:
                userobject = {'followerCount': 0, 'followingCount': 0, 'heartCount': 0, 'status': 'error', 'videoCount': 0}
    thetimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return userobject

def loadusers():
    f = open('userlist.json')
    users = json.load(f)
    return users

def procuser(userobj):
    userobject = getuserdata(userobj["userid"], userobj["sec_uid"])
    useroutput = {}
    useroutput["name"] = userobj["name"]
    useroutput["followerCount"] = userobject["followerCount"]
    useroutput["heartCount"] = userobject["heartCount"]
    useroutput["userid"] = userobj["userid"]
    try:
        with open(f'user-{userobj["userid"]}.json', "r") as userfile:
            lastoutput = json.load(userfile)
            useroutput["newFollowerCount"] = int(userobject["followerCount"]) - (lastoutput["followerCount"])
            useroutput["newHeartCount"] = int(userobject["heartCount"]) - (lastoutput["heartCount"])
    except IOError:
        print(f'user-{userobj["userid"]}.json does not exist.')
    return useroutput

def getuserstats():
    users = loadusers()
    slackmsgdict = {}
    slackmsg = ":busts_in_silhouette: Hourly Follower Stats :busts_in_silhouette:\n"
    for user in users:
        print(user)
        result = procuser(user)
        name = result["name"]
        followers = result["followerCount"]
        #with open(f'user-{result["userid"]}.json', 'w') as f:
        #    json.dump(result, f)
        slackmsg += f'{result["name"]} {result["followerCount"]}'
        if "newFollowerCount" in result:
            if int(result["newFollowerCount"]) >= 0:
                slackmsg += '  +'
            else:
                slackmsg += '  '
            slackmsg += f'{result["newFollowerCount"]}'
        slackmsg += "\n"
    slackmsgdict["followers"] = slackmsg

    slackmsg = ":heart: Hourly Like Stats :heart:\n"
    for user in users:
        print(user)
        result = procuser(user)
        name = result["name"]
        followers = result["heartCount"]
        with open(f'user-{result["userid"]}.json', 'w') as f:
            json.dump(result, f)
        slackmsg += f'{result["name"]} {result["heartCount"]}'
        if "newHeartCount" in result:
            if int(result["newHeartCount"]) >= 0:
                slackmsg += '  +'
            else:
                slackmsg += '  '
            slackmsg += f'{result["newHeartCount"]}'
        slackmsg += "\n"
    slackmsgdict["likes"] = slackmsg
    return slackmsgdict

def main():
    slackmsgdict = getuserstats()
    slackmsg = slackmsgdict["followers"]
    slack_key = os.getenv("slack_key")
    slack_webhook_stub = "https://hooks.slack.com/services/"
    print(slackmsg)
    slack_webhook_url = slack_webhook_stub + slack_key
    result = requests.post(
        slack_webhook_url,
        data='{"text": "' + slackmsg + '"}')
    print(slackmsg)

    slackmsg = slackmsgdict["likes"]
    slack_key = os.getenv("slack_key")
    slack_webhook_stub = "https://hooks.slack.com/services/"
    slack_webhook_url = slack_webhook_stub + slack_key
    result = requests.post(
        slack_webhook_url,
        data='{"text": "' + slackmsg + '"}')
    print(slackmsg)

if __name__ == '__main__':
    main()
