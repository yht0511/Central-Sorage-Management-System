<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ stats.laboratories }}</div>
        <div class="stat-label">实验室总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.storages }}</div>
        <div class="stat-label">存储装置</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.sections }}</div>
        <div class="stat-label">分区数量</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.items }}</div>
        <div class="stat-label">物品总数</div>
      </div>
    </div>

    <!-- 快速操作和警告 -->
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button
              v-if="authStore.isAdmin"
              type="primary"
              :icon="Plus"
              @click="$router.push('/laboratories')"
            >
              新建实验室
            </el-button>
            <el-button
              v-if="authStore.isAdmin"
              type="success"
              :icon="Plus"
              @click="$router.push('/storages')"
            >
              添加存储装置
            </el-button>
            <el-button
              v-if="authStore.isAdmin"
              type="warning"
              :icon="Plus"
              @click="$router.push('/items')"
            >
              添加物品
            </el-button>
            <el-button
              type="info"
              :icon="Search"
              @click="$router.push('/items')"
            >
              搜索物品
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>库存警告</span>
              <el-badge :value="lowStockItems.length" class="badge" />
            </div>
          </template>
          <div class="warning-list">
            <div
              v-for="item in lowStockItems.slice(0, 3)"
              :key="item.id"
              class="warning-item"
            >
              <el-icon class="warning-icon"><WarningFilled /></el-icon>
              <div class="warning-content">
                <div class="warning-title">{{ item.name }}</div>
                <div class="warning-desc">
                  当前库存：{{ item.quantity }} {{ item.unit }}， 最低库存：{{
                    item.min_quantity
                  }}
                  {{ item.unit }}
                </div>
              </div>
            </div>
            <div v-if="lowStockItems.length === 0" class="no-warnings">
              <el-icon><CircleCheckFilled /></el-icon>
              <span>暂无库存警告</span>
            </div>
            <div v-if="lowStockItems.length > 3" class="more-warnings">
              <el-button text @click="$router.push('/items?low_stock=true')">
                查看全部 {{ lowStockItems.length }} 个警告
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>过期警告</span>
              <el-badge
                :value="expiringItems.length"
                class="badge"
                type="danger"
              />
            </div>
          </template>
          <div class="warning-list">
            <div
              v-for="item in expiringItems.slice(0, 3)"
              :key="item.id"
              class="warning-item"
            >
              <el-icon class="expiring-icon"><AlarmClock /></el-icon>
              <div class="warning-content">
                <div class="warning-title">{{ item.name }}</div>
                <div class="warning-desc">
                  过期日期：{{ formatDate(item.expiry_date) }}
                </div>
              </div>
            </div>
            <div v-if="expiringItems.length === 0" class="no-warnings">
              <el-icon><CircleCheckFilled /></el-icon>
              <span>暂无过期警告</span>
            </div>
            <div v-if="expiringItems.length > 3" class="more-warnings">
              <el-button text @click="$router.push('/items?expiring=true')">
                查看全部 {{ expiringItems.length }} 个警告
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近移动记录 -->
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>最近移动记录</span>
          <el-button text @click="$router.push('/movements')"
            >查看全部</el-button
          >
        </div>
      </template>
      <el-table :data="recentMovements" style="width: 100%">
        <el-table-column prop="item.name" label="物品名称" />
        <el-table-column prop="movement_type" label="操作类型">
          <template #default="{ row }">
            <el-tag :type="getMovementTypeTag(row.movement_type)" size="small">
              {{ getMovementTypeText(row.movement_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="user.username" label="操作人" />
        <el-table-column prop="created_at" label="时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";
import { ElMessage } from "element-plus";
import {
  Plus,
  Search,
  WarningFilled,
  CircleCheckFilled,
  AlarmClock,
} from "@element-plus/icons-vue";

const authStore = useAuthStore();

const stats = ref({
  laboratories: 0,
  storages: 0,
  sections: 0,
  items: 0,
});

const lowStockItems = ref([]);
const expiringItems = ref([]);
const recentMovements = ref([]);

const fetchStats = async () => {
  try {
    // 使用专门的统计API
    const response = await api.get("/stats/dashboard");
    stats.value = {
      laboratories: response.data.laboratories || 0,
      storages: response.data.storages || 0,
      sections: response.data.sections || 0,
      items: response.data.items || 0,
    };
  } catch (error) {
    console.error("获取统计数据失败:", error);
    // 如果统计API失败，回退到各个API
    try {
      const [labsRes, storagesRes, sectionsRes, itemsRes] = await Promise.all([
        api.get("/laboratories"),
        api.get("/storages"),
        api.get("/sections"),
        api.get("/items"),
      ]);

      stats.value = {
        laboratories: labsRes.data.total || labsRes.data.data?.length || 0,
        storages: storagesRes.data.total || storagesRes.data.data?.length || 0,
        sections: sectionsRes.data.total || sectionsRes.data.data?.length || 0,
        items: itemsRes.data.total || itemsRes.data.data?.length || 0,
      };
    } catch (fallbackError) {
      console.error("获取备用统计数据也失败:", fallbackError);
    }
  }
};

const fetchLowStockItems = async () => {
  try {
    const response = await api.get("/items/low-stock");
    lowStockItems.value = response.data.data || response.data.items || [];
  } catch (error) {
    console.error("获取低库存物品失败:", error);
    lowStockItems.value = [];
  }
};

const fetchExpiringItems = async () => {
  try {
    const response = await api.get("/items/expiring");
    expiringItems.value = response.data.data || response.data.items || [];
  } catch (error) {
    console.error("获取即将过期物品失败:", error);
    expiringItems.value = [];
  }
};

const fetchRecentMovements = async () => {
  try {
    const response = await api.get("/movements");
    const movements =
      response.data.data || response.data.movements || response.data || [];
    recentMovements.value = movements.slice(0, 10);
  } catch (error) {
    console.error("获取移动记录失败:", error);
    recentMovements.value = [];
  }
};

const getMovementTypeTag = (type) => {
  switch (type) {
    case "in":
      return "success";
    case "out":
      return "danger";
    case "transfer":
      return "warning";
    default:
      return "info";
  }
};

const getMovementTypeText = (type) => {
  switch (type) {
    case "in":
      return "入库";
    case "out":
      return "出库";
    case "transfer":
      return "转移";
    default:
      return "未知";
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-CN");
};

onMounted(() => {
  fetchStats();
  fetchLowStockItems();
  fetchExpiringItems();
  fetchRecentMovements();
});
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

/* 统计卡片样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
  color: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 中间三个框保持相同高度 */
.el-row .el-col {
  display: flex;
}

.dashboard-card {
  margin-bottom: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.dashboard-card .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 快速操作区域 */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1;
  align-content: flex-start;
}

.quick-actions .el-button {
  flex: 1;
  min-width: 120px;
}

/* 警告列表区域 */
.warning-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.warning-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.warning-item:last-child {
  border-bottom: none;
}

.warning-icon {
  color: #e6a23c;
  margin-top: 2px;
}

.expiring-icon {
  color: #f56c6c;
  margin-top: 2px;
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.warning-desc {
  font-size: 14px;
  color: #606266;
}

.no-warnings {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  color: #67c23a;
  min-height: 100px;
}

.more-warnings {
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.badge {
  margin-left: 8px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-number {
    font-size: 24px;
  }

  .quick-actions .el-button {
    min-width: 100px;
    font-size: 12px;
  }

  .warning-list {
    min-height: 150px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .el-row .el-col {
    margin-bottom: 16px;
  }

  .quick-actions {
    gap: 8px;
  }

  .quick-actions .el-button {
    min-width: 80px;
  }
}
</style>
