/**
 * 副职类型相关工具函数
 */

// 副职类型对应的 Element Plus tag 类型
export function getProfessionType(type) {
  const typeMap = {
    1: 'success',   // 庖丁
    2: 'primary',   // 工匠
    3: 'warning',   // 巧匠
    4: 'danger',    // 玉匠
    5: 'info'       // 书匠
  }
  return typeMap[type] || 'default'
}

// 副职等级（默认21级）
export const PROFESSION_LEVEL = 21

// 幸运合成率计算：幸运概率 + (副职增益 × 副职等级)
export function calcLuckyRate(recipe, level = PROFESSION_LEVEL) {
  const base = (recipe.lucky_probability || 0) / 100
  const bonus = ((recipe.profession_level_bonus || 0) / 100) * level
  return base + bonus
}
