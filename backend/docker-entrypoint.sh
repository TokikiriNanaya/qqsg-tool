#!/bin/bash
set -e

echo "=== 等待数据库就绪 ==="
for i in $(seq 1 30); do
    if python -c "
import pymysql, os
try:
    url = os.environ.get('DATABASE_URL', '')
    parts = url.replace('mysql+pymysql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')
    conn = pymysql.connect(
        host=host_port[0],
        port=int(host_port[1]) if len(host_port) > 1 else 3306,
        user=user_pass[0],
        password=user_pass[1] if len(user_pass) > 1 else '',
        database=host_db[1].split('?')[0]
    )
    conn.close()
    print('OK')
except Exception as e:
    exit(1)
" 2>/dev/null; then
        echo "数据库已就绪"
        break
    fi
    echo "等待数据库... ($i/30)"
    sleep 2
done

echo "=== 数据库生命周期管理 ==="
python -c "from app.core.data_sync import bootstrap_database; bootstrap_database()"

echo "=== 启动应用 ==="
exec python run.py
