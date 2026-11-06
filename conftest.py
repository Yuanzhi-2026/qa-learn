import pytest
import requests
from api.client import ApiClient

from config import BASE_URL, ADMIN_USER, ADMIN_PASSWORD, TIMEOUT



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





                    
    

