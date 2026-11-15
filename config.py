"""全局配置：一处定义，到处引用。换环境只改这里。

支持环境变量覆盖，CI 里就不用改代码：
  BASE_URL      被测系统地址，默认 http://127.0.0.1:8080
  ADMIN_USER    登录账号，默认 admin
  ADMIN_PASSWORD 登录密码，默认 admin123
  TIMEOUT       单次请求超时秒数，默认 30
"""

import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8080").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
TIMEOUT = int(os.getenv("TIMEOUT", "30"))
