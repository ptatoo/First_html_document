from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os
import json
import csv
import waitress
from apscheduler.schedulers.background import BackgroundScheduler
import shutil

app = Flask(__name__)
CORS(app)

@app.route('/update')
def update():
    sec_path = "section_data"
    last_sec_path = "last_section_data"

    copy()
    result = SoC_Scraper("subjects.txt", sec_path)
    return "yay"

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


#main function
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update, 'interval', minutes=20)
    scheduler.start()

    port = int(os.environ.get("PORT", 4000))
    waitress.serve(app,host="0.0.0.0", port=port)
