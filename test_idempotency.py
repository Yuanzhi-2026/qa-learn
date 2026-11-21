import uuid
import pytest



def test_two_delete_returns_200(client, request):
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

  

