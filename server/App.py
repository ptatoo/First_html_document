from flask import Flask, jsonify, request
from flask_cors import CORS
from SoC_Scraper import SoC_Scraper
import os

app = Flask(__name__)
CORS(app)

@app.route('/update')
def run_task():
    output = SoC_Scraper()
    return {"message": output}

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/get", methods = ['GET'])
def get_data():
    if(request.method == 'GET'):
        filePath = request.args['filePath']
        try:
            return open(f"server/section_data/{filePath}", "r").read()
        except:
            return jsonify("Cannot find file. " + f"server/Section_Data/{filePath}")
    
    return ""


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))  # 👈 same idea as process.env.PORT || 4000
    app.run(host="0.0.0.0", port=port)
