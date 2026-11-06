"""统一的请求客户端：自动带 token、自动断言 HTTP 层和业务层。"""
import requests

from config import BASE_URL, TIMEOUT


class ApiClient:
    def __init__(self, token=None):
        # Session 复用 TCP 连接，比每次 requests.get 快
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method, path, expect_code=200, **kwargs):
        """
        expect_code: 期望的业务码。正向用例是 200，反向用例传 401/500。
        """
        kwargs.setdefault("timeout", TIMEOUT)          # 调用方没传就用默认超时
        r = self.session.request(method, BASE_URL + path, **kwargs)

        # 第二层断言：HTTP 协议层
        assert r.status_code == 200, (
            f"{method} {path} 返回 HTTP {r.status_code}: {r.text[:200]}"
        )

        body = r.json()

        # 第三层断言：业务层
        if "code" in body:
            assert body["code"] == expect_code, (
                f"{method} {path} 业务码 {body['code']}（期望 {expect_code}）: {body.get('msg')}"
            )
        return body
