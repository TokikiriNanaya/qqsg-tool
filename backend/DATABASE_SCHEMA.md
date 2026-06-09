# 数据库表结构参考

## 📋 概述

本文档列出所有需要手动创建的数据库表及其字段定义。

**注意：** 
- 所有表使用 InnoDB 引擎
- 字符集使用 utf8mb4
- 外键约束根据实际需求决定是否添加

---

## 1. users (用户表)

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

## 2. tags (标签表)

```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '标签名称',
    category VARCHAR(50) NOT NULL COMMENT '标签分类',
    description TEXT COMMENT '标签描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签表';
```

---

## 3. item_tags (物品-标签关联表)

```sql
CREATE TABLE item_tags (
    item_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (item_id, tag_id),
    
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品-标签关联表';
```

---

## 4. items (物品表)

```sql
CREATE TABLE items (
    id INT PRIMARY KEY COMMENT '游戏内ID（原game_id）',
    name VARCHAR(100) NOT NULL COMMENT '物品名称',
    description TEXT COMMENT '物品简介',
    bag_limit INT DEFAULT 99 COMMENT '背包上限',
    warehouse_limit INT DEFAULT 999 COMMENT '仓库上限',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_game_id (game_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品表';
```

---

## 5. recipes (配方表)

对应 MixData.txt 的完整字段：

```sql
CREATE TABLE recipes (
    id INT PRIMARY KEY COMMENT '序号',
    name VARCHAR(200) NOT NULL COMMENT '名称',
    description TEXT COMMENT '简介',
    level_required INT DEFAULT 0 COMMENT '制作所需等级',
    
    -- 材料ID
    material1_id INT DEFAULT 0 COMMENT '材料1的id',
    material2_id INT DEFAULT 0 COMMENT '材料2的id',
    material3_id INT DEFAULT 0 COMMENT '材料3的id',
    
    -- 材料数量
    material1_quantity INT DEFAULT 0 COMMENT '材料1的数量',
    material2_quantity INT DEFAULT 0 COMMENT '材料2的数量',
    material3_quantity INT DEFAULT 0 COMMENT '材料3的数量',
    
    -- 幸运合成
    lucky_probability INT DEFAULT 0 COMMENT '幸运合成概率',
    
    -- 产出物品
    result_item_id INT NOT NULL COMMENT '物品id',
    result_quantity INT DEFAULT 1 COMMENT '产出数量',
    
    -- 幸运合成产出
    lucky_result_item_id INT DEFAULT 0 COMMENT '幸运合成产出物品id',
    lucky_result_quantity INT DEFAULT 0 COMMENT '幸运合成产出数量',
    
    -- 其他字段
    unknown01 INT DEFAULT 0 COMMENT 'unknown01',
    unknown02 INT DEFAULT 0 COMMENT 'unknown02',
    profession_level_bonus INT DEFAULT 0 COMMENT '副职等级增益',
    vitality_cost INT DEFAULT 0 COMMENT '消耗活力',
    unknown03 INT DEFAULT 0 COMMENT 'unknown03',
    profession_type INT DEFAULT 0 COMMENT '副职类型',
    unknown04 INT DEFAULT 0 COMMENT 'unknown04',
    unknown05 INT DEFAULT 0 COMMENT 'unknown05',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_level (level_required),
    INDEX idx_result_item (result_item_id),
    INDEX idx_profession_type (profession_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配方表';
```

---

## 🔧 快速创建所有表

可以将以上 SQL 语句保存为 `create_all_tables.sql`，然后执行：

```bash
mysql -u root -p qqsg < create_all_tables.sql
```

---

## 📝 字段说明

### recipes 表关键字段

| 字段组 | 说明 |
|--------|------|
| **基本信息** | id, name, description, level_required |
| **材料** | material1/2/3_id 和对应的 quantity |
| **产出** | result_item_id, result_quantity |
| **幸运合成** | lucky_probability, lucky_result_item_id, lucky_result_quantity |
| **副职信息** | profession_type (1=庖丁,2=工匠,3=巧匠,4=玉匠,5=书匠), vitality_cost |

### 副职类型映射

- 0: 未知
- 1: 庖丁（烹饪）
- 2: 工匠（制造工具）
- 3: 巧匠（制作饰品）
- 4: 玉匠（制作玉石）
- 5: 书匠（制作符咒）

---

## ⚠️ 注意事项

1. **外键约束**：可以根据性能需求选择是否添加外键
2. **索引优化**：根据查询频率调整索引
3. **字符集**：统一使用 utf8mb4 以支持 emoji
4. **自增主键**：recipes 表的 id 不使用自增，直接使用 MixData 中的序号

---

## 📞 参考

详细的模型定义请参考：`backend/app/models/__init__.py`
