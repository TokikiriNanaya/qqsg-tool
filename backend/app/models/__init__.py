from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    category = Column(String(50), nullable=False, comment="标签分类（如：获取来源、用途、profession_type）")
    value = Column(Integer, default=0, comment="标签值（用于数字映射，如副职类型）")
    sort_order = Column(Integer, default=0, comment="排序号（用于控制显示顺序）")
    description = Column(Text, comment="标签描述")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系 - 多对多
    items = relationship("Item", secondary="item_tags", back_populates="tags")


# 物品-标签关联表（多对多）
item_tags = Table(
    'item_tags',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Item(Base):
    """物品模型"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, nullable=False, comment="游戏内ID")
    name = Column(String(100), nullable=False, comment="物品名称")
    description = Column(Text, comment="物品简介")
    bag_limit = Column(Integer, default=999, comment="背包携带上限")
    warehouse_limit = Column(Integer, default=9999, comment="仓库存放上限")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系 - 多对多
    tags = relationship("Tag", secondary=item_tags, back_populates="items")


class Recipe(Base):
    """配方模型 - 对应 MixData.txt 数据"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="序号")
    name = Column(String(200), nullable=False, comment="名称")
    description = Column(Text, comment="简介")
    level_required = Column(Integer, default=0, comment="制作所需等级")
    
    # 材料ID
    material1_id = Column(Integer, default=0, comment="材料1的id")
    material2_id = Column(Integer, default=0, comment="材料2的id")
    material3_id = Column(Integer, default=0, comment="材料3的id")
    
    # 材料数量
    material1_quantity = Column(Integer, default=0, comment="材料1的数量")
    material2_quantity = Column(Integer, default=0, comment="材料2的数量")
    material3_quantity = Column(Integer, default=0, comment="材料3的数量")
    
    # 幸运合成
    lucky_probability = Column(Integer, default=0, comment="幸运合成概率")
    
    # 产出物品
    result_item_id = Column(Integer, nullable=False, comment="物品id")
    result_quantity = Column(Integer, default=1, comment="产出数量")
    
    # 幸运合成产出
    lucky_result_item_id = Column(Integer, default=0, comment="幸运合成产出物品id")
    lucky_result_quantity = Column(Integer, default=0, comment="幸运合成产出数量")
    
    # 其他字段
    unknown01 = Column(Integer, default=0, comment="unknown01")
    unknown02 = Column(Integer, default=0, comment="unknown02")
    profession_level_bonus = Column(Integer, default=0, comment="副职等级增益")
    vitality_cost = Column(Integer, default=0, comment="消耗活力")
    unknown03 = Column(Integer, default=0, comment="unknown03")
    profession_type = Column(Integer, default=0, comment="副职类型")
    unknown04 = Column(Integer, default=0, comment="unknown04")
    is_ban = Column(Integer, default=0, comment="是否禁用（1=禁用）")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)