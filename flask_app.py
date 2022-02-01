
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, send_from_directory, request, redirect,url_for, session
import json
import datetime
import os
import random
import pyrebase
import requests
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
import database

#Self Py Files
from posts import addPost, getPosts
from config import firebaseConfig


simpleusers = []
avatar = "https://th.bing.com/th/id/R.4939499b222bf9af08fc13a6adaf2fa9?rik=cOyKtHAzH0tTwQ&pid=ImgRaw&r=0"
app = Flask(__name__)
upload = os.path.join(app.root_path, 'static')+"/uploads/"
app.config['UPLOAD_FOLDER'] = upload
app.config.from_pyfile('config.py')

simpleusers = []
images = ["https://tse2.mm.bing.net/th/id/OIP.KE5YalNkS7qnSNWOR7vISQHaEK?pid=ImgDet&w=1920&h=1080&rs=1","https://i1.wp.com/twinfinite.net/wp-content/uploads/2020/10/Destiny-2.jpg?fit=1280%2C720&ssl=1","https://d.ibtimes.co.uk/en/full/1625794/destiny-2-arcstrider-super-ability.png"]
home = ["Hello","Gutentag","Bout Ye","Konichiwa","Bonjour","¿Qué tal?","Nǐ hǎo","Hallo","Hei"]
#makeshift home button
homebtn = "<a href='/'>Go Home</a>"

#Firebase initialisation
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
store = firebase.storage()

@app.route('/')
def hello_world():
    data = home[random.randint(0,len(home)-1)]
    return render_template('home.html', hello = data)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/news')
def news():
    return "News is still in development " + homebtn

#TEST API FOR FLUTTER
@app.route('/api/',methods=['GET'])
def api():
    data = getPosts()['Posts']
    return json.dumps(data[::-1])

#Initial Post Request - will scale out to feed database after flutter integration
@app.route('/api/createpost',methods=['GET','POST'])
def postAPI():
    if request.method == 'POST':
        print(request.data)
        uname = request.form['name']
        uheader = request.form['header']
        uimage = request.form['image']
        if uimage == "":
            uimage = images[1]
        img= request.files['myimage']
        if img != "":
            img= request.files['myimage']
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
            store.child("images/"+img.filename).put(os.path.join(app.config['UPLOAD_FOLDER'], img.filename),session['uid'])
            url = store.child("images/"+img.filename).get_url(session['uid'])
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
        else:
            url =images[1]
        addPost(str(session['name']),uheader,url)
        database.addPost(str(session['name']),avatar,url,uheader)
        resp = {"response":200}
        return redirect(url_for('feed'))
        if 'Dart' in request.headers.get('User-Agent'):
            print(dict(request.files))
    else:
        return render_template("post.html")

@app.route('/feed')
def feed():
    data = getPosts()['Posts']
    return render_template('feed.html', data = data[::-1])

@app.route('/user/<user>')
def profile(user):
    avatar = database.getProfileImages(user, 'avatar')
    print(avatar)
    if 'Dart' in request.headers.get('User-Agent'):
        return str(avatar[0])
    elif session['name'] == user:
        user = session['name']

        return render_template("profile.html", user = user, avatar = avatar[0])

    else:
        return "User Profile"


@app.route('/premium')
def premCheck():
    if session['name']:
        return "Premium coming soon! Perks to be added!"
    else:
        return redirect(url_for("postsignIn"))

@app.route('/roadmap')
def roadmap():
    return render_template("roadmap.html")

@app.route('/featurerequest')
def features():
    if session['name']:
        return "Feature request will soon be live!"
    else:
        return redirect(url_for("postsignIn"))


@app.route('/createuser', methods=['POST'])
def postsignUp():
    email = request.form['email']
    passs = request.form['pass']
    name = request.form['name']
    # creating a user with the given email and password
    try:
        # creating a user with the given email and password
        user=auth.create_user_with_email_and_password(email,passs)
        print(user)
        uid = user['idToken']
        session['uid']=str(uid)
        print(session['uid'])
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']['message']
        if error == "EMAIL_EXISTS":
            print("Email already exists")
    database.addUser(name,email,avatar)
    database.addProfileImages(name,"avatar","https://e7.pngegg.com/pngimages/505/761/png-clipart-login-computer-icons-avatar-icon-monochrome-black-thumbnail.png")
    session['name'] = name
    print(simpleusers)
    return redirect(url_for('hello_world'))

@app.route('/signin',methods=['GET','POST'])
def postsignIn():
    if request.method == "POST":
        email=request.form['email']
        pasw=request.form['pass']
        try:
            # if there is no error then signin the user with given email and password
            user=auth.sign_in_with_email_and_password(email,pasw)
        except:
            message="Invalid Credentials!!Please ChecK your Data"
            return message
        session_id=user['idToken']
        session['uid']=str(session_id)
        print(session['uid'])
        session['name'] = database.getUserName(email)[0]
        print(session['name'])
        if 'Dart' in request.headers.get('User-Agent'):
            return "logged in"
        else:
            return redirect(url_for('feed'), )
    else:
        return render_template("signin.html")

@app.route('/signout',methods=['GET','POST'])
def signout():
    session.clear()
    return redirect(url_for('hello_world'))

@app.route('/addimage',methods=['GET','POST'])
def firepost():
    if request.method == "POST":
        print(request.data)
        img= request.files['myimage']
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
        print(img)

        store.child("images/"+img.filename).put(os.path.join(app.config['UPLOAD_FOLDER'], img.filename),'eyJhbGciOiJSUzI1NiIsImtpZCI6IjQwMTU0NmJkMWRhMzA0ZDc2NGNmZWUzYTJhZTVjZDBlNGY2ZjgyN2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWluZGxldmVsbGVkZmlyZSIsImF1ZCI6Im1pbmRsZXZlbGxlZGZpcmUiLCJhdXRoX3RpbWUiOjE2NDI0MjUzOTksInVzZXJfaWQiOiJidWZJbVMzdlJ2V0swaVdaUHpCNVpPR0R5ZDYyIiwic3ViIjoiYnVmSW1TM3ZSdldLMGlXWlB6QjVaT0dEeWQ2MiIsImlhdCI6MTY0MjQyNTM5OSwiZXhwIjoxNjQyNDI4OTk5LCJlbWFpbCI6ImNocmlzdG9waGVyLmdpbGxlc3BpZUBoc2NuaS5uZXQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiY2hyaXN0b3BoZXIuZ2lsbGVzcGllQGhzY25pLm5ldCJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.Z8bBs9zFS9NHffbYUABLcilyAWBQy_s5JgdWha3NYpGS1jDRHG-aZe9-O07N12mCXvzS71XVOAaEm0vZbQXG67PX3eZCiJNekmttT0Wae46KGM4XDCMm8uGyNY3EJ7E6GNYYKErdYijblkdShOQCAUwEjl44RlUoOpiaa3BvOVd7b8myTAsPrEddV2FCW-cNbK6NrWZMgZi5NeIJTLKmG-fMhEJkKFJeJlkgUSrsEu7WAwyYg4UkybP-3zyZx5MAptSzNZGuRu95jJmjTDDCR92-ehk5bCLBzlCDOKPxcXpCQbu7jqjtH65lDCCHDlq03Go7rRWwv2OTW-0')
        url = store.child("images/"+img.filename).get_url('eyJhbGciOiJSUzI1NiIsImtpZCI6IjQwMTU0NmJkMWRhMzA0ZDc2NGNmZWUzYTJhZTVjZDBlNGY2ZjgyN2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWluZGxldmVsbGVkZmlyZSIsImF1ZCI6Im1pbmRsZXZlbGxlZGZpcmUiLCJhdXRoX3RpbWUiOjE2NDI0MjUzOTksInVzZXJfaWQiOiJidWZJbVMzdlJ2V0swaVdaUHpCNVpPR0R5ZDYyIiwic3ViIjoiYnVmSW1TM3ZSdldLMGlXWlB6QjVaT0dEeWQ2MiIsImlhdCI6MTY0MjQyNTM5OSwiZXhwIjoxNjQyNDI4OTk5LCJlbWFpbCI6ImNocmlzdG9waGVyLmdpbGxlc3BpZUBoc2NuaS5uZXQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiY2hyaXN0b3BoZXIuZ2lsbGVzcGllQGhzY25pLm5ldCJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.Z8bBs9zFS9NHffbYUABLcilyAWBQy_s5JgdWha3NYpGS1jDRHG-aZe9-O07N12mCXvzS71XVOAaEm0vZbQXG67PX3eZCiJNekmttT0Wae46KGM4XDCMm8uGyNY3EJ7E6GNYYKErdYijblkdShOQCAUwEjl44RlUoOpiaa3BvOVd7b8myTAsPrEddV2FCW-cNbK6NrWZMgZi5NeIJTLKmG-fMhEJkKFJeJlkgUSrsEu7WAwyYg4UkybP-3zyZx5MAptSzNZGuRu95jJmjTDDCR92-ehk5bCLBzlCDOKPxcXpCQbu7jqjtH65lDCCHDlq03Go7rRWwv2OTW-0')
        return f"<body><img src={url}></body>"
    else:
        return '<html><body><form method="POST" enctype="multipart/form-data"> <input type="file" name="myimage"><input type="submit" name="submit_image" value="Upload"></form></body></html>'

@app.route('/blog')
def blog():
    return "Blog is still in development " + homebtn

@app.route('/app/createpost',methods=['POST'])
def testfunc():
    data = dict(request.form)
    files = dict(request.files)
    uheader = data['header']
    email = data['email']
    pwrd = data['pass']
    session['name'] = database.getUserName(email)[0]
    uid = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjQwMTU0NmJkMWRhMzA0ZDc2NGNmZWUzYTJhZTVjZDBlNGY2ZjgyN2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWluZGxldmVsbGVkZmlyZSIsImF1ZCI6Im1pbmRsZXZlbGxlZGZpcmUiLCJhdXRoX3RpbWUiOjE2NDI0MjUzOTksInVzZXJfaWQiOiJidWZJbVMzdlJ2V0swaVdaUHpCNVpPR0R5ZDYyIiwic3ViIjoiYnVmSW1TM3ZSdldLMGlXWlB6QjVaT0dEeWQ2MiIsImlhdCI6MTY0MjQyNTM5OSwiZXhwIjoxNjQyNDI4OTk5LCJlbWFpbCI6ImNocmlzdG9waGVyLmdpbGxlc3BpZUBoc2NuaS5uZXQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiY2hyaXN0b3BoZXIuZ2lsbGVzcGllQGhzY25pLm5ldCJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.Z8bBs9zFS9NHffbYUABLcilyAWBQy_s5JgdWha3NYpGS1jDRHG-aZe9-O07N12mCXvzS71XVOAaEm0vZbQXG67PX3eZCiJNekmttT0Wae46KGM4XDCMm8uGyNY3EJ7E6GNYYKErdYijblkdShOQCAUwEjl44RlUoOpiaa3BvOVd7b8myTAsPrEddV2FCW-cNbK6NrWZMgZi5NeIJTLKmG-fMhEJkKFJeJlkgUSrsEu7WAwyYg4UkybP-3zyZx5MAptSzNZGuRu95jJmjTDDCR92-ehk5bCLBzlCDOKPxcXpCQbu7jqjtH65lDCCHDlq03Go7rRWwv2OTW-0'
    img = files['file']
    print(uheader)
    print(img)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    store.child("images/"+img.filename).put(os.path.join(app.config['UPLOAD_FOLDER'], img.filename),uid)
    url = store.child("images/"+img.filename).get_url(uid)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    addPost(str(session['name']),uheader,url)
    database.addPost(str(session['name']),avatar,url,uheader)
    return {"response":200}

@app.route('/app/changeimage',methods=['POST'])
def testfunc2():
    data = dict(request.form)
    files = dict(request.files)
    uheader = data['imgtype']
    email = data['email']
    session['name'] = database.getUserName(email)[0]
    uid = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjQwMTU0NmJkMWRhMzA0ZDc2NGNmZWUzYTJhZTVjZDBlNGY2ZjgyN2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWluZGxldmVsbGVkZmlyZSIsImF1ZCI6Im1pbmRsZXZlbGxlZGZpcmUiLCJhdXRoX3RpbWUiOjE2NDI0MjUzOTksInVzZXJfaWQiOiJidWZJbVMzdlJ2V0swaVdaUHpCNVpPR0R5ZDYyIiwic3ViIjoiYnVmSW1TM3ZSdldLMGlXWlB6QjVaT0dEeWQ2MiIsImlhdCI6MTY0MjQyNTM5OSwiZXhwIjoxNjQyNDI4OTk5LCJlbWFpbCI6ImNocmlzdG9waGVyLmdpbGxlc3BpZUBoc2NuaS5uZXQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiY2hyaXN0b3BoZXIuZ2lsbGVzcGllQGhzY25pLm5ldCJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.Z8bBs9zFS9NHffbYUABLcilyAWBQy_s5JgdWha3NYpGS1jDRHG-aZe9-O07N12mCXvzS71XVOAaEm0vZbQXG67PX3eZCiJNekmttT0Wae46KGM4XDCMm8uGyNY3EJ7E6GNYYKErdYijblkdShOQCAUwEjl44RlUoOpiaa3BvOVd7b8myTAsPrEddV2FCW-cNbK6NrWZMgZi5NeIJTLKmG-fMhEJkKFJeJlkgUSrsEu7WAwyYg4UkybP-3zyZx5MAptSzNZGuRu95jJmjTDDCR92-ehk5bCLBzlCDOKPxcXpCQbu7jqjtH65lDCCHDlq03Go7rRWwv2OTW-0'
    img = files['file']
    print(uheader)
    print(img)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    store.child("images/"+img.filename).put(os.path.join(app.config['UPLOAD_FOLDER'], img.filename),uid)
    url = store.child("images/"+img.filename).get_url(uid)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    print(url)
    #addPost(str(session['name']),uheader,url)
    database.updateProfileImage(session['name'],'avatar',url)
    return url

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/app')
def app_url():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'app-release.apk')



