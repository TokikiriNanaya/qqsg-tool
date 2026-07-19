SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Table structure for item_tags
-- ----------------------------
CREATE TABLE `item_tags`  (
  `item_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`item_id`, `tag_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for items
-- ----------------------------
CREATE TABLE `items`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '游戏中的ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '物品名称',
  `category` int(11) NULL DEFAULT NULL COMMENT '物品分类',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '物品简介',
  `default_price` int(11) NULL DEFAULT NULL COMMENT '默认价格（三国币）',
  `juntuan_point` int(11) NULL DEFAULT NULL COMMENT '军团点',
  `bag_limit` int(11) NULL DEFAULT NULL COMMENT '背包携带上限',
  `warehouse_limit` int(11) NULL DEFAULT NULL COMMENT '仓库存放上限',
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18109 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for recipes
-- ----------------------------
CREATE TABLE `recipes`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '序号',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '简介',
  `level_required` int(11) NULL DEFAULT 0 COMMENT '制作所需等级',
  `material1_id` int(11) NULL DEFAULT 0 COMMENT '材料1的id',
  `material2_id` int(11) NULL DEFAULT 0 COMMENT '材料2的id',
  `material3_id` int(11) NULL DEFAULT 0 COMMENT '材料3的id',
  `material1_quantity` int(11) NULL DEFAULT 0 COMMENT '材料1的数量',
  `material2_quantity` int(11) NULL DEFAULT 0 COMMENT '材料2的数量',
  `material3_quantity` int(11) NULL DEFAULT 0 COMMENT '材料3的数量',
  `lucky_probability` int(11) NULL DEFAULT 0 COMMENT '幸运合成概率',
  `result_item_id` int(11) NOT NULL COMMENT '物品id',
  `result_quantity` int(11) NULL DEFAULT 1 COMMENT '产出数量',
  `lucky_result_item_id` int(11) NULL DEFAULT 0 COMMENT '幸运合成产出物品id',
  `lucky_result_quantity` int(11) NULL DEFAULT 0 COMMENT '幸运合成产出数量',
  `unknown01` int(11) NULL DEFAULT 0 COMMENT 'unknown01',
  `unknown02` int(11) NULL DEFAULT 0 COMMENT 'unknown02',
  `profession_level_bonus` int(11) NULL DEFAULT 0 COMMENT '副职等级增益',
  `vitality_cost` int(11) NULL DEFAULT 0 COMMENT '消耗活力',
  `unknown03` int(11) NULL DEFAULT 0 COMMENT 'unknown03',
  `profession_type` int(11) NULL DEFAULT 0 COMMENT '副职类型',
  `unknown04` int(11) NULL DEFAULT 0 COMMENT 'unknown04',
  `is_ban` int(11) NULL DEFAULT 0 COMMENT '是否禁用',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 564 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '配方表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_dict
-- ----------------------------
CREATE TABLE `sys_dict`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dict_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典分类标识（如：item_category、job_type）',
  `code` int(11) NOT NULL COMMENT '字典编码（业务唯一键）',
  `label` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典显示名称',
  `sort_order` int(11) NULL DEFAULT NULL COMMENT '排序号',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `status` smallint(6) NULL DEFAULT NULL COMMENT '状态（1=启用，0=禁用）',
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_dict_type_code`(`dict_type`, `code`) USING BTREE,
  INDEX `ix_sys_dict_id`(`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 33 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `hashed_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `role` enum('ADMIN','USER') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
