from flask import Flask, jsonify, request
from datetime import datetime
from dotenv import load_dotenv
import requests
import base64
import os
import re

app = Flask(__name__)

# Load environment variables
load_dotenv()

# LRS configuration
LRS_URL = os.getenv("LRS_URL")
LRS_KEY = os.getenv("LRS_KEY")
LRS_SECRET = os.getenv("LRS_SECRET")
CLASS_EXT = os.getenv("CLASS_EXT")
STUDENT_EXT = os.getenv("STUDENT_EXT")

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

TARGET_TASK_KEYS = [
    "q_earth_s02_ob01", "q_earth_s05_ob01", "q_earth_s05_ob02", 
    "q_earth_s06_ob01", "q_earth_s07_ob01", "q_earth_s08_ob01",
    "q_ms1_s2_ob1", "q_ms2_s1_ob1", "q_ms2_s3_ob1", "q_ms2_s7_ob01",
    "q_node2_s01_ob01", "q_node2_s01_ob02", "q_node2_s01_ob03", "q_node2_s01_ob04"
]

@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        # 接收 Grafana 傳來的班級參數
        target_class = request.args.get('class')
        print(f"DEBUG target_class: repr={repr(target_class)}")
        

        # 處理時間範圍
        from_ts = request.args.get('from')
        if from_ts:
            dt_object = datetime.fromtimestamp(int(from_ts)/1000.0)
            start_time = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            start_time = "2026-01-27T00:00:00Z"

        auth_str = f"{LRS_KEY}:{LRS_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}", 
            "X-Experience-API-Version": "1.0.3"
        }

        # 抓取 LRS 資料
        statements = []
        params = {"since": start_time, "limit": 1000}
        
        response = requests.get(LRS_URL, headers=headers, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        statements.extend(data.get("statements", []))

        next_url = data.get("more")
        while next_url:
            if not next_url.startswith("http"):
                from urllib.parse import urljoin
                next_url = urljoin(LRS_URL, next_url)
            
            next_res = requests.get(next_url, headers=headers, verify=False)
            next_res.raise_for_status()
            next_data = next_res.json()
            statements.extend(next_data.get("statements", []))
            next_url = next_data.get("more")

        # 統計變數
        unique_students = set()
        verb_counts = {}
        user_progress = {}
        correct_count = 0
        total_quiz_attempts = 0
        filtered_record_count = 0

        for s in statements:
            st = s.get("statement", s) 
            context = st.get("context", {})
            extensions = context.get("extensions", {})
            statement_class = str(extensions.get(CLASS_EXT, "")).strip()
            
            # --- 強化的班級過濾邏輯 ---
            # 取得目標班級並標準化
            raw_target = request.args.get('class', 'ALL')
            # 只要包含 "ALL" (不分大小寫) 或 參數為空，就不過濾
            is_all = not raw_target or str(raw_target).upper() == "ALL" or "ALL" in str(raw_target).upper()

            if not is_all:
                # 處理 Grafana 可能傳送的逗號分隔值 (例如 "110,111")
                allowed_classes = [c.strip() for c in str(raw_target).split(',')]
                if statement_class not in allowed_classes:
                    continue
            # ------------------------

            # 通過過濾，增加紀錄數
            filtered_record_count += 1

            # --- 學生識別 (優先使用 Student ID) ---
            student_id_ext = extensions.get(STUDENT_EXT)
            actor = st.get("actor", {})
            account = actor.get("account") or {}
            actor_fallback = account.get("name") or actor.get("name") or actor.get("mbox")
            
            final_id = student_id_ext if student_id_ext else actor_fallback

            if final_id:
                unique_students.add(final_id)
                if final_id not in user_progress:
                    user_progress[final_id] = set()

                # 動作與正確率邏輯
                verb_info = st.get("verb", {})
                verb_display = verb_info.get("display", {}).get("en-US", "Unknown")
                verb_id = verb_info.get("id", "")
                
                if "submitted" in verb_id:
                    total_quiz_attempts += 1
                    result = st.get("result", {})
                    if result.get("completion") is True:
                        correct_count += 1
                
                verb_display = re.sub(r'pressed controller button-\w to ', '', verb_display)
                verb_counts[verb_display] = verb_counts.get(verb_display, 0) + 1

                # 進度邏輯
                for ext_key in extensions.keys():
                    for task_id in TARGET_TASK_KEYS:
                        if task_id in ext_key:
                            user_progress[final_id].add(task_id)

        student_count = len(unique_students)

        # 進度計算
        if student_count > 0:
            individual_progresses = [
                (len(tasks) / len(TARGET_TASK_KEYS)) * 100 
                for tasks in user_progress.values()
            ]
            total_tasks_completed = sum(len(tasks) for tasks in user_progress.values())
            avg_progress = (total_tasks_completed / (student_count * len(TARGET_TASK_KEYS))) * 100
            max_progress = max(individual_progresses)
            min_progress = min(individual_progresses)
        else:
            avg_progress = max_progress = min_progress = 0

        correction_rate = (correct_count / total_quiz_attempts * 100) if total_quiz_attempts > 0 else 0

        return jsonify({
            "status": "success", 
            "record_count": filtered_record_count, # 這裡會連動 Records 面板
            "student_count": student_count,
            "average_progress": round(avg_progress, 2), 
            "max_progress": round(max_progress, 2), 
            "min_progress": round(min_progress, 2),
            "correction_rate": round(correction_rate, 2),
            "total_quiz_attempts": total_quiz_attempts,
            "verb_distribution": verb_counts, 
            "source": "LRS"
        })
    
    except Exception as e:
        print(f"Error Detail: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)