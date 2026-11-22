import uuid
import threading

import pytest

from api.client import ApiClient


@pytest.mark.xfail(strict=True, reason="若依 sys_role 无唯一索引，并发创建绕过业务查重产生重复数据")
def test_concurrent_create_role_creates_only_one(client, token, request):
  role_name = f"qa_cc_{uuid.uuid4().hex[:8]}"

  def cleanup():
    rows = client.request("GET", "/system/role/list",
                          params={"roleName": role_name})["rows"]
    for row in rows:
      if row["roleName"] == role_name:
        client.request("DELETE", f"/system/role/{row['roleId']}")

  request.addfinalizer(cleanup)

  # 1 定义 payload（10 个线程共用这一个 dict）
  payload = {
    "roleName": role_name,
    "roleKey": role_name,
    "roleSort": 1,
    "status": "0",
    "menuIds": [],
  }

  # 2 起跑线 + 收集容器
  n = 10
  barrier = threading.Barrier(n)
  results = []
  lock = threading.Lock()

  # 3 每个线程做的事
  def worker():
    barrier.wait()
    c = ApiClient(token=token)
    try:
      body = c.request("POST", "/system/role", json=payload)
      code = body["code"]
    except AssertionError as e:
      code = str(e)[:60]
    with lock:
      results.append(code)

  # 4 起 10 个线程，全部启动后再等它们全部结束
  threads = [threading.Thread(target=worker) for _ in range(n)]
  for t in threads:
    t.start()
  for t in threads:
    t.join()

  # 5 回查：库里应该只有 1 条
  after = client.request("GET", "/system/role/list", params={"roleName": role_name})
  assert after["total"] == 1, f"并发 {n} 次创建后库里 {after['total']} 条；各线程返回：{results}"
