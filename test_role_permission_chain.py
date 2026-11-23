import uuid
import requests

from api.client import ApiClient
from config import BASE_URL, TIMEOUT


def test_role_permission_takes_effect_without_relogin(client, request):
  role_name = f"qa_chain_{uuid.uuid4().hex[:8]}"
  user_name = f"qa_chain_{uuid.uuid4().hex[:8]}"

  def cleanup():
    rows=client.request("GET", "/system/user/list", params={
      "userName": user_name, 
    }, timeout=TIMEOUT)["rows"]
    for row in rows:
      if row["userName"] == user_name:
        client.request("DELETE", f"/system/user/{row['userId']}")
    rows=client.request("GET", "/system/role/list", params={
      "roleName": role_name, 
    }, timeout=TIMEOUT)["rows"]
    for row in rows:
      if row["roleName"] == role_name:
        client.request("DELETE", f"/system/role/{row['roleId']}")

  request.addfinalizer(cleanup)

  # ① 建角色，menuIds 给空列表
  client.request("POST", "/system/role", json={
    "roleName": role_name, "roleKey": role_name,
    "roleSort": 1, "status": "0", "menuIds": [],
  })
  # ② 回查列表拿 role_id
  role_id = client.request("GET", "/system/role/list",
                           params={"roleName": role_name})["rows"][0]["roleId"]

  # ③ 建用户：deptId=103、roleIds=[role_id]、password="test123456"
  client.request("POST", "/system/user", json={
    "userName": user_name, 
    "nickName": "链路测试",
    "password": "test123456", 
    "deptId": 103, 
    "roleIds": [role_id]
  }, timeout=TIMEOUT)
  # ④ 用 requests.post 登录这个新用户，拿 token
  r=requests.post(f"{BASE_URL}/login", json={
    "username": user_name, 
    "password": "test123456", 
  }, timeout=TIMEOUT)
  token=r.json()["token"]
  # ⑤ 断言：ApiClient(token=新token).request("GET", "/system/user/list", expect_code=403)
  low= ApiClient(token=token)
  low.request("GET", "/system/user/list", expect_code=403)
  detail=client.request("GET", f"/system/role/{role_id}")["data"]
  client.request("PUT", f"/system/role", json={
    **detail, 
    "menuIds": [100]
  }, timeout=TIMEOUT)
  low.request("GET", "/system/user/list", expect_code=200)
  client.request("PUT", f"/system/role", json={
    **detail, 
    "menuIds": []
  }, timeout=TIMEOUT)
  low.request("GET", "/system/user/list", expect_code=403)

