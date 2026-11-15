# 若依管理系统 · 接口自动化测试

[![CI](https://github.com/Yuanzhi-2026/qa-learn/actions/workflows/ci.yml/badge.svg)](https://github.com/Yuanzhi-2026/qa-learn/actions/workflows/ci.yml)

基于 Python + pytest + requests 的接口自动化测试项目，被测系统为 RuoYi 3.9.2（本地部署于 `http://127.0.0.1:8080`）。

## 技术栈

| 项 | 版本 |
|---|---|
| Python | 3.11 |
| pytest | 9.2.0 |
| requests | 2.34.2 |
| 被测系统 | RuoYi 3.9.2（Spring Boot + JWT） |

## 目录结构

```
qa-learn/
├── config.py            # 全局配置：服务地址、账号、超时
├── conftest.py          # fixture：登录 token、请求头、测试数据（含自动清理）
├── pytest.ini           # pytest 配置：用例收集范围
├── api/
│   ├── __init__.py
│   └── client.py        # 请求客户端：统一鉴权 + 三层断言
├── test_login.py        # 登录接口（正向 / 密码错误）
├── test_user.py         # 用户 CRUD（增 / 查 / 改 / 删 / 鉴权）
├── test_system.py       # 系统模块只读接口（部门 / 角色 / 配置 / 字典 / 在线用户 / 菜单）
├── api_index.py         # 辅助脚本：从 OpenAPI 文档检索接口定义
└── practice/            # 早期练习脚本（不参与用例收集）
```

## 快速开始

```powershell
# 1. 启动被测系统（RuoYi 后端，监听 8080）
# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行全部用例
pytest

# 只跑某个文件 / 某条用例
pytest test_user.py
pytest test_user.py::test_delete_user
```

## 用例覆盖

共 **20 条**，覆盖 4 个模块：

| 模块 | 用例数 | 覆盖点 |
|---|---|---|
| 登录 | 2 | 登录成功返回 token、密码错误返回业务异常 |
| 用户（测试模块） | 6 | 列表查询、新增、详情、更新后读回校验、删除后读回校验、未授权 401 |
| 系统 | 9 | 部门树、角色列表（含分页一致性校验）、参数配置、岗位、公告、字典类型、在线用户、菜单树、未授权 401 |
| 系统用户（真实 CRUD） | 3 | 列表条件查询、修改后读回校验（含字段未被清空）、逻辑删除后 delFlag 校验 |

## 设计说明

**1. 分层**

```
config.py  →  conftest.py  →  api/client.py  →  用例
（配置）      （前置数据）     （请求 + 断言）     （业务断言）
```

用例只表达业务意图，不重复写 URL、请求头、超时和协议层断言。

**2. 三层断言**

| 层 | 判断 | 位置 |
|---|---|---|
| HTTP 层 | `status_code == 200` | `ApiClient.request` 统一断言 |
| 业务层 | `body["code"] == expect_code` | `ApiClient.request` 统一断言 |
| 数据层 | 业务字段是否符合预期 | 各用例自行断言 |

反向用例通过 `expect_code` 参数显式声明期望的异常码（如 `expect_code=401`）。

**3. 测试数据管理**

- `token` 为 session 级 fixture，整个测试过程只登录一次
- `new_user_id` 为 function 级 fixture，每条用例创建独立数据，`yield` 后自动删除
- 用例之间无执行顺序依赖，可单独运行

**4. 参数化**

形状相同的 5 个只读列表接口使用 `@pytest.mark.parametrize` 复用同一套断言，避免复制粘贴。

## 已知限制

- 被测系统为本地部署，用例未做环境切换（`config.py` 中写死 `127.0.0.1:8080`）
- 登录接口未覆盖验证码场景（本地部署已关闭验证码）
- 未接入 CI，需手动执行

## 测试过程中发现的服务端行为

以下均为实际发请求验证的结果，不是文档描述：

1. **`PUT /system/user` 是全量更新**：请求体省略 `deptId` 时，该字段会被清空为 `null`，接口仍返回"操作成功"。用例采用"先 GET 详情 → 改一个字段 → 整个对象 PUT 回去"的方式规避。
2. **`userName`（登录名）不可修改**：PUT 时传入也不会生效，但接口照常返回成功。可修改的是 `nickName`。
3. **删除是逻辑删除**：DELETE 后 `GET /system/user/{id}` 仍能查到数据，只是 `delFlag` 从 `0` 变为 `2`；`GET /system/user/list` 会把已删除记录过滤掉。两个接口行为不一致，用例以 `delFlag` 作为删除断言依据。
4. **`DELETE` 不校验影响行数**：删除一个不存在的 `userId` 同样返回"操作成功"，因此清理逻辑必须回查确认。
5. **`POST /system/user` 不返回新用户 ID**：只能通过 `GET /system/user/list?userName=xxx` 回查获取。该查询为 `like` 模糊匹配，用例通过随机 `userName` + `total == 1` 断言避免误取。
