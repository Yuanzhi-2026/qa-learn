# learn-log · qa-learn

## 若依管理系统 接口自动化测试

**2026-11-15 · 20 passed**（登录 2 + 测试模块用户 6 + 系统只读 9 + 系统用户 CRUD 3）

**环境**：Python 3.11.15（uv venv）｜pytest 9.2.0｜requests 2.34.2｜pytest-html 4.2.0｜被测 RuoYi 3.9.2 @ 127.0.0.1:8080（`java -jar ruoyi-admin.jar` 启动，需 MySQL + Redis 已运行）

**踩过的坑**
1. `BASE_URL + path` 是纯拼接，path 必须 `/` 开头，否则 `'127.0.0.1:8080system' is not a valid host`
2. `GET /system/user/list` 是 `like` 模糊匹配，`rows[0]` 不保证是目标用户 → 断言 `total == 1`
3. `POST /system/user` 不返回新 ID → 必须回查列表；且 `userName` 大小写敏感，写错静默返回全量
4. `PUT /system/user` 全量更新，省略 `deptId` 会被清空为 null 且返回成功 → 先 GET 详情再整对象 PUT
5. `userName`（登录名）不可修改，传了也忽略，但返回"操作成功"
6. 删除是逻辑删除：详情仍返回 `delFlag='2'`，列表已过滤；`DELETE` 不存在的 id 也返回成功
7. **fixture 在 `yield` 之前抛异常 → 清理代码永不执行 → 库里残留垃圾数据**（本轮出现 3 次，已手工清理）

**还没掌握的**
- fixture 失败时如何保证清理（`request.addfinalizer` / `try-finally`）
- 响应体分层：`body`（含 code/msg/data）vs `data`（对象本身），变量名必须与内容一致

**面试清单**
- 简历一句话：基于 pytest + requests 的若依接口自动化框架，20 条用例覆盖 4 模块，分层封装 + 数据自给自足
- 最可能被追问：① 为什么用 fixture 造数据而不是写死 ID ② 三层断言怎么分层 ③ 逻辑删除怎么验证 ④ 用例失败会不会留下脏数据
- 目前答不好：④（`addfinalizer` 还没用过）、参数化与分开写的判据只停留在"断言是否相同"

## 下次继续（2026-11-15 记录）

**已完成**：20 条用例全绿 · fixture 改用 `addfinalizer` · README 含「测试中发现的服务端行为」· `.github/workflows/ci.yml` 已写好

**卡在哪**：GitHub 推送不通（`github.com:443` / `:22` 均被封，只有 `api.github.com` 通）。仓库已建：`Yuanzhi-2026/qa-learn`

**明天第一步**：
1. 开代理
2. 远端默认分支是 `main`（只有一个 README 初始化提交 `031aea8c`），本地是 `master`
3. 推送用：`git push -u origin master:main`
4. 到 GitHub 看 Actions 是否变绿

**B 选项（端到端 CI）待决定**：需 4~6 小时，CI 里 service container 起 MySQL+Redis + 若依源码 `mvn package`（jar 86MB 无法走 API 上传）

## 2026-11-15 晚 · GitHub 接通，CI 变绿

**成果**：仓库 https://github.com/Yuanzhi-2026/qa-learn 已上线，13 个提交，CI 两次运行全绿

**踩到的三个坑（按顺序）**

1. `CRYPT_E_NO_REVOCATION_CHECK (0x80092012)` —— 代理环境下 Windows schannel 吊销检查过不去。`http.schannelCheckRevoke=false` 不生效，最终用 `GIT_SSL_NO_VERIFY=true` 环境变量绕过（只对我的子进程生效，未写进系统环境变量）
2. `credential.helper=helper-selector` 会弹图形提示卡住推送。改用内联 helper 传 token：`-c credential.helper='!f(){ echo username=x-access-token; echo "password=$GH_TOKEN"; }; f'`
3. `refusing to allow an OAuth App to create or update workflow ... without 'workflow' scope` —— gh 默认 token 只有 `gist, read:org, repo`，推 `.github/workflows/` 需要额外授权。解法：`gh auth refresh -s workflow`

**绕过第 3 个坑的办法**：先把不含 ci.yml 的提交 `e770c06` 推到 main，让代码先上线，再补授权推剩余提交

**最终状态**：本地分支由 `master` 改名 `main`，与远端一致；README 加了 CI 徽章

## 2026-11-15 晚 · B 方案完成：CI 里跑真实若依

**最终结果**：`integration` 作业全绿，20 passed，耗时约 2 分钟（Maven 有缓存）

**做了什么**

1. `config.py` 改成读环境变量（`BASE_URL` / `ADMIN_USER` / `ADMIN_PASSWORD` / `TIMEOUT`），本地默认值不变
2. `ci.yml` 拆成两个作业：`check`（语法 + 收集，20 秒）与 `integration`（起 MySQL+Redis+若依，跑真接口）
3. 被测系统不进仓库：CI 每次 clone RuoYi-Vue 源码，用 JDK 17 现场编译

**四个坑，按踩到顺序**

| 坑 | 报错 | 解法 |
|---|---|---|
| setup-java 的 maven 缓存 | `No file in ... matched to [**/pom.xml]` | 本仓库没有 pom.xml，改用 `actions/cache` 缓存 `~/.m2/repository` |
| 若依日志路径写死 | `Logback configuration error detected` + `/home/ruoyi/logs` 不存在 | `sudo mkdir -p /home/ruoyi/logs` |
| 登录验证码 | `{'msg': '验证码已失效', 'code': 500}` | 种子数据 `sys.account.captchaEnabled=true`，导入 SQL 后 UPDATE 成 false |
| gh token 缺 workflow 权限 | `refusing to allow an OAuth App to create ... workflow` | `gh auth refresh -s workflow` |

**记住的判断**：CI 里 `check` 绿只说明代码能跑，`integration` 绿才说明系统还能用。两层都要有。

## 2026-11-15 深夜 · 越权用例开局

**进度**：简历表述写完（`简历表述.md`），越权用例的 fixture 写到一半

**实测得到的事实**

| 调用方 | /system/user/list |
|---|---|
| admin | code 200 |
| 普通用户 ry | code 200（它的角色被分了很多菜单，**不能用来测越权**） |
| 新建空权限用户 | HTTP 200 + **code 403**「没有权限，请联系管理员授权」 |

**其他实测**：`GET /system/role/{名字}` 报「参数[roleId]要求 Long」；角色被用户引用时删除报「已分配,不能删除」，所以 cleanup 必须先删用户再删角色。

**下次继续**：补完 `low_priv_token` 的创建部分（造角色→回查 roleId→造用户→登录 yield token），再写 3 条用例（越权 403 ×2 + 对照组 /test/user/list 200）

## 2026-11-17 · 越权用例完成（23 passed）

**成果**：新增 3 条越权用例 + 1 个 `low_priv_token` fixture，全部 23 条 1.86s 通过，库里零残留。

| 用例 | 期望 |
|---|---|
| 低权限用户查 `/system/user/list` | HTTP 200 + 业务码 403「没有权限，请联系管理员授权」 |
| 低权限用户查 `/system/dept/list` | 同上 |
| 低权限用户查 `/test/user/list` | 200，`data` 2 条（对照组） |

**关键事实（实测）**
- 越权返回 **HTTP 200 + 业务码 403**，只断 HTTP 状态码的用例毫无防护力
- 内置 `ry` 不能测越权：它的角色被分配了大量菜单，实测全部 200
- `/test/user/list` 返回结构是 `{code,data,msg}`，没有 `total`/`rows`，且**明文返回 password**
- 角色被用户引用时删不掉（「xx已分配,不能删除」），cleanup 必须先删用户

**权限机制**：`@PreAuthorize("@ss.hasPermi('system:user:list')")` → `PermissionService.hasPermi` → 看 `LoginUser.permissions` 集合（admin 是通配符 `*:*:*`）。菜单为空的角色 → 集合为空 → 直接 false → 403。`/test/user/list` 没有任何 `@PreAuthorize`，只要登录就 200。

**这次踩的坑（自己写代码时）**
1. 一个 fixture 只能有一个 `yield`，第二个起是语法性错误；`yield` 后的代码是 teardown
2. `client.request(...)["rows"]` 结果没赋给变量 → 下一行 `client[...]` 报 `'ApiClient' object is not subscriptable`（连踩 3 次）
3. `menuIds` 拼成 `meuIds` → 报 `Cannot read the array length because "<local4>" is null`，报错里看不到字段名
4. `roleIds: []` + `roleId: [x]` → 用户没绑上角色，用例会「假通过」（验证的是没角色的用户）
5. 列表接口顶层直接是 `rows`，详情接口才是 `data`
6. `def low_priv_token[:20]` —— 切片表达式当函数名，`SyntaxError` 会让整个测试文件收集失败（21→17 items）

**CI**：`b8daae9` 两层全绿（check + integration），README 用例表已更新为 23 条

**已收口（2026-11-17）**
- `简历表述.md` 升至 23 条版本：5 条 bullets、证据表加 2 行、新增第 11/12 题（越权设计、为什么不是 HTTP 403）
- Obsidian 新增节点 `认证与授权`（工程 / 安全）、`越权测试`（测试 / 接口自动化），原文存档 `2026-11-17_对话_越权测试实战`，节点 18→20，零断链

**待办**
- conftest.py 里硬编码的 `test123456`，应挪到 `config.py` 走环境变量
- 可加一条用例：造 `roleKey="admin"` 的角色，验证它不会拿到超级管理员权限（判断走 `userId==1`，不是 roleKey）
- 参数边界 / 幂等 / 并发 / 分页边界 / 跨接口链路 五个维度还没覆盖

**面试口述已过关**
- 对照组的作用：403 只证明"这接口被拒"，对照 200 才证明"账号可用但没权限"，从而排除账号状态异常、全局异常兜底、环境异常三种解释

## 2026-11-18 · 参数边界维度（26 passed）

**成果**：`test_param_boundary.py` 3 条，全部 26 条用例 1.7s 通过，跑两遍零残留。提交 `1bf665a`。

| 用例 | 输入 | 期望 |
|---|---|---|
| 缺 roleName | 其余字段齐全 | code 500「角色名称不能为空」 |
| 超长 | roleName = `"a" * 31` | code 500「长度不能超过30个字符」 |
| 边界下沿 | roleName 恰好 30 字符 | code 200 + 回查 len==30 |

**实测的分页参数缺陷（待写成 xfail）**

| 输入 | 实际 |
|---|---|
| `pageNum=abc` | code 200，返回全量（类型错误被静默忽略） |
| `pageNum=-1` | code 200，返回全量 |
| `pageSize=100000` | code 200，无上限 |
| `pageSize=0` | code 200，total=2 但 rows=0 |
| `userName=' OR 1=1 --` | code 200，total=0（无注入，走 #{} 参数化） |

**重要发现：报错文案可能是非确定的。** 同一请求（roleName 与 roleKey 同时缺失）连发 12 次，5 次返回「角色名称不能为空」、7 次返回「权限字符不能为空」——若依只取第一条违反信息，Hibernate Validator 的违反集合顺序不保证。修法不是放宽断言，而是**让失败原因唯一**（补齐其余字段）。

**今天踩的坑**
1. 字段名 `roleCode` 拼错（应是 `roleKey`），Jackson 静默忽略未知字段，导致用例实际测的是「缺 roleKey」而不是「超长」
2. 用 `f"qa_guest_{uuid4().hex[:31]}"` 造长度，实际 40 字符——边界值必须用 `"a" * 31` 精确控制
3. 断言文案写成「不能超过31个字符」，实际是 `@Size(max=30)` 的「不能超过30个字符」
4. 只加 `request` 参数、没定义 cleanup、没调 `addfinalizer` —— 用例绿但每次留垃圾数据（124、128、132、136 四条都是我手动清的）
5. 忘记传 `params` 过滤 → `len(rows)==1` 断言拿全表 4 条

**下次继续**
- 补写 2 条 xfail：`pageNum=abc`、`pageNum=-1` 应被拒绝（`strict=True`），目标 `26 passed, 2 xfailed`
- 之后：`pageSize=100000` 无上限、`pageSize=0` 契约不一致
