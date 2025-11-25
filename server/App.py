from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os
import json
import csv
import waitress
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, set_access_cookies
import shutil

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'placeholder' 

app.config['JWT_COOKIE_CSRF_PROTECT'] = False # Enable in production

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# DISABLING Secure allows cookies over HTTP (localhost)
app.config['JWT_COOKIE_SECURE'] = False 

# Lax is required for localhost non-https
app.config['JWT_COOKIE_SAMESITE'] = 'Lax' 

jwt = JWTManager(app)

GOOGLE_CLIENT_ID = "454930251106-d7a2pe23cnivc8aehsehh4bkjbbvgna1.apps.googleusercontent.com"

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
        access_token = create_access_token(identity=user_email)

        # 3. Create response and set cookie
        response = jsonify({"msg": "Login Success", "user": user_email})
        set_access_cookies(response, access_token)

        return response,200

    except Exception as e:
        return "FUCKING HAACKER, YOU ARE FUCKING INVALID AUTHENTICATION", 401


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
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
    sec_path = "section_data"
    last_sec_path = "last_section_data"

    copy()
    result = SoC_Scraper("Subjects.txt", sec_path)
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
    sec_path = "section_data"
    last_sec_path = "last_section_data"

    subject_paths = set()
    for root, folders, files in os.walk(sec_path):
        for filename in files:
            file_path = os.path.join(root,filename)
            subject_paths.add(file_path)

    last_subject_paths = set()
    for root, folders, files in os.walk(sec_path):
        for filename in files:
            file_path = os.path.join(root,filename)
            last_subject_paths.add(file_path)

    common_files = subject_paths.intersection(last_subject_paths)
            

#default interface
@app.route("/")
def hello_world():
    return "Hello, World!"

#main function
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update, 'interval', minutes=20)
    scheduler.start()

    port = int(os.environ.get("PORT", 4000))
    waitress.serve(app,host="0.0.0.0", port=port)
