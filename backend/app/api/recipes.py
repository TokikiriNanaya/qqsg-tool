from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Recipe, User, UserRole
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from app.api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/recipes", tags=["配方"])


# 配方列表响应模型
class RecipeListResponse(BaseModel):
    total: int
    items: List[RecipeResponse]


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="账户已被禁用")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


@router.get("/", response_model=RecipeListResponse)
def list_recipes(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    level_required: Optional[int] = None,
    profession_type: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取配方列表（所有用户可访问）"""
    query = db.query(Recipe)
    
    # 按名称搜索
    if name:
        query = query.filter(Recipe.name.like(f"%{name}%"))
    
    # 按等级筛选
    if level_required is not None:
        query = query.filter(Recipe.level_required == level_required)
    
    # 按副职类型筛选
    if profession_type is not None:
        query = query.filter(Recipe.profession_type == profession_type)
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    recipes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": recipes
    }


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """获取单个配方详情（所有用户可访问）"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    return recipe


@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新配方（仅管理员）"""
    # 检查ID是否已存在
    existing = db.query(Recipe).filter(Recipe.id == recipe.result_item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该配方ID已存在")
    
    # 创建配方
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新配方（仅管理员）"""
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    # 更新基本字段
    update_data = recipe.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除配方（仅管理员）"""
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    db.delete(db_recipe)
    db.commit()
    return {"message": "配方删除成功"}
