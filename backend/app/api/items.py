from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Item, Tag, User, UserRole, Recipe
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.api.auth import get_current_user

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
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取物品列表（所有用户可访问）"""
    query = db.query(Item)
    
    # 按名称搜索
    if name:
        query = query.filter(Item.name.like(f"%{name}%"))
    
    # 按标签筛选
    if tag_id:
        query = query.join(Item.tags).filter(Tag.id == tag_id)
    
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
        query = query.filter(Item.name.like(f"%{q}%"))
    
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
    item_data = item.dict(exclude={'tag_ids'})
    if item.id is None:
        item_data.pop('id', None)
    db_item = Item(**item_data)
    
    # 添加标签关联
    if item.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(item.tag_ids)).all()
        db_item.tags = tags
    
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
    update_data = item.dict(exclude_unset=True, exclude={'tag_ids'})
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    # 更新标签关联
    if item.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(item.tag_ids)).all()
        db_item.tags = tags
    
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
    
    # 按排序号排序
    query = query.order_by(Tag.sort_order.asc())
    
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
    name: str,
    category: str,
    value: int = 0,
    sort_order: int = 0,
    description: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新标签（仅管理员）"""
    existing_tag = db.query(Tag).filter(Tag.name == name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )
    
    existing_value = db.query(Tag).filter(Tag.category == category, Tag.value == value).first()
    if existing_value and value != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下已存在相同的值"
        )
    
    new_tag = Tag(
        name=name,
        category=category,
        value=value,
        sort_order=sort_order,
        description=description
    )
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.put("/tags/{tag_id}")
def update_tag(
    tag_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    value: Optional[int] = None,
    sort_order: Optional[int] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新标签（仅管理员）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    if name:
        existing_tag = db.query(Tag).filter(Tag.name == name, Tag.id != tag_id).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )
        tag.name = name
    
    if category:
        tag.category = category
    
    if value is not None:
        existing_value = db.query(Tag).filter(Tag.category == tag.category, Tag.value == value, Tag.id != tag_id).first()
        if existing_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类下已存在相同的值"
            )
        tag.value = value
    
    if sort_order is not None:
        tag.sort_order = sort_order
    
    if description is not None:
        tag.description = description
    
    db.commit()
    db.refresh(tag)
    return tag


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