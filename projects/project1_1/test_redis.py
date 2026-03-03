import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
    r.ping()
    print("✅ Redis 连接成功！")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
