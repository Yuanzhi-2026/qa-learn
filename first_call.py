import requests

r = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=10)
print(r.status_code)
print(r.json()["title"])
assert r.status_code == 200
