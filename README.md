# 若依管理系统 · 接口自动化测试

[![CI](https://github.com/Yuanzhi-2026/qa-learn/actions/workflows/ci.yml/badge.svg)](https://github.com/Yuanzhi-2026/qa-learn/actions/workflows/ci.yml)

基于 Python + pytest + requests 的接口自动化测试项目，被测系统为 RuoYi 3.9.2（本地部署于 `http://127.0.0.1:8080`）。

## 技术栈

| 项 | 版本 |
|---|---|
| Python | 3.11 |
| pytest | 9.2.0 |
| requests | 2.34.2 |
| 被测系统 | RuoYi 3.9.2（Spring Boot 4.1 + JWT） |
| 数据库 / 缓存 | MySQL 8.0 / Redis 7（CI 环境） |
| 运行环境 | JDK 17 / Python 3.11 |

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
├── test_system_user.py  # 系统用户真实 CRUD + 越权访问（403 / 对照组）
├── test_param_boundary.py  # 参数边界：必填 / 长度边界 / 分页参数类型
├── test_idempotency.py     # 幂等：重复删除 / 重复创建 / 重复更新
├── test_concurrency.py     # 并发：10 线程同时创建同一角色
├── test_role_permission_chain.py  # 跨接口链路：角色 → 用户 → 登录 → 权限生效
├── api_index.py         # 辅助脚本：从 OpenAPI 文档检索接口定义
├── probe.py             # 辅助脚本：打印任意接口的返回结构
├── learn-log.md         # 复现日志：踩坑记录与复盘
├── .github/workflows/   # CI：代码检查 + 端到端测试
└── practice/            # 早期练习脚本（不参与用例收集）
```

## 快速开始

```powershell
# 1. 启动被测系统（RuoYi 后端，监听 8080）
# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行全部用例
pytest

# 换环境不用改代码，用环境变量覆盖
$env:BASE_URL="http://测试机IP:8080"; pytest

# 只跑某个文件 / 某条用例
pytest test_user.py
pytest test_user.py::test_delete_user
```

## 用例覆盖

共 **35 条**，覆盖 8 个模块（30 条通过 + 5 条标记为已知缺陷）：

| 模块 | 用例数 | 覆盖点 |
|---|---|---|
| 登录 | 2 | 登录成功返回 token、密码错误返回业务异常 |
| 用户（测试模块） | 6 | 列表查询、新增、详情、更新后读回校验、删除后读回校验、未授权 401 |
| 系统 | 9 | 部门树、角色列表（含分页一致性校验）、参数配置、岗位、公告、字典类型、在线用户、菜单树、未授权 401 |
| 系统用户（真实 CRUD） | 3 | 列表条件查询、修改后读回校验（含字段未被清空）、逻辑删除后 delFlag 校验 |
| 越权访问 | 3 | 空权限角色用户访问 `system/*` 返回 403（用户 / 部门）、同一用户访问免鉴权 demo 接口返回 200（对照组） |
| 参数边界 | 7 | 缺必填、字段超长被拒、边界值下沿成功（3 条）；分页参数 4 组非法输入用 `parametrize` 合并为 1 个函数、展开 4 项，全部 `xfail` |
| 幂等 | 3 | 同一角色连续删除两次（`delFlag` 置 2 且列表查不到）；相同 roleKey 重复创建被唯一约束挡住、库里仍 1 条；同一 body 连续 PUT 两次数据不变 |
| 并发 | 1 | `threading.Barrier` 让 10 线程同一刻提交同一请求，实测插入 9 条重复角色（`xfail`，见下） |
| 跨接口链路 | 1 | 建空权限角色 → 建用户挂角色 → 该用户登录后访问 403；给角色加菜单权限后**同一 token** 立即 200；撤销后又变 403 |

## 已知缺陷（用例标记为 xfail）

> 完整缺陷报告（含复现步骤、根因分析、修复建议、证据）：[`docs/缺陷报告.md`](docs/缺陷报告.md)


以下行为经实测确认与合理预期不符，用例断言写的是**期望值**并用 `@pytest.mark.xfail(strict=True)` 标记，缺陷修复后用例会转为失败以提醒更新。

| 接口 | 现象 | 影响 |
|---|---|---|
| `GET /system/role/list` | `pageNum=abc` 被静默忽略，按默认值返回全量数据（code 200） | 调用方传错参数类型完全无感知 |
| `GET /system/role/list` | `pageNum=-1` 未校验，按默认值返回全量数据（code 200） | 分页参数越界无反馈 |
| `GET /system/role/list` | `pageSize=100000` 无上限校验 | 大表场景下可被拖慢或内存放大 |
| `GET /system/role/list` | `pageSize=0` 时 `total=2` 但 `rows` 为空 | 分页契约不一致 |
| `POST /system/role` | 同一 roleKey 并发 10 次提交，9 次成功入库（`sys_role` 表无唯一索引，业务层 check-then-act 判重非原子） | 产生同名重复角色，后续按角色授权时权限范围翻倍 |

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
- `low_priv_token` 为 function 级 fixture，先造空权限角色、再建用户并绑定该角色，最后用该用户登录取 token；清理函数通过 `addfinalizer` 在创建动作之前登记，保证创建中途失败也能清干净
- 用例之间无执行顺序依赖，可单独运行

**4. 参数化**

形状相同的 5 个只读列表接口使用 `@pytest.mark.parametrize` 复用同一套断言，避免复制粘贴。

## 持续集成

CI 分两层，一层验证代码本身，一层验证真实系统。

| 作业 | 做什么 | 耗时 | 能发现什么 | 发现不了什么 |
|---|---|---|---|---|
| `check` | `compileall` 语法检查 + `pytest --collect-only` 用例收集 | 约 20 秒 | 语法错误、fixture 名对不上、参数化写错 | 接口行为变化 |
| `integration` | 起 MySQL 8 + Redis 7，现场编译并启动若依，跑全部 35 条用例 | 约 2 分钟（Maven 有缓存） | 业务回归、接口契约变更 | 前端问题、性能问题 |

`integration` 的执行链路：

```
MySQL/Redis service container
  → 导入 ry_*.sql + quartz.sql（建表 + 种子数据）
  → 关闭登录验证码（UPDATE sys_config）
  → clone RuoYi-Vue 源码并用 JDK 17 编译
  → java -jar 启动，轮询 /captchaImage 直到就绪
  → BASE_URL=http://127.0.0.1:8080 pytest
```

关键取舍：**被测系统不进仓库**。`ruoyi-admin.jar` 有 86 MB，超出 GitHub API 单次请求上限（base64 后约 115 MB），所以 CI 每次现场拉源码编译。Maven 依赖用 `actions/cache` 缓存，第二次起编译只花几十秒。

三个必须处理的环境差异（本地跑不出来，CI 就红）：

1. `setup-java` 的 `cache: maven` 要求本仓库根目录有 `pom.xml`，我们的是运行时拉取，所以改用 `actions/cache` 单独缓存 `~/.m2`
2. 若依 `logback.xml` 把日志路径写死为 `/home/ruoyi/logs`，目录不存在会直接启动失败
3. 种子数据里 `sys.account.captchaEnabled = true`，登录必须带图形验证码；CI 里改成 `false`

## 已知限制

- 登录接口未覆盖验证码场景（本地与 CI 环境都已关闭验证码）
- CI 的端到端作业跑在固定的 `ubuntu-latest` 上，未覆盖 Windows / 容器化部署场景
- 用例只覆盖单接口行为，未做跨接口的业务链路测试与并发场景

## 测试过程中发现的服务端行为

以下均为实际发请求验证的结果，不是文档描述：

1. **`PUT /system/user` 是全量更新**：请求体省略 `deptId` 时，该字段会被清空为 `null`，接口仍返回"操作成功"。用例采用"先 GET 详情 → 改一个字段 → 整个对象 PUT 回去"的方式规避。
2. **`userName`（登录名）不可修改**：PUT 时传入也不会生效，但接口照常返回成功。可修改的是 `nickName`。
3. **删除是逻辑删除**：DELETE 后 `GET /system/user/{id}` 仍能查到数据，只是 `delFlag` 从 `0` 变为 `2`；`GET /system/user/list` 会把已删除记录过滤掉。两个接口行为不一致，用例以 `delFlag` 作为删除断言依据。
4. **`DELETE` 不校验影响行数**：删除一个不存在的 `userId` 同样返回"操作成功"，因此清理逻辑必须回查确认。
5. **`POST /system/user` 不返回新用户 ID**：只能通过 `GET /system/user/list?userName=xxx` 回查获取。该查询为 `like` 模糊匹配，用例通过随机 `userName` + `total == 1` 断言避免误取。
