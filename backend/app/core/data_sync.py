"""
官方数据自动同步模块
启动时自动将 sql/data/ 目录下的 SQL 文件执行到数据库
使用 INSERT IGNORE 避免重复插入，确保幂等
"""
import os
import logging
from sqlalchemy import text
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

# 数据文件目录（Docker 容器内路径）
DATA_DIR = "/app/sql/data"


def sync_official_data():
    """同步官方数据到数据库（INSERT IGNORE，幂等安全）"""
    if not os.path.isdir(DATA_DIR):
        logger.info(f"数据目录不存在，跳过数据同步: {DATA_DIR}")
        return

    sql_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith('.sql'))
    if not sql_files:
        logger.info("无数据文件，跳过数据同步")
        return

    db = SessionLocal()
    try:
        for filename in sql_files:
            filepath = os.path.join(DATA_DIR, filename)
            logger.info(f"同步数据文件: {filename}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 将 INSERT INTO 替换为 INSERT IGNORE INTO（避免重复插入报错）
            content = content.replace('INSERT INTO', 'INSERT IGNORE INTO')

            # 逐条执行
            statements = [s.strip() for s in content.split(';') if s.strip()]
            for stmt in statements:
                try:
                    db.execute(text(stmt))
                except Exception as e:
                    logger.warning(f"执行语句失败（已跳过）: {e}")

        db.commit()
        logger.info(f"官方数据同步完成，共处理 {len(sql_files)} 个文件")
    except Exception as e:
        db.rollback()
        logger.error(f"数据同步失败: {e}")
    finally:
        db.close()
