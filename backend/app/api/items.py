from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Item, Tag, User, UserRole
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/items", tags=["物品"])


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


@router.get("/", response_model=List[ItemResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    tag_id: int = None,
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
    
    items = query.offset(skip).limit(limit).all()
    return items


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
    # 检查物品ID是否已存在
    if db.query(Item).filter(Item.id == item.id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="物品ID已存在"
        )
    
    db_item = Item(**item.dict(exclude={'tag_ids'}))
    
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
    
    db.delete(db_item)
    db.commit()
    return {"message": "物品删除成功"}


@router.get("/tags/all")
def get_all_tags(db: Session = Depends(get_db)):
    """获取所有标签（所有用户可访问）"""
    tags = db.query(Tag).all()
    return tags


@router.post("/tags/")
def create_tag(
    tag_name: str,
    category: str,
    description: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新标签（仅管理员）"""
    # 检查标签是否已存在
    existing_tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )
    
    new_tag = Tag(
        name=tag_name,
        category=category,
        description=description
    )
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag
