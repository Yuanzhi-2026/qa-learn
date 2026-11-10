"""临时查看接口返回结构的工具。

用法：
    python probe.py "/system/user/list?userName=admin"
    python probe.py /system/role/list
"""
import json
import sys

import requests

from config import ADMIN_PASSWORD, ADMIN_USER, BASE_URL, TIMEOUT

path = sys.argv[1] if len(sys.argv) > 1 else "/v3/api-docs"

session = requests.Session()
login = session.post(
    f"{BASE_URL}/login",
    json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
    timeout=TIMEOUT,
).json()
session.headers["Authorization"] = "Bearer " + login["token"]

resp = session.get(BASE_URL + path, timeout=TIMEOUT)
print(f"GET {path}")
print(f"HTTP {resp.status_code}")

try:
    body = resp.json()
except ValueError:
    print("返回不是 JSON：", resp.text[:300])
    sys.exit(0)

print("顶层键:", list(body.keys()))
print("code =", body.get("code"), "| msg =", body.get("msg"))

for key in ("rows", "data"):
    value = body.get(key)
    if isinstance(value, list):
        print(f"{key}: 列表，{len(value)} 条")
        if value:
            print(f"{key}[0] 的字段:", list(value[0].keys()))
    elif value is not None:
        print(f"{key}: {type(value).__name__} -> {json.dumps(value, ensure_ascii=False)[:200]}")
