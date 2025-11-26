from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os
import json
import csv
import waitress
import requests
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, set_access_cookies
import shutil
import sqlite3
from google.oauth2 import id_token
from google.auth.transport import requests

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

load_dotenv() 
#loading env vars
USER_DB_PATH = os.getenv("USER_DB_PATH")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
SEC_PATH = os.getenv("SECTION_DATA_PATH")
LAST_SEC_PATH = os.getenv("LAST_SECTION_DATA_PATH")

#configging jwt
app.config['JWT_SECRET_KEY'] = str(os.getenv("JWT_KEY"))

app.config['JWT_COOKIE_CSRF_PROTECT'] = False # Enable in production
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# DISABLING Secure allows cookies over HTTP (localhost)
app.config['JWT_COOKIE_SECURE'] = False 
# Lax is required for localhost non-https
app.config['JWT_COOKIE_SAMESITE'] = 'Lax' 

#initializing JWT Manager
jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def google_auth():
    data = request.get_json()
    auth_code = request.get_json()['credentials']

    try:
        id_info = id_token.verify_oauth2_token(
            auth_code,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        user_email = id_info['email']
        user_given_name = id_info['given_name']
        access_token = create_access_token(identity=user_email)

        # 3. Create response and set cookie
        response = jsonify({"msg": "Login Success", "user": user_email})
        set_access_cookies(response, access_token)

        # 4. log user into db
        db = sqlite3.connect(USER_DB_PATH, timeout=5.0)  
        cur = db.cursor()   
        
        try:
            cur.execute('INSERT INTO users (name, email) VALUES (?,?)', (user_given_name,user_email))
            print(f"user {user_email} created")
        except:
            print(f"user {user_email} already exists")
        db.commit()
        db.close() 
        return response,200

    except Exception as e:
        print("unauth")
        return "Invalid Authentication", 401

# Protect a route with jwt_required, which will kick out requests without a vaalid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie') # Demonstration how to get the cookie
    print(jwt_token)

    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/update')
def update():
    copy()
    result = SoC_Scraper("Subjects.txt", SEC_PATH)
    return result

def copy():
    sec_path = "section_data"
    last_sec_path = "last_section_data"

    for root, folders, files in os.walk(sec_path):
        for filename in files:
            file_path = os.path.join(root,filename)
            shutil.copy(file_path,f"{last_sec_path}/{filename}")

    return "nice Job!"

#get CSV data
@app.route("/get", methods = ['GET'])
def get_data():
    if(request.method == 'GET'):
        filePath = request.args['filePath']

        #tries to open file
        try:
            file = open(f"{filePath}", "r").readlines()
        except:
            return jsonify("Cannot find file. " +  f"FileName: {filePath}")
            
        #converts csv data into json data and returns
        csv_reader = csv.DictReader(file)
        output = []
        for row in csv_reader:
            output.append(row)
        return jsonify(output)
    
    return ""

@app.route("/displayChanges")
def displayChanges():

    subject_paths = set()
    for root, folders, files in os.walk(SEC_PATH):
        for filename in files:
            file_path = os.path.join(root,filename)
            subject_paths.add(file_path)

    last_subject_paths = set()
    for root, folders, files in os.walk(LAST_SEC_PATH):
        for filename in files:
            file_path = os.path.join(root,filename)
            last_subject_paths.add(file_path)

    common_files = subject_paths.intersection(last_subject_paths)
            

#default interface
@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/test")
def test():
    db = sqlite3.connect(USER_DB_PATH, timeout=5.0)  
    cur = db.cursor()

    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()

    db.commit()
    db.close()

    for row in rows:
        print(row)

    return jsonify("LOL"), 200


def setupSQLite():
    db = sqlite3.connect(USER_DB_PATH, timeout=5.0)  

    cur = db.cursor()

    create_table_query = """  
    CREATE TABLE IF NOT EXISTS users (  
        id INTEGER PRIMARY KEY AUTOINCREMENT,  
        name TEXT NOT NULL,  
        email TEXT UNIQUE NOT NULL
    );  
    """ 

    cur.execute(create_table_query)  

    db.close()
    

#main function
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update, 'interval', minutes=20)
    scheduler.start()

    setupSQLite()

    port = int(os.environ.get("PORT", 4000))
    waitress.serve(app,host="0.0.0.0", port=port)
