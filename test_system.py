from api.client import ApiClient

def test_get_dept_list_returns_200(client):
  body=client.request("GET", "/system/dept/list")
  assert isinstance(body["data"], list)
  assert len(body["data"])>=1

def test_get_role_list_returns_200(client):
  body=client.request("GET", "/system/role/list")
  assert isinstance(body["total"], int)
  assert body["total"]>=1
  assert body["total"] == len(body["rows"])


def test_get_role_list_without_token_returns_401():
  anon=ApiClient()
  anon.request("GET", "/system/role/list", expect_code=401)



