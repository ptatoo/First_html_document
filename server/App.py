from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os
import json
import csv

app = Flask(__name__)
CORS(app)

@app.route('/update')
def run_task():
    output = SoC_Scraper()
    return {"message": output}

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
            file = open(f"section_data/{filePath}", "r").readlines()
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
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
