import pytest
import requests
from api.client import ApiClient

from config import BASE_URL, ADMIN_USER, ADMIN_PASSWORD, TIMEOUT
import uuid



@pytest.fixture(scope="session")
def token():
    r = requests.post(
        f"{BASE_URL}/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert r.json()["code"] == 200, f"登录失败: {r.json()}"
    yield r.json()["token"]



@pytest.fixture
def new_user_id(auth_headers):
    uid=9438666
    r=requests.post(f"{BASE_URL}/test/user/save", 
                    params={"userId": uid, "username": "user1", "password": "test123456", "mobile": "138000"},
                    headers=auth_headers,
                    timeout=TIMEOUT)
    yield uid
    requests.delete(
        f"{BASE_URL}/test/user/{uid}",
        headers=auth_headers,
        timeout=TIMEOUT,
    )

@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def client(token):
    return ApiClient(token=token)


@pytest.fixture
def low_priv_token(client, request):
    name=f"qa_low_{uuid.uuid4().hex[:8]}"
    role_name=f"qa_guest_{uuid.uuid4().hex[:8]}"
    def cleanup():
        rows=client.request("GET", "/system/user/list", 
                            params={"userName": name})["rows"]
        for row in rows:
            if row["userName"] == name:
                client.request("DELETE", f"/system/user/{row['userId']}")
        rows=client.request("GET", "/system/role/list", 
                            params={"roleName": role_name})["rows"]
        for row in rows:
            if row["roleName"] == role_name:
                client.request("DELETE", f"/system/role/{row['roleId']}")
    request.addfinalizer(cleanup)
    client.request("POST", "/system/role", json={
        "roleName": role_name, 
        "roleKey": role_name, 
        "roleSort": 1, 
        "status": "0", 
        "menuIds": [], 
    })
    body=client.request("GET", "/system/role/list", params={"roleName": role_name})["rows"]
    role_id=body[0]["roleId"]
    print("role_id: ", role_id)

    client.request("POST", "/system/user", json={
        "deptId": 103,
        "userName": name, 
        "nickName" : "低权限测试用户",
        "sex" : "0", 
        "password": "test123456",
        "status": "0",
        "roleIds": [role_id]
    })
    r=requests.post(f"{BASE_URL}/login",json={
        "username": name,
        "password": "test123456"
    }, timeout=TIMEOUT)
    assert r.json()["code"] == 200, f"低权限测试用户登录失败: {r.json()}"
    yield r.json()["token"]

       
    

    





                    
    

