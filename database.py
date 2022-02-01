import sqlite3
from datetime import datetime

now = datetime.now()
now = now.strftime("%d/%m/%Y %H:%M:%S")






def addPost(author, avatar, image, body):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       createdAt           TEXT    NOT NULL,
       author            TEXT     NOT NULL,
       avatar   TEXT NOT NULL,
       image        TEXT,
       body         TEXT,
       likes INT,
       report INT,
       coments TEXT,
       premium INT,
       adminPost TEXT,
       editorpicks TEXT
       );''')
    sql = '''INSERT INTO posts(
   createdAt, author, avatar, body) VALUES
   (?, ?, ?, ?)'''
    values = (now,author, avatar, body)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()


def addUser(user, email, avatar):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       createdAt           TEXT    NOT NULL,
       user            TEXT     NOT NULL UNIQUE,
       email    TEXT NOT NULL UNIQUE,
       avatar   TEXT NOT NULL,
       friends        TEXT,
       reported INT,
       lastSeen TEXT,
       lastPost TEXT,
       premium INT,
       adminPost TEXT,
       editorpicks TEXT
       );''')
    sql = '''INSERT INTO users(
   createdAt, user, email, avatar) VALUES
   (?, ?, ?, ?)'''
    values = (now,user, email, avatar)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()

def getUserName(email):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user FROM users WHERE email = ?", (email,))
    res = cursor.fetchone()
    return res


def addProfileImages(user, imgtype, image):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profileimages
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       createdAt           TEXT    NOT NULL,
       user            TEXT     NOT NULL,
       imgtype   TEXT NOT NULL,
       image        TEXT
       );''')
    sql = '''INSERT INTO profileimages(
   createdAt, user, imgtype, image) VALUES
   (?, ?, ?, ?)'''
    values = (now,user, imgtype, image)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()

def updateProfileImage(user, imgtype, image):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profileimages
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       createdAt           TEXT    NOT NULL,
       user            TEXT     NOT NULL,
       imgtype   TEXT NOT NULL,
       image        TEXT
       );''')
    sql = ''' UPDATE profileimages
              SET createdAt = ? ,
                  image = ?
              WHERE user = ? and imgtype = ?'''
    values = (now,image, user, imgtype)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()

def getProfileImages(user, imgtype):
    conn = sqlite3.connect('mindlevelled.db')
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM profileimages WHERE user = ?and imgtype = ?", (user,imgtype,))
    res = cursor.fetchone()
    return res

