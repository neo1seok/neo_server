import redis

# Redis 서버에 연결 (기본 설정: 로컬호스트, 포트 6379)
r = redis.Redis(host='192.168.0.17', port=6379, db=0)

# 데이터 입력
r.set('my_key', 'my_value')

# 데이터 조회
value = r.get('my_key')
print(value)  # b'my_value' 출력

# 데이터 만료 시간 설정 (예: 10초 후에 만료)
r.set('temporary_key', 'temporary_value', ex=10)
