import collections
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 1. ĐỊNH NGHĨA THUẬT TOÁN (PHẢI CÓ CÁI NÀY MỚI HẾT LỖI) ---
class BaccaratRobotAlgo:
    def __init__(self, history):
        self.history = history
        self.algorithms = {
            "Cầu Bệt": self.predict_bet,
            "Cầu 1-1": self.predict_1_1,
            "Cầu 2-2": self.predict_2_2,
            "Cầu Nghiêng": self.predict_bias
        }

    def predict_bet(self, sub_history):
        return sub_history[-1] if sub_history else None

    def predict_1_1(self, sub_history):
        return 1 - sub_history[-1] if sub_history else None

    def predict_2_2(self, sub_history):
        if len(sub_history) < 2: return sub_history[-1]
        if sub_history[-1] == sub_history[-2]:
            return 1 - sub_history[-1]
        return sub_history[-1]

    def predict_bias(self, sub_history):
        if not sub_history: return None
        count = collections.Counter(sub_history)
        return 0 if count[0] >= count[1] else 1

    def get_best_prediction(self):
        if len(self.history) < 5:
            return {"prediction": "CHỜ DỮ LIỆU", "algorithm": "N/A", "confidence": "0%"}

        algo_scores = {name: 0 for name in self.algorithms.keys()}
        test_depth = min(len(self.history), 10)
        
        for i in range(test_depth - 1, 0, -1):
            curr_idx = len(self.history) - i
            past_data = self.history[:curr_idx]
            real_res = self.history[curr_idx]
            for name, func in self.algorithms.items():
                if func(past_data) == real_res:
                    algo_scores[name] += 1

        best_algo = max(algo_scores, key=algo_scores.get)
        win_rate = (algo_scores[best_algo] / (test_depth - 1)) * 100
        final_pred = self.algorithms[best_algo](self.history)
        
        return {
            "prediction": "CON" if final_pred == 0 else "CÁI",
            "algorithm": best_algo,
            "confidence": f"{int(win_rate)}%"
        }

# --- 2. HÀM XỬ LÝ LẤY DỮ LIỆU TỪ API GỐC ---
def get_analysis():
    url = "https://api-bcr-thanhnhan.onrender.com/api/baccarat"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("success"):
            return {"error": "API gốc không trả về dữ liệu thành công"}

        tables = data.get("data", [])
        all_results = []

        for item in tables:
            table_id = item.get("table")
            raw_result = item.get("result", "")
            
            # Chuyển chữ P, B thành số 0, 1
            history = []
            for char in raw_result:
                if char == 'P': history.append(0)
                elif char == 'B': history.append(1)

            # Gọi Class thuật toán đã định nghĩa ở trên
            robot = BaccaratRobotAlgo(history)
            pred = robot.get_best_prediction()

            all_results.append({
                "table": table_id,
                "total_rounds": len(raw_result), # Hiển thị full số ván lấy được
                "prediction": pred['prediction'],
                "algorithm": pred['algorithm'],
                "confidence": pred['confidence'],
                "history_raw": raw_result
            })
        return all_results
    except Exception as e:
        return {"error": str(e)}

# --- 3. ĐỊNH NGHĨA ĐƯỜNG DẪN /PHANTICH ---
@app.route('/phantich', methods=['GET'])
def phantich_api():
    results = get_analysis()
    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
