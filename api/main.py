from flask import Flask, jsonify
from datetime import datetime, time
import requests
import base64
import os

app = Flask(__name__)

# LRS setup
LRS_URL = "https://nccu-rb521.nccu.edu.tw/data/xAPI/statements"
LRS_KEY = "f38d35951635983bf9a371e70bbe776a3e539e2b"
LRS_SECRET = "fdeb801552ccfda89d4cd485cee881feb968bb16"

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        #get data from chosen time
        start_time = "2026-01-25T00:00:00+08:00"

        # create Basic Auth
        auth_str = f"{LRS_KEY}:{LRS_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "X-Experience-API-Version": "1.0.3"
        }

        # add a 'since' filter
        # set limit to 1000 (can adjust according to activity)
        params = {
            "since": start_time, 
            "limit": 1000
        }

        # ask data from LRS
        response = requests.get(LRS_URL, headers=headers, params=params, verify=False)
        response.raise_for_status()
        data = response.json()

        # today_count means today's statement count
        today_count = len(data.get("statements", []))

        return jsonify({
            "status": "success", 
            "record_count": today_count, 
            "source": "LRS"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)