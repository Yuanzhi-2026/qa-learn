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


def show_detail(keyword):
    """打印某个接口的完整定义：参数在哪、要什么字段"""
    for path, ops in spec["paths"].items():
        if keyword not in path:
            continue
        for method, op in ops.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            print(f"\n{method.upper()} {path}   [{op.get('summary','')}]")
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

if detail and len(sys.argv) > 1:
    show_detail([a for a in sys.argv[1:] if not a.startswith("-")][0])
