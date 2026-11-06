from api.client import ApiClient


def test_get_user_list_token_returns_200(client):
    body = client.request("GET", "/system/user/list")
    assert isinstance(body["total"], int)
    assert body["total"] >= 1


def test_get_user_list_without_token_returns_401():
    anon = ApiClient()                      # 不带 token 的客户端
    anon.request("GET", "/system/user/list", expect_code=401)


def test_save_user(client):
    client.request("POST", "/test/user/save",
                   params={"userId": 9, "username": "testuser", "password": "test123",
                           "mobile": "13800000000"})


def test_get_user_detail_after_save(client, new_user_id):
    body = client.request("GET", f"/test/user/{new_user_id}")
    assert body["data"]["userId"] == new_user_id


def test_update_user_mobile(client, new_user_id):
    client.request("PUT", "/test/user/update",
                   json={"userId": new_user_id, "username": "user2", "password": "test456",
                         "mobile": "139999999999"})
    body = client.request("GET", f"/test/user/{new_user_id}")
    assert body["data"]["mobile"] == "139999999999"


def test_delete_user(client, new_user_id):
    client.request("DELETE", f"/test/user/{new_user_id}")
    body = client.request("GET", f"/test/user/{new_user_id}", expect_code=500)
    assert body["msg"] == "用户不存在"
