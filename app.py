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
        # Gọi tới API của bạn để lấy dữ liệu 26 bàn
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("success"): return {"error": "Lấy dữ liệu thất bại"}

        all_results = []
        for item in data.get("data", []):
            table_id = item.get("table")
            raw_res = item.get("result", "")
            
            # Chạy thuật toán cho từng bàn
            algo = BaccaratAlgo(raw_res)
            prediction = algo.predict_logic()
            
            all_results.append({
                "table": table_id,
                "prediction": prediction,
                "raw": raw_res[-5:] # Lấy 5 con cuối xem chơi
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