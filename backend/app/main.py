import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api import auth, recipes, items, share, dict as dict_api
from app.core.dict_cache import dict_cache
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(share.router, prefix="/api")
app.include_router(dict_api.router, prefix="/api")

# 启动时预热字典缓存
@app.on_event("startup")
def startup_cache():
    db = SessionLocal()
    try:
        dict_cache.load_all(db)
        logger.info("字典缓存预热完成")
    except Exception as e:
        logger.warning(f"字典缓存预热失败（可能表未创建）: {e}")
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ============================================
# 静态文件服务（前端 SPA）
# ============================================
import os

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

if os.path.isdir(static_dir):
    # 挂载前端静态资源（JS/CSS/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        """前端 SPA 回退路由：非 /api/ 请求返回 index.html"""
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
