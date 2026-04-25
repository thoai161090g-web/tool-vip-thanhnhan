import collections
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# --- 1. THUẬT TOÁN CỦA BẠN (Đã sửa để nhận diện chuỗi P, B, T) ---
class BaccaratAlgo:
    def __init__(self, raw_result):
        # Chuyển chuỗi "BTPBB" thành list [1, 0, 1, 1]
        self.history = []
        for char in raw_result:
            if char == 'P': self.history.append(0)
            elif char == 'B': self.history.append(1)
            # T (Hòa) thường bỏ qua trong soi cầu

    def predict_logic(self):
        if len(self.history) < 5: return "CHỜ..."
        # Ví dụ: đánh bệt (theo con cuối)
        return "CON" if self.history[-1] == 0 else "CÁI"

# --- 2. HÀM GỌI API GỐC VÀ XỬ LÝ 26 BÀN ---
def get_analysis():
    url = "https://api-bcr-thanhnhan.onrender.com/api/baccarat"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("success"): return {"error": "Lấy dữ liệu thất bại"}

        all_results = []
        for item in data.get("data", []):
            table_id = item.get("table")
            raw_res = item.get("result", "") # Đây là chuỗi full: "BTPBBP..."
            
            # --- PHẦN XỬ LÝ FULL DỮ LIỆU ---
            # Chuyển chuỗi sang list số để thuật toán chạy
            history_indices = []
            for char in raw_res:
                if char == 'P': history_indices.append(0)
                elif char == 'B': history_indices.append(1)
                # Nếu gặp 'T', thuật toán sẽ giữ nguyên nhịp cũ hoặc bỏ qua tùy bạn
                # Ở đây ta lấy full P và B để không làm gãy cầu
            
            # Đếm tổng số ván thực tế (P + B + T)
            total_rounds = len(raw_res) 
            
            # Đưa vào thuật toán của bạn
            robot = BaccaratRobotAlgo(history_indices) 
            prediction = robot.get_best_prediction()
            
            all_results.append({
                "table": table_id,
                "total_rounds": total_rounds, # Hiển thị số ván
                "prediction": prediction['prediction'],
                "algorithm": prediction['algorithm'],
                "confidence": prediction['confidence'],
                "full_string": raw_res # Trả về chuỗi gốc để bạn đối chiếu
            })
        return all_results
    except Exception as e:
        return {"error": str(e)}

# --- 3. CỔNG API CỦA RIÊNG BẠN ---
@app.route('/phantich', methods=['GET'])
def api_home():
    results = get_analysis()
    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
