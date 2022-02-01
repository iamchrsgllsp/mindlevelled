import json
from datetime import datetime

def getPosts():
    with open("/home/mindlevelled/mysite/post.json") as posts:
        data = json.load(posts)
        return data


def addPost(name,header,image):
    data = getPosts()
    id = maxID()
    print(id)
    print(header)
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    newpost = {"id": id,"createdAt": now,"name": name,"avatar": image,"message":header}
    newposts = data['Posts']
    newposts.append(dict(newpost))
    print(newpost)
    with open("/home/mindlevelled/mysite/post.json","w") as posts:
        posts.write(json.dumps({"Posts":newposts}))

def maxID():
    data = getPosts()['Posts']
    ids = []
    for x in data:
        ids.append(int(x['id']))

    return str(int(max(ids))+1)