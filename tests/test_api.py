import pytest
import time
import json
from fastapi.testclient import TestClient
from report_generator.main import create_app  # 导入 create_app

# 创建应用实例
app = create_app()
client = TestClient(app)

def test_generate_report_success():
    with open("tests/test_data.json", "r") as f:
        test_data = json.load(f)
    
    response = client.post("/generate-report/", json=test_data)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "report.docx" in response.headers["content-disposition"]

def test_generate_report_invalid_data():
    response = client.post("/generate-report/", json={"invalid": "data"})
    assert response.status_code == 422

def test_rate_limiting(monkeypatch):
    # 启用速率限制并使用 Redis
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    # monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 创建新的应用实例（确保使用新的速率限制状态）
    test_app = create_app()
    test_client = TestClient(test_app)

    with open("tests/test_data.json", "r") as f:
        test_data = json.load(f)

    # 发送6个请求 - 添加微小延迟
    responses = []
    for i in range(6):
        responses.append(test_client.post("/generate-report/", json=test_data))
        time.sleep(0.1)  # 添加100ms延迟确保区分请求
    
    # 检查状态码
    status_codes = [r.status_code for r in responses]
    print("Status codes:", status_codes)  # 调试输出
    
    # 前5个应该成功
    for res in responses[:5]:
        assert res.status_code == 200
    
    # 第6个应该被限制
    assert responses[5].status_code == 429