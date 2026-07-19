"""
数据库生命周期管理模块
- 首次启动：建表 + 导入初始数据 + 标记 Alembic 版本
- 后续启动：Alembic 迁移 + 数据同步
"""
import os
import logging
import subprocess
from sqlalchemy import text, inspect
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

# 数据文件目录
INIT_DIR = "/app/sql/init"
DATA_DIR = "/app/sql/data"


def _is_database_initialized(db) -> bool:
    """检测数据库是否已初始化（检查 users 表是否存在）"""
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    return "users" in tables


def _run_sql_file(db, filepath: str):
    """执行单个 SQL 文件"""
    logger.info(f"  执行: {os.path.basename(filepath)}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 跳过 SET 和 FOREIGN_KEY_CHECKS 等配置语句
    statements = []
    for stmt in content.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        upper = stmt.upper()
        if upper.startswith('SET ') or upper.startswith('SET FOREIGN_KEY_CHECKS'):
            continue
        statements.append(stmt)

    for stmt in statements:
        try:
            db.execute(text(stmt))
        except Exception as e:
            logger.warning(f"  语句跳过: {e}")

    db.commit()


def init_database():
    """首次初始化：建表"""
    if not os.path.isdir(INIT_DIR):
        logger.warning(f"初始化目录不存在: {INIT_DIR}")
        return

    sql_files = sorted(f for f in os.listdir(INIT_DIR) if f.endswith('.sql'))
    if not sql_files:
        logger.info("无初始化 SQL 文件")
        return

    db = SessionLocal()
    try:
        for filename in sql_files:
            _run_sql_file(db, os.path.join(INIT_DIR, filename))
        logger.info(f"数据库初始化完成，共执行 {len(sql_files)} 个文件")
    except Exception as e:
        db.rollback()
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()


def stamp_alembic_head():
    """标记当前数据库版本为 Alembic 最新版（首次初始化后使用）"""
    logger.info("标记 Alembic 版本为 head...")
    result = subprocess.run(
        ["python", "-m", "alembic", "stamp", "head"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        logger.warning(f"Alembic stamp 失败: {result.stderr}")
    else:
        logger.info("Alembic 版本标记完成")


def run_alembic_migration():
    """执行 Alembic 自动迁移（已有数据库时使用）"""
    logger.info("=== Alembic 自动迁移 ===")
    result = subprocess.run(
        ["python", "-m", "alembic", "revision", "--autogenerate", "-m", "auto_migration"],
        capture_output=True, text=True
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.warning(f"revision 警告: {result.stderr}")

    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        capture_output=True, text=True
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"upgrade 失败: {result.stderr}")
    else:
        logger.info("Alembic 迁移完成")


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


def bootstrap_database():
    """
    数据库启动流程（entrypoint 调用）：
    1. 检测数据库是否已初始化
    2. 未初始化 → 建表 + 标记 Alembic 版本 + 导入初始数据
    3. 已初始化 → Alembic 迁移 + 数据同步
    """
    db = SessionLocal()
    try:
        initialized = _is_database_initialized(db)
    finally:
        db.close()

    if not initialized:
        logger.info("=== 数据库未初始化，执行首次建表 ===")
        init_database()
        stamp_alembic_head()
        logger.info("=== 首次初始化完成，导入初始数据 ===")
        sync_official_data()
    else:
        logger.info("=== 数据库已初始化，执行增量迁移 ===")
        run_alembic_migration()
        logger.info("=== 同步最新数据 ===")
        sync_official_data()
