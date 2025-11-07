from flask import Flask, jsonify, request
from SoC_Scraper import SoC_Scraper

app = Flask(__name__)

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
            return open(f"server/Section_Data/{filePath}", "r").read()
        except:
            return jsonify("OOPSIE")
    
    return None

if __name__ == '__main__':
    app.run(debug=True, port=8023)
