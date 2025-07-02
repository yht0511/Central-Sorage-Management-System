<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobile && sidebarVisible"
      class="sidebar-overlay"
      @click="toggleSidebar"
    ></div>

    <el-aside
      :width="sidebarWidth"
      :class="['sidebar', { 'sidebar-hidden': isMobile && !sidebarVisible }]"
    >
      <div class="logo">
        <el-icon><Management /></el-icon>
        <span v-if="!isMobile || sidebarVisible" class="logo-text"
          >实验室仓储管理系统</span
        >
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        :collapse="isMobile && !sidebarVisible"
        @select="onMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>总览</span>
        </el-menu-item>

        <el-menu-item index="/laboratories">
          <el-icon><OfficeBuilding /></el-icon>
          <span>实验室管理</span>
        </el-menu-item>

        <el-menu-item index="/storages">
          <el-icon><Box /></el-icon>
          <span>存储装置</span>
        </el-menu-item>

        <el-menu-item index="/sections">
          <el-icon><Grid /></el-icon>
          <span>分区管理</span>
        </el-menu-item>

        <el-menu-item index="/items">
          <el-icon><Goods /></el-icon>
          <span>物品管理</span>
        </el-menu-item>

        <el-menu-item index="/movements">
          <el-icon><TrendCharts /></el-icon>
          <span>移动记录</span>
        </el-menu-item>

        <el-menu-item index="/users" v-if="authStore.isAdmin">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-button
            v-if="isMobile"
            class="menu-button"
            type="text"
            @click="toggleSidebar"
          >
            <el-icon size="20"><Menu /></el-icon>
          </el-button>
          <h2 class="header-title">
            {{ $route.meta.title || "实验室仓储管理系统" }}
          </h2>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username" v-if="!isMobile">{{
                authStore.user?.username
              }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { ElMessageBox, ElMessage } from "element-plus";
import {
  Management,
  Odometer,
  OfficeBuilding,
  Box,
  Grid,
  Goods,
  TrendCharts,
  User,
  ArrowDown,
  SwitchButton,
  Menu,
} from "@element-plus/icons-vue";

const router = useRouter();
const authStore = useAuthStore();

// 响应式状态
const isMobile = ref(false);
const sidebarVisible = ref(true);

// 计算属性
const sidebarWidth = computed(() => {
  if (isMobile.value) {
    return sidebarVisible.value ? "250px" : "0px";
  }
  return "250px";
});

// 检查是否为移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
  if (isMobile.value) {
    sidebarVisible.value = false;
  } else {
    sidebarVisible.value = true;
  }
};

// 切换侧栏显示
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};

// 菜单选择事件（移动端选择菜单后自动隐藏侧栏）
const onMenuSelect = () => {
  if (isMobile.value) {
    sidebarVisible.value = false;
  }
};

// 处理用户操作
const handleCommand = async (command) => {
  switch (command) {
    case "profile":
      router.push("/profile");
      break;
    case "logout":
      try {
        await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        });
        authStore.logout();
        ElMessage.success("已退出登录");
        router.push("/login");
      } catch {
        // 用户取消
      }
      break;
  }
};

// 生命周期
onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", checkMobile);
});
</script>

<style scoped>
.layout-container {
  height: 100vh;
  position: relative;
}

.sidebar {
  background-color: #304156;
  border-right: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1000;
}

.sidebar-hidden {
  margin-left: -250px;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: block;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 60px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #434d5e;
  padding: 0 16px;
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 60px);
}

.main-container {
  transition: margin-left 0.3s ease;
  flex: 1;
  min-width: 0;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.menu-button {
  padding: 8px;
  margin-right: 8px;
  color: #606266;
}

.menu-button:hover {
  background-color: #f5f7fa;
}

.header-title {
  color: #303133;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  color: #303133;
  font-size: 14px;
  white-space: nowrap;
}

.dropdown-icon {
  color: #909399;
  transition: transform 0.2s;
}

.main-content {
  background-color: #f5f7fa;
  padding: 16px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }

  .main-container {
    margin-left: 0 !important;
    width: 100%;
  }

  .header {
    padding: 0 12px;
  }

  .header-title {
    font-size: 16px;
  }

  .main-content {
    padding: 12px;
  }

  .logo {
    font-size: 16px;
    padding: 0 12px;
  }

  .user-info {
    padding: 6px 8px;
  }
}

/* 小屏幕优化 */
@media (max-width: 480px) {
  .header-title {
    font-size: 14px;
  }

  .logo {
    font-size: 14px;
  }

  .main-content {
    padding: 8px;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .header-title {
    font-size: 17px;
  }

  .main-content {
    padding: 20px;
  }
}
</style>
