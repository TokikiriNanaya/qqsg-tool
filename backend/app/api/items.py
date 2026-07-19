from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dict_cache import dict_cache
from app.models import Item, User, UserRole, Recipe
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.api.auth import get_current_user
from app.core.pinyin import match_pinyin

router = APIRouter(prefix="/items", tags=["物品"])


# 物品列表响应模型
class ItemListResponse(BaseModel):
    total: int
    items: List[ItemResponse]


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


def get_item_category_map():
    """获取物品分类映射（code -> label），从缓存获取"""
    return dict_cache.get_code_label_map("item_category")


def add_item_category_label(item, category_map):
    """为物品添加分类名称"""
    item_dict = item.__dict__ if hasattr(item, '__dict__') else dict(item)
    category_val = item.category if hasattr(item, 'category') else item.get('category')
    item_dict['category_label'] = category_map.get(category_val, str(category_val) if category_val else '')
    return item_dict


@router.get("/", response_model=ItemListResponse)
def list_items(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取物品列表（所有用户可访问）"""
    query = db.query(Item)
    
    # 按名称搜索（支持拼音首字母、全拼）
    if name:
        # 先用 SQL LIKE 粗筛中文名称
        candidates = query.filter(Item.name.like(f"%{name}%")).all()
        # 如果粗筛无结果，全量查询后用拼音匹配
        if not candidates:
            all_items = query.all()
            candidates = [item for item in all_items if match_pinyin(item.name, name)]
        
        total = len(candidates)
        # 内存分页
        paged = candidates[skip: skip + limit]
    else:
        total = query.count()
        paged = query.offset(skip).limit(limit).all()
    
    # 获取物品分类标签映射，添加分类名称
    category_map = get_item_category_map()
    items_with_label = [add_item_category_label(item, category_map) for item in paged]
    
    return {"total": total, "items": items_with_label}


@router.get("/search")
def search_items(
    q: str = "",
    limit: int = None,
    db: Session = Depends(get_db)
):
    """搜索物品（所有用户可访问）"""
    query = db.query(Item)
    
    if q:
        # 先用 SQL LIKE 粗筛中文名称
        candidates = query.filter(Item.name.like(f"%{q}%")).all()
        # 如果粗筛无结果，全量查询后用拼音匹配
        if not candidates:
            all_items = query.all()
            candidates = [item for item in all_items if match_pinyin(item.name, q)]
        # 同时补上拼音匹配命中的（粗筛可能漏掉拼音命中的）
        else:
            like_ids = {item.id for item in candidates}
            all_items = query.all()
            for item in all_items:
                if item.id not in like_ids and match_pinyin(item.name, q):
                    candidates.append(item)
    
        if limit is not None:
            items = candidates[:limit]
        else:
            items = candidates
    else:
        if limit is not None:
            items = query.limit(limit).all()
        else:
            items = query.all()
    return [{"id": item.id, "name": item.name} for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """获取单个物品详情（所有用户可访问）"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    category_map = get_item_category_map()
    return add_item_category_label(item, category_map)


@router.post("/", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新物品（仅管理员）"""
    # 如果传入了ID，检查是否已存在
    if item.id is not None:
        if db.query(Item).filter(Item.id == item.id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="物品ID已存在"
            )
    
    # 创建物品（不传id时由数据库自增长）
    item_data = item.dict()
    if item.id is None:
        item_data.pop('id', None)
    db_item = Item(**item_data)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新物品（仅管理员）"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    # 更新基本字段
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除物品（仅管理员）"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    # 检查该物品是否被用作配方的材料或产出
    recipes_using_item = db.query(Recipe).filter(
        (Recipe.material1_id == item_id) |
        (Recipe.material2_id == item_id) |
        (Recipe.material3_id == item_id) |
        (Recipe.result_item_id == item_id) |
        (Recipe.lucky_result_item_id == item_id)
    ).all()
    
    if recipes_using_item:
        recipe_names = [recipe.name for recipe in recipes_using_item]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法删除物品，该物品正在被以下配方使用：{', '.join(recipe_names)}"
        )
    
    db.delete(db_item)
    db.commit()
    return {"message": "物品删除成功"}


