from flask import Flask, request
from SoC_Scraper import SoC_Scraper

app = Flask(__name__)

@app.route('/run_task')
def run_task():
    output = SoC_Scraper()
    return {"message": output}

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
