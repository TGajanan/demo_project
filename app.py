from flask import Flask , render_template, request, session
from pymongo import MongoClient
import requests
from bson.objectid import ObjectId
from bson import ObjectId
import secrets
from flask_pymongo import PyMongo
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Connection with mongodb atlas
# client = MongoClient('mongodb://localhost:27017')
client = MongoClient('mongodb+srv://gaja:gaja123@cluster0.jdoybcv.mongodb.net/blueimpulsedemo')
db = client.blueimpulsedemo

app=Flask(__name__)
app.secret_key = secrets.token_hex(16) 
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'userimage')

@app.route('/', methods=['GET', 'POST'])
def homepage():
    logged_in=False
    if 'user_id' in session:
        logged_in=True
        return render_template("index.html",logged_in=logged_in)
    return render_template("index.html",logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = db.userdetails.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            msg = "User validated"
            session['email'] = email
            session['user_id'] = str(user['_id']) 
            logged_in = True 
            return render_template("index.html", msg=msg, success=1, logged_in=logged_in)
        else:
            msg = "Invalid credentials"
            return render_template("login.html", msg=msg, success=0)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    collection = db['userdetails']
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  #Hash the password
        user = collection.find_one({'email': email})
        if user:
            msg = "This email already exists!"
            return render_template("register.html", msg=msg, success=0)
        else:
            data = {
                'username': username,
                'email': email,
                'password': hashed_password,  #Store the hashed password
                'profileImage': " ",
                'fname': " ", 'lname': " ",
                'mobile_number': " ", 'oname': " ", 'location': " "
            }
            db.userdetails.insert_one(data)
            msg = "Successfully registered!"
            return render_template('login.html', success=1, msg=msg)
    return render_template('register.html')

@app.route('/myaccount', methods=['GET', 'POST'])
def myaccount():
    user_id = session.get('user_id')
    user = db.userdetails.find_one({'_id': ObjectId(user_id)})
    print("user details from session", user)
    if request.method == "POST":
        file = request.files['profileImage']
        fname = request.form['fname']
        lname = request.form['lname']
        oname = request.form['oname']
        email = session.get('email')
        mobile_number = request.form['mobile_number']
        location = request.form['location']
        filename = file.filename
        print("userdetails not updated")
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.userdetails.update_one(
                {'email': email},
                {'$set': {'profileImage': filename, 'fname': fname, 'lname': lname,
                          'mobile_number': mobile_number, 'oname': oname, 'location': location}})
            print("serdetails updated")
            user = db.userdetails.find_one({'email': email})
            return render_template('myaccount.html', user=user)
    return render_template('myaccount.html', user=user)


#logout function
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('user_id', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
