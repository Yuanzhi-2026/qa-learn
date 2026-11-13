from api.client import ApiClient
import pytest
import uuid

def test_get_system_user_list_returns_200(client):
  body=client.request("GET", "/system/user/list", params={"userName": "admin"})
  assert body["total"] == 1
  assert body["rows"][0]["userName"] == "admin"



@pytest.fixture
def new_user_id(client):
  name = f"qa_{uuid.uuid4().hex[:8]}"
  client.request("POST", "/system/user", 
                 json={"userName" : name, "nickName": "测试用户", "password": "test456",
                 "deptId": 103, "roleIds": [2], "postId": [1], "sex": "0", "status": 0})
  rows=client.request("GET", "/system/user/list", params={
                      "userName": name})
  uid=rows["rows"][0]["userId"]
  
  yield uid
  client.request("DELETE", f"/system/user/{uid}")
  
 

def test_put_system_user_returns_200(client, new_user_id):
  data=client.request("GET", f"/system/user/{new_user_id}")
  data["data"]["nickName"]="yuanzi"
  client.request("PUT", "/system/user", json=data["data"])
  data=client.request("GET", f"/system/user/{new_user_id}")
  assert data["data"]["nickName"] == "yuanzi"
  assert data["data"]["deptId"] == 103


def test_delete_systen_user_returns_200(client, new_user_id):
  client.request("DELETE", f"/system/user/{new_user_id}")
  data=client.request("GET", f"/system/user/{new_user_id}")
  assert data["data"]["delFlag"] == "2"

  
