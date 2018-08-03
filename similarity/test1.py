import redis

if __name__ == '__main__':
    redissss = redis.Redis(db=5)
    redissss.delete('test')