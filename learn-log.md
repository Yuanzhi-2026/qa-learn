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
