/**
 * 将配方数据转换为 Vue Flow 的 nodes + edges 格式
 *
 * 布局：物品节点 + 配方节点，smoothstep 阶梯连接
 * 配方节点用不同颜色区分（橙色=材料→配方，绿色=配方→产物）
 *
 * 多配方时每个配方独立一行，垂直展开
 */

import { MarkerType } from '@vue-flow/core'

const H_GAP = 220       // 材料节点之间的水平间距
const COL_WIDTH = 700  // 每个配方列的宽度（容纳最多3个材料）
const V_GAP = 180      // 垂直间距（每层之间）

let nodeIdCounter = 0

function resetCounter() {
  nodeIdCounter = 0
}

function itemNodeKey(itemId, suffix = '') {
  return `item_${itemId}${suffix}`
}

function recipeNodeKey(recipeId, suffix = '') {
  return `recipe_${recipeId}${suffix}`
}

function makeMarker(color) {
  return {
    type: MarkerType.ArrowClosed,
    width: 14,
    height: 14,
    color
  }
}

/**
 * 构建单个配方的 flow 数据（配方详情页使用）
 *
 * 布局:
 *     [鸡蛋] [井水]           ← 材料物品 (y=-400)
 *        │     │
 *     [煮鸡蛋 Lv.1]           ← 配方节点 (y=-200)
 *         │
 *       [真纯]                ← 产物物品 (y=0)
 *         │
 *       [物品A]               ← 可制作物品 (y=200)
 *
 * @param {Object} recipe - 配方数据
 * @param {Array} asMaterialRecipes - 产物作为材料的配方列表
 * @returns {{ nodes: Array, edges: Array }}
 */
export function buildSingleRecipeFlow(recipe, asMaterialRecipes = null) {
  resetCounter()
  const nodes = []
  const edges = []
  const placedNodeIds = new Set()

  function addNode(node) {
    if (!placedNodeIds.has(node.id)) {
      placedNodeIds.add(node.id)
      nodes.push(node)
    }
  }

  function addEdge(edge) {
    if (!edges.find(e => e.id === edge.id)) {
      edges.push(edge)
    }
  }

  if (!recipe) return { nodes, edges }

  const recipeSummary = buildRecipeSummary(recipe)
  const materials = extractMaterials(recipe)
  const resultItemId = Number(recipe.result_item_id) || 0

  // ===== 第1层：材料物品节点 (y = -2 * V_GAP)，固定3个位置 =====
  const matPositions = []
  if (materials.length === 1) {
    matPositions.push(0)
  } else if (materials.length === 2) {
    matPositions.push(-0.5, 0.5)
  } else {
    matPositions.push(-1, 0, 1)
  }

  materials.forEach((mat, idx) => {
    const matNodeId = itemNodeKey(mat.id)
    addNode({
      id: matNodeId,
      type: 'item',
      position: { x: matPositions[idx] * H_GAP, y: -2 * V_GAP },
      data: {
        label: mat.name || `物品${mat.id}`,
        item_id: mat.id,
        quantity: mat.qty,
        category: mat.category || '',
        description: mat.description || '',
        default_price: mat.default_price ?? null,
        asMaterialRecipes: [recipeSummary],
        nodeType: 'material'
      }
    })
  })

  // ===== 第2层：配方节点 (y = -V_GAP) =====
  const recipeNodeId = recipeNodeKey(recipe.id)
  addNode({
    id: recipeNodeId,
    type: 'recipe',
    position: { x: 0, y: -V_GAP },
    data: { recipe: recipeSummary }
  })

  // ===== 第3层：产物物品节点 (y = 0) =====
  let resultNodeId = null
  if (resultItemId > 0) {
    resultNodeId = itemNodeKey(resultItemId)
    addNode({
      id: resultNodeId,
      type: 'item',
      position: { x: 0, y: 0 },
      data: {
        label: recipe.result_item_name || `物品${resultItemId}`,
        item_id: resultItemId,
        quantity: recipe.result_quantity,
        category: recipe.result_item_category || '',
        description: recipe.result_item_description || '',
        default_price: recipe.result_item_price ?? null,
        asResultRecipes: [recipeSummary],
        nodeType: 'root'
      }
    })
  }

  // 材料 → 配方（实线）
  materials.forEach((mat, idx) => {
    const matNodeId = itemNodeKey(mat.id)
    addEdge({
      id: `e_m_${matNodeId}_r_${recipeNodeId}`,
      source: matNodeId,
      target: recipeNodeId,
      type: 'smoothstep',
      data: { direction: 'upstream' },
      markerEnd: makeMarker('#e6a23c'),
      pathOptions: { borderRadius: 8, offset: 30 }
    })
  })

  // 配方 → 产物（实线）
  if (resultNodeId) {
    addEdge({
      id: `e_r_${recipeNodeId}_p_${resultNodeId}`,
      source: recipeNodeId,
      target: resultNodeId,
      type: 'smoothstep',
      data: { direction: 'upstream' },
      markerEnd: makeMarker('#e6a23c'),
      pathOptions: { borderRadius: 8, offset: 30 }
    })
  }

  // ===== 可制作物品 (y = V_GAP) =====
  if (asMaterialRecipes && asMaterialRecipes.length > 0) {
    const allResults = []
    asMaterialRecipes.forEach((mr) => {
      const ms = buildRecipeSummary(mr)
      const rid = Number(mr.result_item_id) || 0
      if (rid > 0) {
        allResults.push({ id: rid, name: mr.result_item_name, qty: mr.result_quantity, recipeSummary: ms })
      }
    })

    // 去重
    const unique = []
    const seen = new Set()
    allResults.forEach(r => { if (!seen.has(r.id)) { seen.add(r.id); unique.push(r) } })

    unique.forEach((res, ri) => {
      const rnId = itemNodeKey(res.id)
      const xOff = unique.length === 1 ? 0 : (ri - (unique.length - 1) / 2) * COL_WIDTH
      addNode({
        id: rnId,
        type: 'item',
        position: { x: xOff, y: V_GAP },
        data: {
          label: res.name || `物品${res.id}`,
          item_id: res.id,
          quantity: res.qty,
          default_price: res.default_price ?? null,
          asResultRecipes: [res.recipeSummary],
          nodeType: 'product'
        }
      })
    })

    allResults.forEach(res => {
      addEdge({
        id: `e_p_${resultNodeId}_d_${itemNodeKey(res.id)}_${res.recipeSummary.id}`,
        source: resultNodeId,
        target: itemNodeKey(res.id),
        type: 'smoothstep',
        data: { direction: 'downstream' },
        markerEnd: makeMarker('#67c23a'),
        pathOptions: { borderRadius: 8, offset: 30 }
      })
    })
  }

  return { nodes, edges }
}

/**
 * 构建物品的完整配方树 flow 数据（物品详情页使用）
 *
 * 多配方时每个配方独立一行，垂直展开
 *
 * 上半部分（制作配方）：
 *   [鸡蛋] [井水]          [鸡蛋]        ← 材料 (y=-400)
 *      │     │               │
 *   [煮鸡蛋 Lv.1]    [增产法 Lv.4]       ← 配方 (y=-200)
 *      │                    │
 *      └────────┬───────────┘
 *               │
 *            [真纯]                       ← 中心 (y=0)
 *               │
 *      ┌────────┴───────────┐
 *      │                    │
 *   [物品A]              [物品B]          ← 产物 (y=200)
 *
 * @param {Object} treeData - { recipesAsResult, recipesByMaterial }
 * @param {Object} currentItem - 当前物品信息
 * @returns {{ nodes: Array, edges: Array }}
 */
export function buildItemRecipeFlow(treeData, currentItem) {
  resetCounter()
  const nodes = []
  const edges = []
  const placedNodeIds = new Set()

  function addNode(node) {
    if (!placedNodeIds.has(node.id)) {
      placedNodeIds.add(node.id)
      nodes.push(node)
    }
  }

  function addEdge(edge) {
    if (!edges.find(e => e.id === edge.id)) {
      edges.push(edge)
    }
  }

  if (!treeData) return { nodes, edges }

  const recipesAsResult = treeData.recipesAsResult || treeData.recipes_as_result || treeData.as_result || []
  const recipesByMaterial = treeData.recipesByMaterial || treeData.recipes_by_material || treeData.as_material || []

  console.log('[buildItemRecipeFlow] item:', currentItem?.id, currentItem?.name,
    'as_result:', recipesAsResult.length, 'as_material:', recipesByMaterial.length)

  // ===== 中心物品节点 (y=0) =====
  const centerId = itemNodeKey(currentItem.id)
  addNode({
    id: centerId,
    type: 'item',
    position: { x: 0, y: 0 },
    data: {
      label: currentItem.name || `物品${currentItem.id}`,
      item_id: currentItem.id,
      category: currentItem.category || '',
      description: currentItem.description || '',
      default_price: currentItem.default_price ?? null,
      nodeType: 'root'
    }
  })

  // ===== 上半部分：制作配方 =====
  // 每个配方占一列，垂直方向：材料(y=-2V) → 配方(y=-V) → 中心(y=0)
  // 材料固定3个位置（居中排列），配方节点在列中心
  recipesAsResult.forEach((recipe, ri) => {
    const rs = buildRecipeSummary(recipe)
    const materials = extractMaterials(recipe)
    const colCenterX = (ri - (recipesAsResult.length - 1) / 2) * COL_WIDTH

    // 材料节点 (y = -2 * V_GAP)，固定3个位置，有材料则放中间
    // 位置映射：1个材料→位置0，2个→-1,0，3个→-1,0,1
    const matPositions = []
    if (materials.length === 1) {
      matPositions.push(0)
    } else if (materials.length === 2) {
      matPositions.push(-0.5, 0.5)
    } else {
      matPositions.push(-1, 0, 1)
    }

    materials.forEach((mat, mi) => {
      const matId = itemNodeKey(mat.id, `_ar_${ri}`)
      const mx = colCenterX + matPositions[mi] * H_GAP
      addNode({
        id: matId,
        type: 'item',
        position: { x: mx, y: -2 * V_GAP },
        data: {
          label: mat.name || `物品${mat.id}`,
          item_id: mat.id,
          quantity: mat.qty,
          category: mat.category || '',
          description: mat.description || '',
          default_price: mat.default_price ?? null,
          asMaterialRecipes: [rs],
          nodeType: 'material'
        }
      })

      // 材料 → 配方（实线）
      const rid = recipeNodeKey(recipe.id, '_ar')
      addEdge({
        id: `e_m_${matId}_r_${rid}`,
        source: matId,
        target: rid,
        type: 'smoothstep',
        data: { direction: 'upstream' },
        markerEnd: makeMarker('#e6a23c'),
        pathOptions: { borderRadius: 8, offset: 30 }
      })
    })

    // 配方节点 (y = -V_GAP)
    const rid = recipeNodeKey(recipe.id, '_ar')
    addNode({
      id: rid,
      type: 'recipe',
      position: { x: colCenterX, y: -V_GAP },
      data: { recipe: rs }
    })

    // 配方 → 中心（实线）
    addEdge({
      id: `e_r_${rid}_c_${centerId}`,
      source: rid,
      target: centerId,
      type: 'smoothstep',
      data: { direction: 'upstream' },
      markerEnd: makeMarker('#e6a23c'),
      pathOptions: { borderRadius: 8, offset: 30 }
    })
  })

  // ===== 下半部分：可制作配方 =====
  recipesByMaterial.forEach((recipe, ri) => {
    const rs = buildRecipeSummary(recipe)
    const resultItemId = Number(recipe.result_item_id) || 0
    if (resultItemId <= 0) return

    const colCenterX = (ri - (recipesByMaterial.length - 1) / 2) * COL_WIDTH

    // 配方节点 (y = V_GAP)
    const rid = recipeNodeKey(recipe.id, '_bm')
    addNode({
      id: rid,
      type: 'recipe',
      position: { x: colCenterX, y: V_GAP },
      data: { recipe: rs }
    })

    // 中心 → 配方（虚线）
    addEdge({
      id: `e_c_${centerId}_r_${rid}`,
      source: centerId,
      target: rid,
      type: 'smoothstep',
      data: { direction: 'downstream' },
      markerEnd: makeMarker('#67c23a'),
      pathOptions: { borderRadius: 8, offset: 30 }
    })

    // 产物节点 (y = 2 * V_GAP)
    const resId = itemNodeKey(resultItemId, `_bm_${ri}`)
    addNode({
      id: resId,
      type: 'item',
      position: { x: colCenterX, y: 2 * V_GAP },
      data: {
        label: recipe.result_item_name || `物品${resultItemId}`,
        item_id: resultItemId,
        quantity: recipe.result_quantity,
        category: recipe.result_item_category || '',
        description: recipe.result_item_description || '',
        default_price: recipe.result_item_price ?? null,
        asResultRecipes: [rs],
        nodeType: 'product'
      }
    })

    // 配方 → 产物（虚线）
    addEdge({
      id: `e_r_${rid}_p_${resId}`,
      source: rid,
      target: resId,
      type: 'smoothstep',
      data: { direction: 'downstream' },
      markerEnd: makeMarker('#67c23a'),
      pathOptions: { borderRadius: 8, offset: 30 }
    })
  })

  return { nodes, edges }
}

/**
 * 从配方中提取有效的材料列表
 */
function extractMaterials(recipe) {
  const materials = []
  for (let i = 1; i <= 3; i++) {
    const id = Number(recipe[`material${i}_id`]) || 0
    const qty = Number(recipe[`material${i}_quantity`]) || 0
    if (id > 0 && qty > 0) {
      materials.push({
        id,
        name: recipe[`material${i}_name`] || '',
        qty,
        category: recipe[`material${i}_category`] || '',
        description: recipe[`material${i}_description`] || '',
        default_price: recipe[`material${i}_default_price`] ?? null
      })
    }
  }
  return materials
}

/**
 * 构建配方摘要
 */
function buildRecipeSummary(recipe) {
  return {
    id: recipe.id,
    name: recipe.name,
    profession_type: recipe.profession_type,
    profession_type_label: recipe.profession_type_label,
    level_required: recipe.level_required,
    lucky_probability: recipe.lucky_probability,
    profession_level_bonus: recipe.profession_level_bonus,
    vitality_cost: recipe.vitality_cost,
    result_quantity: recipe.result_quantity,
    is_ban: recipe.is_ban,
    materials: [
      { id: recipe.material1_id, name: recipe.material1_name, quantity: recipe.material1_quantity },
      { id: recipe.material2_id, name: recipe.material2_name, quantity: recipe.material2_quantity },
      { id: recipe.material3_id, name: recipe.material3_name, quantity: recipe.material3_quantity }
    ].filter(m => Number(m.id) > 0 && Number(m.quantity) > 0),
    result: {
      id: recipe.result_item_id,
      name: recipe.result_item_name,
      quantity: recipe.result_quantity
    }
  }
}
