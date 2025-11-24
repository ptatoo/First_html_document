from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os
import json
import csv
import waitress
from dotenv import load_dotenv
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import shutil

app = Flask(__name__)
CORS(app)

# Initialize JWTManager
app.config['JWT_SECRET_KEY'] = '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'  # Replace with your own secret key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
jwt = JWTManager(app)

load_dotenv()  # Load the environment variables from the .env file

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']

@app.route('/google_login', methods=['POST'])
def login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,  # client ID from the credential at google developer console
        'client_secret': GOOGLE_SECRET_KEY,  # client secret from the credential at google developer console
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    """
        check here if user exists in database, if not, add him
    """

    jwt_token = create_access_token(identity=user_info['email'])  # create jwt token
    response = jsonify(user=user_info)
    response.set_cookie('access_token_cookie', value=jwt_token, secure=True)

    return response, 200


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie') # Demonstration how to get the cookie
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

#default interface
@app.route("/")
def hello_world():
    return "Hello, World!"

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
            

#main function
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update, 'interval', minutes=20)
    scheduler.start()

    port = int(os.environ.get("PORT", 4000))
    waitress.serve(app,host="0.0.0.0", port=port)
