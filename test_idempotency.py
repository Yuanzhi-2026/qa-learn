import uuid
import pytest



def test_delete_same_role_twice_is_idempotent(client, request):
  role_name=f"qu_role_{uuid.uuid4().hex[:8]}"
  def cleanup():
    rows=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
    for row in rows:
      if row["roleName"] ==role_name:
        client.request("DELETE", f"/system/role/{row['roleId']}")

  request.addfinalizer(cleanup)
  
  client.request("POST", "/system/role", json={
    "roleName": role_name,
    "roleKey": f"qa_long{uuid.uuid4().hex[:8]}",
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })
  rows=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
  role_id=rows[0]["roleId"]
  client.request("DELETE", f"/system/role/{role_id}")
  client.request("DELETE", f"/system/role/{role_id}")
  body=client.request("GET", f"/system/role/{role_id}")["data"]
  assert body["delFlag"] == "2"
  after=client.request("GET", "/system/role/list", params={"roleName": role_name})
  assert after["total"] == 0

  
def test_create_role_twice_with_same_key_creates_only_one(client, request):
  role_name=f"qu_role_{uuid.uuid4().hex[:8]}"
  role_key=f"qa_long{uuid.uuid4().hex[:8]}"
  def cleanup():
    rows=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
    for row in rows:
      if row["roleName"] ==role_name:
        client.request("DELETE", f"/system/role/{row['roleId']}")
  request.addfinalizer(cleanup)
  client.request("POST", "/system/role", json={
    "roleName": role_name,
    "roleKey": role_key,
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })
  dup=client.request("POST", "/system/role", expect_code=500, json={
    "roleName": role_name,
    "roleKey": role_key,
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })
  assert "已存在" in dup["msg"]
  after=client.request("GET", "/system/role/list", params={"roleName": role_name})
  assert after["total"] == 1


def test_put_same_role_twice_is_idempotent(client, request):
  role_name=f"qu_role_{uuid.uuid4().hex[:8]}"
  role_key=f"qa_long{uuid.uuid4().hex[:8]}"
  def cleanup():
    rows=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
    for row in rows:
      if row["roleName"] ==role_name:
        client.request("DELETE", f"/system/role/{row['roleId']}")
  request.addfinalizer(cleanup)
  client.request("POST", "/system/role", json={
    "roleName": role_name,
    "roleKey": role_key,
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })
  rows=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
  role_id=rows[0]["roleId"]
  client.request("PUT", "/system/role", json={
    "roleId": role_id,
    "roleName": role_name,
    "roleKey": role_key,
    "roleSort": 2, 
    "status": "0", 
    "menuIds": [],  
    })
  client.request("PUT", "/system/role", json={
    "roleId": role_id,
    "roleName": role_name,
    "roleKey": role_key,
    "roleSort": 2, 
    "status": "0", 
    "menuIds": [],  
    })
  body=client.request("GET", f"/system/role/{role_id}")["data"]
  assert body["roleName"] == role_name
  assert body["roleSort"] == 2
  assert body["status"] == "0"
