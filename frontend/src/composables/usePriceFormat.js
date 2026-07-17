/**
 * 价格格式化工具
 * 规则：
 * - 都为空或0 → 不展示价格
 * - 仅有三国币 → "100三国币"
 * - 仅有军团点 → "100军团点*0.2=20三国币"
 * - 两者都有 → "100三国币+100军团点*0.2=120三国币"
 */

/**
 * 格式化价格文本
 * @param {number|null|undefined} defaultPrice - 三国币价格
 * @param {number|null|undefined} juntuanPoint - 军团点
 * @returns {string} 格式化后的价格文本，为空时返回空字符串
 */
export function formatPrice(defaultPrice, juntuanPoint) {
  const dp = defaultPrice || 0
  const jp = juntuanPoint || 0

  if (dp === 0 && jp === 0) return ''

  const jpValue = jp * 0.2
  const total = dp + jpValue

  if (dp > 0 && jp > 0) {
    return `${dp}+${jp}*0.2=${total.toFixed(0)}`
  } else if (dp > 0) {
    return `${dp}`
  } else {
    return `${jp}*0.2=${jpValue.toFixed(0)}`
  }
}

/**
 * 判断是否有价格需要展示
 * @param {number|null|undefined} defaultPrice
 * @param {number|null|undefined} juntuanPoint
 * @returns {boolean}
 */
export function hasPrice(defaultPrice, juntuanPoint) {
  return !!(defaultPrice || juntuanPoint)
}
