from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, recipes, items, share, dict as dict_api
from app.core.dict_cache import dict_cache
from app.core.database import SessionLocal
from app.core.database import engine
from app.models import Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

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
    finally:
        db.close()


@app.get("/")
def read_root():
    return {
        "message": "欢迎使用QQ三国工具API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
