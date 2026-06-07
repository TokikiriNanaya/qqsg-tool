<template>
  <el-header class="header">
    <div class="header-content">
      <div class="logo" @click="$router.push('/')">
        <h2>QQSG配方查询</h2>
      </div>
      
      <el-menu mode="horizontal" :ellipsis="false" router>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/recipes">配方列表</el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/admin">管理后台</el-menu-item>
      </el-menu>
      
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <span class="username">{{ userStore.userInfo?.username }}</span>
          <el-button type="danger" @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
}
</script>

<style scoped>
.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  cursor: pointer;
  color: #667eea;
}

.logo h2 {
  margin: 0;
}

.el-menu {
  border-bottom: none;
  flex: 1;
  justify-content: center;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #606266;
  margin-right: 10px;
}
</style>
