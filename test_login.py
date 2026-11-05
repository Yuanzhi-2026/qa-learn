import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_login_success_returns_token():
  r=requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"}, timeout=30)
  assert r.status_code == 200
  assert r.json()["code"] == 200
  assert r.json()["token"]


def test_login_wrong_password_returns_business_error():
  r=requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "wrongpass"}, timeout=30)
  assert r.status_code == 200
  print(r.status_code, r.json())
  assert "密码错误" in r.json()["msg"]  
  assert r.json()["code"] == 500

  
