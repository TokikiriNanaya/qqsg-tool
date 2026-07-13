"""
对外分享/搜索 API 模块
供其他项目（如 QQ 机器人）调用，使用 GET 请求，参数固定为 keyword
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.pinyin import match_pinyin
from app.core.config import settings
from app.models import Recipe, Item, Tag, User, UserRole
from app.api.auth import get_current_user_optional
from app.api.recipes import add_material_names, add_profession_type_label, get_profession_type_map

router = APIRouter(prefix="/share", tags=["对外分享"])


# ========== 响应模型 ==========

class ShareRecipeItem(BaseModel):
    """分享搜索结果中的配方条目"""
    id: int
    name: str
    match_type: str  # "exact" 完全匹配 或 "partial" 部分匹配
    detail_text: str  # 配方详情文本
    detail_url: str   # 详情页链接


class ShareItemEntry(BaseModel):
    """分享搜索结果中的物品条目"""
    id: int
    name: str
    match_type: str
    detail_text: str
    detail_url: str


class ShareSearchResponse(BaseModel):
    """搜索响应"""
    keyword: str
    recipes: list[ShareRecipeItem] = []
    items: list[ShareItemEntry] = []
    total_count: int = 0


# ========== 工具函数 ==========

def format_recipe_detail(recipe_dict: dict) -> str:
    """将配方详情格式化为文本"""
    lines = [f"【{recipe_dict.get('name', '')}】"]

    # 副职和等级
    prof_label = recipe_dict.get('profession_type_label', '未知')
    level = recipe_dict.get('level_required', 0)
    lines.append(f"副职: {prof_label} Lv.{level}")

    # 材料
    materials = []
    for idx in [1, 2, 3]:
        mat_name = recipe_dict.get(f'material{idx}_name', '')
        mat_qty = recipe_dict.get(f'material{idx}_quantity', 0)
        if mat_name and mat_qty > 0:
            materials.append(f"{mat_name}×{mat_qty}")
    if materials:
        lines.append(f"材料: {' + '.join(materials)}")

    # 产出
    result_name = recipe_dict.get('result_item_name', '')
    result_qty = recipe_dict.get('result_quantity', 1)
    lines.append(f"产出: {result_name}×{result_qty}")

    # 幸运产出
    lucky_name = recipe_dict.get('lucky_result_item_name', '')
    lucky_qty = recipe_dict.get('lucky_result_quantity', 0)
    if lucky_name and lucky_qty > 0:
        lines.append(f"幸运产出: {lucky_name}×{lucky_qty}")

    # 幸运概率
    lucky_prob = recipe_dict.get('lucky_probability', 0)
    if lucky_prob > 0:
        lines.append(f"幸运概率: {lucky_prob / 100:.1f}%")

    # 活力消耗
    vitality = recipe_dict.get('vitality_cost', 0)
    if vitality > 0:
        lines.append(f"消耗活力: {vitality}")

    # 描述
    desc = recipe_dict.get('description', '')
    if desc:
        lines.append(f"描述: {desc}")

    return "\n".join(lines)


def format_item_detail(item) -> str:
    """将物品详情格式化为文本"""
    lines = [f"【{item.name}】"]

    if item.category:
        lines.append(f"分类: {item.category}")

    if item.description:
        lines.append(f"描述: {item.description}")

    if item.default_price is not None:
        lines.append(f"默认价格: {item.default_price} 三国币")

    if item.bag_limit:
        lines.append(f"背包上限: {item.bag_limit}")

    if item.warehouse_limit:
        lines.append(f"仓库上限: {item.warehouse_limit}")

    return "\n".join(lines)


# ========== 接口 ==========

@router.get("/search", response_model=ShareSearchResponse)
def share_search(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    base_url: str = Query("", description="前端基础URL，用于拼接详情链接"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    对外搜索接口

    搜索逻辑：
    1. 优先在配方中搜索 keyword
    2. 其次在物品中搜索 keyword
    3. 完全匹配的结果优先排在前面
    4. 返回文本详情 + 详情页链接
    """
    result = ShareSearchResponse(keyword=keyword)
    profession_map = get_profession_type_map(db)

    # 前端地址，从请求参数获取，去掉末尾斜杠
    base_url = base_url.rstrip('/')

    # ========== 第一步：搜索配方 ==========
    all_recipes = db.query(Recipe)

    # 非管理员过滤禁用配方
    if not current_user or current_user.role != UserRole.ADMIN:
        all_recipes = all_recipes.filter(Recipe.is_ban != 1)

    all_recipes = all_recipes.all()

    recipe_exact_matches = []
    recipe_partial_matches = []

    for recipe in all_recipes:
        if match_pinyin(recipe.name, keyword):
            recipe_dict = add_material_names(
                add_profession_type_label(recipe, profession_map), db
            )
            if recipe.name == keyword:
                recipe_exact_matches.append(recipe_dict)
            else:
                recipe_partial_matches.append(recipe_dict)

    # 先精确匹配，再部分匹配
    sorted_recipes = recipe_exact_matches + recipe_partial_matches

    for r in sorted_recipes:
        detail_text = format_recipe_detail(r)
        detail_url = f"{base_url}/recipes/{r['id']}"
        result.recipes.append(ShareRecipeItem(
            id=r['id'],
            name=r['name'],
            match_type="exact" if r in recipe_exact_matches else "partial",
            detail_text=detail_text,
            detail_url=detail_url,
        ))

    # ========== 第二步：搜索物品 ==========
    all_items = db.query(Item).all()

    item_exact_matches = []
    item_partial_matches = []

    for item in all_items:
        if match_pinyin(item.name, keyword):
            if item.name == keyword:
                item_exact_matches.append(item)
            else:
                item_partial_matches.append(item)

    sorted_items = item_exact_matches + item_partial_matches

    for item in sorted_items:
        detail_text = format_item_detail(item)
        detail_url = f"{base_url}/items/{item.id}" if base_url else f"/items/{item.id}"
        result.items.append(ShareItemEntry(
            id=item.id,
            name=item.name,
            match_type="exact" if item in item_exact_matches else "partial",
            detail_text=detail_text,
            detail_url=detail_url,
        ))

    result.total_count = len(result.recipes) + len(result.items)

    return result
