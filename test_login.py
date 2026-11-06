import requests
import json

from config import BASE_URL, ADMIN_USER, ADMIN_PASSWORD, TIMEOUT


def test_login_success_returns_token():
  r=requests.post(f"{BASE_URL}/login", json={"username": ADMIN_USER, "password": ADMIN_PASSWORD}, timeout=TIMEOUT)
  assert r.status_code == 200
  assert r.json()["code"] == 200
  assert r.json()["token"]


def test_login_wrong_password_returns_business_error():
  r=requests.post(f"{BASE_URL}/login", json={"username": ADMIN_USER, "password": "wrongpass"}, timeout=TIMEOUT)
  assert r.status_code == 200
  print(r.status_code, r.json())
  assert "密码错误" in r.json()["msg"]  
  assert r.json()["code"] == 500

  
