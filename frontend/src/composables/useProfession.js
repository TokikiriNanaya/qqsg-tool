/**
 * 副职类型相关工具函数
 * 注意：副职类型数据来自字典接口 /api/dict/job_type，不要硬编码
 */

// 副职类型对应的 Element Plus tag 颜色（根据 code 哈希）
export function getProfessionType(type) {
  const colorMap = ['', 'success', 'primary', 'warning', 'danger']
  if (!type) return 'default'
  return colorMap[Math.abs(type) % colorMap.length] || 'info'
}

// 副职等级（默认21级）
export const PROFESSION_LEVEL = 21

// 幸运合成率计算：幸运概率 + (副职增益 × 副职等级)
export function calcLuckyRate(recipe, level = PROFESSION_LEVEL) {
  const base = (recipe.lucky_probability || 0) / 100
  const bonus = ((recipe.profession_level_bonus || 0) / 100) * level
  return base + bonus
}
