import uuid
import pytest

def test_create_role_without_name_returns_500(client):
  body=client.request("POST", "/system/role", expect_code=500, json={
    "roleKey": "qa_guest",
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],
  })

  assert "角色名称不能为空" in body["msg"]

def test_create_role_with_name_31_chars_returns_500(client):
  roleName="a"*31
  body=client.request("POST", "/system/role", expect_code=500, json={
    "roleName": roleName,
    "roleKey": f"qa_long{uuid.uuid4().hex[:8]}",
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })

  assert "角色名称长度不能超过30个字符" in body["msg"]

def test_create_role_with_name_30_chars_returns_200(client, request):
  roleName=f"qa30_{uuid.uuid4().hex}"[:30]
  def cleanup():
    rows=client.request("GET", "/system/role/list", 
                       params={"roleName": roleName})["rows"]
    for row in rows:
      if row["roleName"] == roleName:
        client.request("DELETE", f"/system/role/{row['roleId']}")

  request.addfinalizer(cleanup)
  client.request("POST", "/system/role", json={
    "roleName": roleName,
    "roleKey": f"qa_long{uuid.uuid4().hex[:8]}",
    "roleSort": 1, 
    "status": "0", 
    "menuIds": [],  
    })

  row=client.request("GET", "/system/role/list", 
                     params={"roleName": roleName})["rows"]
  assert len(row) ==1
  assert row[0]["roleName"] == roleName
  assert len(row[0]["roleName"]) == 30


@pytest.mark.xfail(strict=True, reason="若依未校验 pageNum 类型，非数字被静默忽略并返回全量数据")
def test_role_list_with_non_numeric_page_num_is_rejected(client):
  body=client.request("GET", "/system/role/list", params={
    "pageNum": "abc",
    "pageSize": 10,
  })
  assert body["code"]!=200

@pytest.mark.xfail(strict=True, reason="pageNum 负数未校验，服务端按默认值返回全量数据")
def test_role_list_with_negative_page_num_is_rejected(client):
  body=client.request("GET", "/system/role/list", params={
    "pageNum": -1,
    "pageSize": 10,
  })
  assert body["code"]!=200
