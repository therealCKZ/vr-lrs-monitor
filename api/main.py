from flask import Flask, jsonify, request
from datetime import datetime, time
from dotenv import load_dotenv
import requests
import base64
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# LRS configuration
LRS_URL = "https://nccu-rb521.nccu.edu.tw/data/xAPI/statements"
LRS_KEY = os.getenv("LRS_KEY")
LRS_SECRET = os.getenv("LRS_SECRET")

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        # Read timestamp from Grafana
        from_ts = request.args.get('from')
        if from_ts:
            # Transform Grafana timestamp to ISO format
            dt_object = datetime.fromtimestamp(int(from_ts)/1000.0)
            start_time = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            # Default fallback start time
            start_time = "2026-01-27T00:00:00Z"

        # Basic Authentication setup
        auth_str = f"{LRS_KEY}:{LRS_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}", 
            "X-Experience-API-Version": "1.0.3"
        }

        # Query parameters for LRS
        params = {"since": start_time, "limit": 1000}
        
        # Request data from LRS
        response = requests.get(LRS_URL, headers=headers, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        statements = data.get("statements", [])

        # Logic for counting unique participants
        unique_actors = set()
        for s in statements:
            # Standardize xAPI statement structure
            st = s.get("statement", s) 
            actor = st.get("actor", {})
            
            # Extract identifier from account name, name, or mbox
            account = actor.get("account") or {}
            actor_id = account.get("name") or actor.get("name") or actor.get("mbox")

            if actor_id:
                unique_actors.add(actor_id)

        # Define result outside the loop to prevent errors if statements list is empty
        participant_count = len(unique_actors)

        return jsonify({
            "status": "success", 
            "record_count": len(statements),
            "participant_count": participant_count,  
            "start_time_used": start_time, 
            "source": "LRS"
        })
    
    except Exception as e:
        # Log error details for debugging in docker logs
        print(f"Error Detail: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)