from flask import Flask, jsonify, request
from SoC_Scraper import SoC_Scraper
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

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
            return open(f"server/section_data/{filePath}", "r").read()
        except:
            return jsonify("OOPSIE")
    
    return None

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
    app.run(debug=False, port=5000)


