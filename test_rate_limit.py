import requests
import time
import json  # 添加json模块

url = "http://localhost:8000/generate-report/"
headers = {"Content-Type": "application/json"}

with open("tests/test_data.json", "r", encoding="utf-8") as f:
    # 使用json.load解析JSON
    data = json.load(f)

print("Ограничение скорости тестирования (5 запросов в минуту)：")
for i in range(1, 7):
    # 使用json参数自动设置Content-Type
    response = requests.post(url, json=data, headers=headers)
    status = "✅ успех" if response.status_code == 200 else "❌ Ограниченный" if response.status_code == 429 else f"❌ 错误({response.status_code})"
    print(f"просить {i} - Код статуса: {response.status_code} ({status})")
    
    # 如果是400错误，打印响应内容
    if response.status_code == 400:
        print(f"Подробности ошибки: {response.text}")
    
    time.sleep(0.1)