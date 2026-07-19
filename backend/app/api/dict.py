"""
通用字典 API
- GET  /api/dict/{dict_type}      获取指定类型的字典列表（公开）
- GET  /api/dict/                  获取所有字典（管理员，用于字典管理页面）
- POST /api/dict/                  创建字典项（管理员）
- PUT  /api/dict/{dict_id}         更新字典项（管理员）
- DELETE /api/dict/{dict_id}       删除字典项（管理员）
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.dict_cache import dict_cache
from app.models import SysDict, User, UserRole
from app.api.auth import get_current_user

router = APIRouter(prefix="/dict", tags=["字典"])


# ========== Pydantic Schemas ==========

class DictItemOut(BaseModel):
    """字典项响应（公开接口）"""
    code: int
    label: str
    sort_order: Optional[int] = 0

    class Config:
        from_attributes = True


class DictItemAdminOut(BaseModel):
    """字典项响应（管理后台，含完整字段）"""
    id: int
    dict_type: str
    code: int
    label: str
    sort_order: int
    remark: Optional[str] = None
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DictListAdminOut(BaseModel):
    total: int
    items: List[DictItemAdminOut]


class DictCreate(BaseModel):
    dict_type: str = Field(..., max_length=50, description="字典分类标识")
    code: int = Field(..., description="字典编码")
    label: str = Field(..., max_length=50, description="字典显示名称")
    sort_order: int = Field(0, description="排序号")
    remark: Optional[str] = None
    status: int = Field(1, description="状态（1=启用，0=禁用）")


class DictUpdate(BaseModel):
    dict_type: Optional[str] = None
    code: Optional[int] = None
    label: Optional[str] = None
    sort_order: Optional[int] = None
    remark: Optional[str] = None
    status: Optional[int] = None


# ========== 工具函数 ==========

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


# ========== 公开接口 ==========

@router.get("/{dict_type}", response_model=List[DictItemOut])
def get_dict_by_type(dict_type: str, db: Session = Depends(get_db)):
    """获取指定类型的字典列表（所有用户可访问，走缓存）"""
    items = dict_cache.get_dict_list(dict_type)
    if not items:
        # 缓存未命中，从数据库加载并更新缓存
        dict_cache.load_all(db)
        items = dict_cache.get_dict_list(dict_type)
    return items


# ========== 管理接口 ==========

@router.get("/", response_model=DictListAdminOut)
def list_all_dicts(
    skip: int = 0,
    limit: int = 100,
    dict_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """获取所有字典项（管理员，用于字典管理页面）"""
    query = db.query(SysDict)
    if dict_type:
        query = query.filter(SysDict.dict_type == dict_type)

    query = query.order_by(SysDict.dict_type.asc(), SysDict.sort_order.asc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.post("/", response_model=DictItemAdminOut)
def create_dict(
    item: DictCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """创建字典项（管理员）"""
    # 检查 dict_type + code 唯一性
    dup = db.query(SysDict).filter(
        SysDict.dict_type == item.dict_type,
        SysDict.code == item.code
    ).first()
    if dup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"字典类型 '{item.dict_type}' 下已存在编码 {item.code}"
        )

    new_item = SysDict(
        dict_type=item.dict_type,
        code=item.code,
        label=item.label,
        sort_order=item.sort_order,
        remark=item.remark,
        status=item.status,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    # 失效缓存
    dict_cache.invalidate(item.dict_type)
    return new_item


@router.put("/{dict_id}", response_model=DictItemAdminOut)
def update_dict(
    dict_id: int,
    item: DictUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """更新字典项（管理员）"""
    existing = db.query(SysDict).filter(SysDict.id == dict_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="字典项不存在")

    old_dict_type = existing.dict_type

    update_data = item.dict(exclude_unset=True)

    # 检查唯一性
    new_label = update_data.get('label', existing.label)
    new_dict_type = update_data.get('dict_type', existing.dict_type)
    new_code = update_data.get('code', existing.code)
    dup = db.query(SysDict).filter(
        SysDict.dict_type == new_dict_type,
        SysDict.code == new_code,
        SysDict.id != dict_id
    ).first()
    if dup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"字典类型 '{new_dict_type}' 下已存在编码 {new_code}"
        )

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    # 失效缓存（新旧 dict_type 都需要失效）
    dict_cache.invalidate(old_dict_type)
    if new_dict_type != old_dict_type:
        dict_cache.invalidate(new_dict_type)

    return existing


@router.delete("/{dict_id}")
def delete_dict(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """删除字典项（管理员）"""
    item = db.query(SysDict).filter(SysDict.id == dict_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")

    dict_type = item.dict_type
    db.delete(item)
    db.commit()
    dict_cache.invalidate(dict_type)
    return {"message": "字典项删除成功"}
