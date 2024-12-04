from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import makeGrid
app = Flask(__name__)
CORS(app)

def init():
    makeGrid.loadData()

def makeDaily():
    print("**Create Daily Puzzle Here**")

scheduler = BackgroundScheduler()
scheduler.add_job(makeDaily, 'interval', days=1, start_date='2024-12-04 00:00:00', timezone='EST')
scheduler.start()
init()



@app.route('/get_strings')
def getStrings():
    #get daily puzzle
    grid = makeGrid.getRandomGrid()
    #replace this
    return jsonify({'grid': grid})

@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.get_json()  # Use get_json() to parse JSON data
    #print("data: "+str(data))
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    rowNum = data.get("row", 0)
    colNum = data.get("col", 0)

    user_answer = data.get("answer", "")
    row = data.get("rowObject")
    col = data.get("colObject")

    #print(f"User submitted: {user_answer}")
    #print(f"Categories: {str(row)} + {str(col)}")
    ans = makeGrid.checkSubmission(user_answer, row, col)
    #print(str("Success? "+str(ans)))

    return jsonify({"success": ans, "row": rowNum, "col": colNum})

#http://127.0.0.1:5000

if __name__ == '__main__':
    #makeGrid.loadData()
    app.run(debug=True)