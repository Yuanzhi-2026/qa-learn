import requests
import json


BASE_URL = "http://127.0.0.1:8080"

def test_get_user_list_token_returns_200(auth_headers):
  r=requests.get(f"{BASE_URL}/system/user/list", headers=auth_headers, timeout=30)
  assert r.status_code == 200
  body=r.json()
  assert body["code"] == 200
  assert isinstance(body["total"], int)
  assert body["total"]>=1


def test_get_user_list_without_token_returns_401():
    r=requests.get(f"{BASE_URL}/system/user/list", timeout=30)
    assert r.status_code == 200
    assert r.json()["code"] == 401

def test_save_user(auth_headers):
   r=requests.post(f"{BASE_URL}/test/user/save", 
                   headers=auth_headers, 
                   params={"userId": 9, "username": "testuser", "password": "test123", "mobile": "13800000000"}, 
                   timeout=30)
   assert r.status_code == 200
   body=r.json()
   assert body["code"] == 200

def test_get_user_detail_after_save(auth_headers, new_user_id):
   r=requests.get(f"{BASE_URL}/test/user/{new_user_id}", 
                      headers=auth_headers, 
                      timeout=30)
   assert r.status_code == 200
   body=r.json()
   assert body["code"] == 200
   assert body["data"]["userId"] == new_user_id


def test_update_user_mobile(auth_headers, new_user_id):
   r_put=requests.put(f"{BASE_URL}/test/user/update", 
                  headers=auth_headers,
                  json={"userId": new_user_id, "username": "user2", "password": "test456", "mobile": "139999999999"},
                  timeout=30)
   assert r_put.status_code == 200
   body=r_put.json()
   assert body["code"] == 200
   r_get=requests.get(f"{BASE_URL}/test/user/{new_user_id}", 
                      headers=auth_headers, 
                      timeout=30)
   assert r_get.status_code == 200
   body=r_get.json()
   assert body["code"] == 200
   assert body["data"]["mobile"] == "139999999999"

def test_delete_user(auth_headers, new_user_id):
   r_delete=requests.delete(f"{BASE_URL}/test/user/{new_user_id}", 
                      headers=auth_headers, 
                      timeout=30)
   assert r_delete.status_code == 200
   body=r_delete.json()
   assert body["code"] == 200

   r_get=requests.get(f"{BASE_URL}/test/user/{new_user_id}", 
                      headers=auth_headers, 
                      timeout=30)
   assert r_get.status_code == 200
   body=r_get.json()
   assert body["code"] == 500
   assert body["msg"] == "用户不存在"





   


   




