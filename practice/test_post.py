import requests
import pytest

BASE_URL = "https://jsonplaceholder.typicode.com"


def test_get_post_exist_returns_200():
    r = requests.get(f"{BASE_URL}/posts/1", timeout=30)

    # 第一层：HTTP 状态码
    assert r.status_code == 200

    # 第二层/第三层：业务字段
    body = r.json()
    assert body["id"] == 1
    assert body["title"]
@pytest.mark.parametrize("invalid_id", [
    999999,-1,0,"abc"
])
def test_get_post_invalid_id_returns_404(invalid_id):
    r = requests.get(f"{BASE_URL}/posts/{invalid_id}", timeout=30)
    assert r.status_code == 404
    assert r.json() == {}

    
