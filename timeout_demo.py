import time
import requests

t0 = time.time()
try:
    requests.get("https://httpbin.org/delay/10")
except Exception as e:
    print(type(e).__name__, "|", e)
print("耗时", round(time.time() - t0, 1), "秒")
