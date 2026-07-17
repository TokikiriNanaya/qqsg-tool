from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Recipe, User, UserRole, Tag, Item
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from app.api.auth import get_current_user, get_current_user_optional
from app.core.pinyin import match_pinyin
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


def get_profession_type_map(db: Session):
    """获取副职类型标签映射（从数据库查询）"""
    tags = db.query(Tag).filter(Tag.category == "副职类型").all()
    return {tag.value: tag.name for tag in tags}


def add_profession_type_label(recipe, profession_map):
    """为配方添加副职类型标签名称"""
    recipe_dict = recipe.__dict__ if hasattr(recipe, '__dict__') else dict(recipe)
    profession_type = recipe.profession_type if hasattr(recipe, 'profession_type') else recipe.get('profession_type')
    recipe_dict['profession_type_label'] = profession_map.get(profession_type, "未知")
    return recipe_dict


def add_material_names(recipe, db: Session):
    """为配方添加材料名称及物品详细信息"""
    recipe_dict = recipe.__dict__ if hasattr(recipe, '__dict__') else dict(recipe)
    
    # 收集所有物品ID
    material_ids = [
        recipe_dict.get('material1_id', 0),
        recipe_dict.get('material2_id', 0),
        recipe_dict.get('material3_id', 0)
    ]
    result_item_id = recipe_dict.get('result_item_id', 0)
    lucky_item_id = recipe_dict.get('lucky_result_item_id', 0)
    
    all_item_ids = [i for i in material_ids + [result_item_id, lucky_item_id] if i and i > 0]
    
    # 获取物品ID到物品对象的映射
    items = db.query(Item).filter(Item.id.in_(all_item_ids)).all()
    item_map = {item.id: item for item in items}
    
    # 添加材料名称和详细信息
    for idx in [1, 2, 3]:
        mid = recipe_dict.get(f'material{idx}_id', 0)
        mat_item = item_map.get(mid)
        recipe_dict[f'material{idx}_name'] = mat_item.name if mat_item else ''
        recipe_dict[f'material{idx}_category'] = mat_item.category if mat_item else ''
        recipe_dict[f'material{idx}_description'] = mat_item.description if mat_item else ''
        recipe_dict[f'material{idx}_default_price'] = mat_item.default_price if mat_item else None
        recipe_dict[f'material{idx}_juntuan_point'] = mat_item.juntuan_point if mat_item else None
    
    # 添加产出物品名称和详细信息
    result_item = item_map.get(result_item_id)
    recipe_dict['result_item_name'] = result_item.name if result_item else ''
    recipe_dict['result_item_category'] = result_item.category if result_item else ''
    recipe_dict['result_item_description'] = result_item.description if result_item else ''
    recipe_dict['result_item_price'] = result_item.default_price if result_item else None
    recipe_dict['result_item_juntuan_point'] = result_item.juntuan_point if result_item else None
    recipe_dict['result_item_bag_limit'] = result_item.bag_limit if result_item else 999
    
    # 添加幸运合成物品名称
    lucky_item = item_map.get(lucky_item_id)
    recipe_dict['lucky_result_item_name'] = lucky_item.name if lucky_item else ''
    
    return recipe_dict


@router.get("/", response_model=RecipeListResponse)
def list_recipes(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    level_required: Optional[int] = None,
    profession_type: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取配方列表（所有用户可访问）"""
    query = db.query(Recipe)
    
    # 非管理员不能看到被禁用的配方
    if not current_user or current_user.role != UserRole.ADMIN:
        query = query.filter(Recipe.is_ban != 1)
    
    # 按等级筛选
    if level_required is not None:
        query = query.filter(Recipe.level_required == level_required)
    
    # 按副职类型筛选
    if profession_type is not None:
        query = query.filter(Recipe.profession_type == profession_type)
    
    # 按名称搜索（支持拼音首字母、全拼）
    if name:
        # 先用 SQL LIKE 粗筛中文名称
        candidates = query.filter(Recipe.name.like(f"%{name}%")).all()
        # 如果粗筛无结果，全量查询后用拼音匹配
        if not candidates:
            all_recipes = query.all()
            candidates = [r for r in all_recipes if match_pinyin(r.name, name)]
        
        total = len(candidates)
        # 内存分页
        paged = candidates[skip: skip + limit]
    else:
        total = query.count()
        paged = query.offset(skip).limit(limit).all()
    
    # 获取副职类型映射
    profession_map = get_profession_type_map(db)
    
    # 添加副职类型标签名称和材料名称
    recipes_with_label = [add_material_names(add_profession_type_label(r, profession_map), db) for r in paged]
    
    return {
        "total": total,
        "items": recipes_with_label
    }


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取单个配方详情（所有用户可访问）"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    # 非管理员不能看到被禁用的配方
    if recipe.is_ban == 1 and (not current_user or current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=404, detail="配方不存在")
    
    # 获取副职类型映射
    profession_map = get_profession_type_map(db)
    
    # 添加副职类型标签名称和材料名称
    recipe_dict = add_material_names(add_profession_type_label(recipe, profession_map), db)
    return recipe_dict


@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新配方（仅管理员）"""
    # 将 None 转为 0
    recipe_dict = recipe.dict()
    for key, value in recipe_dict.items():
        if value is None:
            recipe_dict[key] = 0
    
    # 移除 id，让数据库自动生成
    recipe_dict.pop('id', None)
    
    # 创建配方
    db_recipe = Recipe(**recipe_dict)
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
    
    # 更新基本字段，将 None 转为 0
    update_data = recipe.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is None:
            value = 0
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


# 添加一个响应模型用于物品配方树
class ItemRecipeTreeResponse(BaseModel):
    recipes_by_material: List[RecipeResponse] = []  # 作为材料的配方
    recipes_as_result: List[RecipeResponse] = []  # 作为产物的配方


@router.get("/by-material/", response_model=RecipeListResponse)
def get_recipes_by_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """根据材料ID获取相关配方（所有用户可访问）"""
    # 查询使用该材料的配方
    query = db.query(Recipe).filter(
        (Recipe.material1_id == material_id) |
        (Recipe.material2_id == material_id) |
        (Recipe.material3_id == material_id)
    )
    
    # 非管理员不能看到被禁用的配方
    if not current_user or current_user.role != UserRole.ADMIN:
        query = query.filter(Recipe.is_ban != 1)
    
    recipes = query.all()
    
    # 获取副职类型映射
    profession_map = get_profession_type_map(db)
    
    # 添加副职类型标签名称和材料名称
    recipes_with_label = [add_material_names(add_profession_type_label(r, profession_map), db) for r in recipes]
    
    return {
        "total": len(recipes_with_label),
        "items": recipes_with_label
    }


@router.get("/item-tree/{item_id}")
def get_item_recipe_tree(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取物品的配方树（上下结构：制作配方 + 可制作配方）"""
    # 获取作为材料的配方（可制作配方）
    query_material = db.query(Recipe).filter(
        (Recipe.material1_id == item_id) |
        (Recipe.material2_id == item_id) |
        (Recipe.material3_id == item_id)
    )
    
    # 获取作为产物的配方（制作配方）
    query_result = db.query(Recipe).filter(
        Recipe.result_item_id == item_id
    )
    
    # 非管理员不能看到被禁用的配方
    if not current_user or current_user.role != UserRole.ADMIN:
        query_material = query_material.filter(Recipe.is_ban != 1)
        query_result = query_result.filter(Recipe.is_ban != 1)
    
    recipes_as_material = query_material.all()
    recipes_as_result = query_result.all()
    
    # 获取副职类型映射
    profession_map = get_profession_type_map(db)
    
    # 处理配方
    recipes_material_list = [add_material_names(add_profession_type_label(r, profession_map), db) for r in recipes_as_material]
    recipes_result_list = [add_material_names(add_profession_type_label(r, profession_map), db) for r in recipes_as_result]
    
    return {
        "recipes_by_material": recipes_material_list,
        "recipes_as_result": recipes_result_list
    }