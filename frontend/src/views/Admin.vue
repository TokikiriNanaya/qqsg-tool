<template>
  <div class="admin-page">
    <Header />
    
    <el-main>
      <div class="container">
        <h1>管理后台</h1>
        
        <el-tabs v-model="activeTab">
          <!-- 用户管理 -->
          <el-tab-pane label="用户管理" name="users">
            <el-table :data="users" v-loading="userLoading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="role" label="角色" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
                    {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '活跃' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    :type="row.is_active ? 'warning' : 'success'"
                    @click="toggleUserStatus(row)"
                  >
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="loadUsers"
                @size-change="handleSizeChange"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-main>
    
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getUsers, updateUserStatus } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('users')
const users = ref([])
const userLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadUsers = async () => {
  userLoading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    const res = await getUsers(params)
    // 后端返回格式: { total: number, items: array }
    users.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    userLoading.value = false
  }
}

// 处理每页显示数量变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 重置到第一页
  loadUsers()
}

// 切换用户状态
const toggleUserStatus = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateUserStatus(row.id, { is_active: !row.is_active })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${action}失败:`, error)
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main {
  flex: 1;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
