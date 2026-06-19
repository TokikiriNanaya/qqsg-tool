from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Item, Tag, User, UserRole, Recipe
from app.schemas import ItemCreate, ItemUpdate, ItemResponse, TagCreate, TagUpdate
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
        return {"total": total, "items": paged}
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}


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
    return item


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


@router.get("/tags/all")
def get_all_tags(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有标签（所有用户可访问）"""
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    
    # 先按分类排序，再按排序号排序
    query = query.order_by(Tag.category.asc(), Tag.sort_order.asc())
    
    total = query.count()
    tags = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": tags
    }


@router.get("/tags/{tag_id}")
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取单个标签详情（所有用户可访问）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.post("/tags/")
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新标签（仅管理员）"""
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )
    
    existing_value = db.query(Tag).filter(Tag.category == tag.category, Tag.value == tag.value).first()
    if existing_value and tag.value != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下已存在相同的值"
        )
    
    new_tag = Tag(
        name=tag.name,
        category=tag.category,
        value=tag.value or 0,
        sort_order=tag.sort_order or 0,
        description=tag.description
    )
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.put("/tags/{tag_id}")
def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新标签（仅管理员）"""
    existing = db.query(Tag).filter(Tag.id == tag_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    update_data = tag.dict(exclude_unset=True)
    
    if 'name' in update_data and update_data['name']:
        dup = db.query(Tag).filter(Tag.name == update_data['name'], Tag.id != tag_id).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )
    
    if 'value' in update_data and update_data['value'] is not None:
        category = update_data.get('category', existing.category)
        dup_val = db.query(Tag).filter(Tag.category == category, Tag.value == update_data['value'], Tag.id != tag_id).first()
        if dup_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类下已存在相同的值"
            )
    
    for key, value in update_data.items():
        if value is not None:
            setattr(existing, key, value)
    
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除标签（仅管理员）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    db.delete(tag)
    db.commit()
    return {"message": "标签删除成功"}