import pytest
import requests

BASE_URL = "http://127.0.0.1:8080"


@pytest.fixture(scope="session")
def token():
    r = requests.post(
        f"{BASE_URL}/login",
        json={"username": "admin", "password": "admin123"},
        timeout=30,
    )
    assert r.json()["code"] == 200, f"登录失败: {r.json()}"
    yield r.json()["token"]



@pytest.fixture
def new_user_id(auth_headers):
    uid=9438666
    r=requests.post(f"{BASE_URL}/test/user/save", 
                    params={"userId": uid, "username": "user1", "password": "test123456", "mobile": "138000"},
                    headers=auth_headers,
                    timeout=30)
    yield uid
    requests.delete(
        f"{BASE_URL}/test/user/{uid}",
        headers=auth_headers,
        timeout=30,
    )

@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

                    
    

