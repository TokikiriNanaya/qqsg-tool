from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import UserRole


# 标签相关Schema
class TagBase(BaseModel):
    name: str = Field(..., max_length=50)
    category: str = Field(..., max_length=50)
    value: Optional[int] = 0
    sort_order: Optional[int] = 0
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    value: Optional[int] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None


class TagResponse(TagBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 物品相关Schema
class ItemBase(BaseModel):
    id: int = Field(...)
    name: str = Field(..., max_length=100)
    category: Optional[str] = None
    description: Optional[str] = None
    default_price: Optional[int] = None
    bag_limit: Optional[int] = Field(99, ge=1)
    warehouse_limit: Optional[int] = Field(999, ge=1)


class ItemCreate(ItemBase):
    id: Optional[int] = None  # 创建时可选，数据库自增长


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    default_price: Optional[int] = None
    bag_limit: Optional[int] = None
    warehouse_limit: Optional[int] = None


class ItemResponse(ItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 用户相关Schema
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: Optional[UserRole] = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 登录相关Schema
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# 配方相关Schema - 对应 MixData.txt
class RecipeBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    level_required: int = 0
    
    # 材料ID
    material1_id: Optional[int] = 0
    material2_id: Optional[int] = 0
    material3_id: Optional[int] = 0
    
    # 材料数量
    material1_quantity: int = 0
    material2_quantity: int = 0
    material3_quantity: int = 0
    
    # 幸运合成
    lucky_probability: int = 0
    
    # 产出物品
    result_item_id: Optional[int] = 0
    result_quantity: int = 1
    
    # 幸运合成产出
    lucky_result_item_id: Optional[int] = 0
    lucky_result_quantity: int = 0
    
    # 其他字段
    unknown01: int = 0
    unknown02: int = 0
    profession_level_bonus: int = 0
    vitality_cost: int = 0
    unknown03: int = 0
    profession_type: int = 0
    unknown04: int = 0
    is_ban: int = 0


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level_required: Optional[int] = None
    material1_id: Optional[int] = None
    material2_id: Optional[int] = None
    material3_id: Optional[int] = None
    material1_quantity: Optional[int] = None
    material2_quantity: Optional[int] = None
    material3_quantity: Optional[int] = None
    lucky_probability: Optional[int] = None
    result_item_id: Optional[int] = None
    result_quantity: Optional[int] = None
    lucky_result_item_id: Optional[int] = None
    lucky_result_quantity: Optional[int] = None
    profession_level_bonus: Optional[int] = None
    vitality_cost: Optional[int] = None
    profession_type: Optional[int] = None
    is_ban: Optional[int] = None


class RecipeResponse(RecipeBase):
    id: int
    profession_type_label: Optional[str] = None
    material1_name: Optional[str] = None
    material2_name: Optional[str] = None
    material3_name: Optional[str] = None
    result_item_name: Optional[str] = None
    lucky_result_item_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True



# 通用响应Schema
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None