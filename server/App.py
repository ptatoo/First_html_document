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
            try:
                return open(f"section_data/{filePath}", "r").read()
            except:
                return jsonify("Cannot find file. " + f"server/Section_Data/{filePath}")
    
    return ""

scheduler = BackgroundScheduler()

# 2. Add the job to the scheduler
# This will run the 'scrape_data' function every 30 minutes.
# Use 'seconds', 'minutes', 'hours', 'days', or 'weeks'.
scheduler.add_job(func=run_task, trigger="interval", seconds = 30)

# 3. Start the scheduler
scheduler.start()

# 4. Shut down the scheduler when the app exits
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))  # 👈 same idea as process.env.PORT || 4000
    app.run(host="0.0.0.0", port=port)
