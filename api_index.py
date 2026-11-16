"""把 /v3/api-docs 里的所有接口导出成清单。用法: python api_index.py [关键词]"""
import json, sys, urllib.request

SPEC = "http://127.0.0.1:8080/v3/api-docs"
kw = sys.argv[1].lower() if len(sys.argv) > 1 else ""
detail = "-d" in sys.argv

spec = json.loads(urllib.request.urlopen(SPEC, timeout=30).read().decode())
paths = spec.get("paths", {})

lines = []
for path in sorted(paths):
    for method, op in paths[path].items():
        if method not in ("get", "post", "put", "delete", "patch"):
            continue
        summary = (op.get("summary") or "").strip()
        lines.append(f"{method.upper():6s} {path:45s} {summary}")

if kw:
    lines = [l for l in lines if kw in l.lower()]

if not detail:
    print(f"共 {len(lines)} 个接口" + (f"（关键词: {kw}）" if kw else ""))
    for l in lines:
        print(" ", l)


METHODS = ("get", "post", "put", "delete", "patch")


def show_detail(keyword):
    """打印接口的完整定义：参数在哪、要什么字段。

    keyword 可以带方法名限定，例如 "post system/role"；
    只写路径片段就会把这个路径下的所有方法都打出来。
    """
    words = keyword.lower().split()
    method_filter = [w for w in words if w in METHODS]
    path_kw = " ".join(w for w in words if w not in METHODS)

    hit = 0
    for path, ops in spec["paths"].items():
        if path_kw and path_kw not in path:
            continue
        for method, op in ops.items():
            if method not in METHODS:
                continue
            if method_filter and method not in method_filter:
                continue
            hit += 1
            print(f"\n{method.upper()} {path}   [{op.get('summary', '')}]")
            if "parameters" in op:
                for prm in op["parameters"]:
                    loc = prm.get("in", "?")
                    name = prm.get("name")
                    ref = prm.get("schema", {}).get("$ref")
                    print(f"  参数 {name} 位置={loc} 必填={prm.get('required')}")
                    if ref:
                        cls = ref.split("/")[-1]
                        fields = spec["components"]["schemas"].get(cls, {}).get("properties", {})
                        print(f"  字段({cls}): " + ", ".join(fields.keys()))
            if "requestBody" in op:
                for ctype, body in op["requestBody"]["content"].items():
                    ref = body.get("schema", {}).get("$ref", "")
                    cls = ref.split("/")[-1]
                    fields = spec["components"]["schemas"].get(cls, {}).get("properties", {})
                    print(f"  请求体 Content-Type={ctype}")
                    print(f"  字段({cls}): " + ", ".join(fields.keys()))

    if hit == 0:
        print(f"没找到匹配「{keyword}」的接口。")
        print("  提示：若依是 RESTful 风格，新增是 POST 到集合路径（POST /system/role），没有 /add 后缀")
        print("  去掉 -d 先看完整列表，例如：python api_index.py system/role")


if detail and len(sys.argv) > 1:
    show_detail(" ".join(a for a in sys.argv[1:] if not a.startswith("-")))
