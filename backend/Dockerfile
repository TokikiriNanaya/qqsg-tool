FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

# 安装系统依赖（mysqlclient 需要 gcc 和 libmariadb-dev）
# 替换为清华 apt 镜像源，避免构建时卡住
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 启动脚本（含数据库初始化/迁移/数据同步）
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 9940

# 启动命令
ENTRYPOINT ["/docker-entrypoint.sh"]
