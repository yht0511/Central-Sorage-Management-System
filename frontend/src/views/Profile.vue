<template>
  <div class="profile">
    <div class="page-header">
      <h2>个人资料</h2>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：基本信息 -->
      <el-col :span="16">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h3>基本信息</h3>
              <el-button
                type="primary"
                size="small"
                @click="enableEdit"
                v-if="!isEditing"
              >
                编辑资料
              </el-button>
              <div v-else>
                <el-button size="small" @click="cancelEdit"> 取消 </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click="saveProfile"
                  :loading="saving"
                >
                  保存
                </el-button>
              </div>
            </div>
          </template>

          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            :disabled="!isEditing"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input
                    v-model="profileForm.username"
                    disabled
                    placeholder="用户名不可修改"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="角色">
                  <el-tag :type="getRoleType(profileForm.role)" size="large">
                    {{ getRoleLabel(profileForm.role) }}
                  </el-tag>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="真实姓名" prop="real_name">
                  <el-input
                    v-model="profileForm.real_name"
                    placeholder="请输入真实姓名"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="profileForm.email"
                    placeholder="请输入邮箱地址"
                    type="email"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="电话" prop="phone">
                  <el-input
                    v-model="profileForm.phone"
                    placeholder="请输入电话号码"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="部门">
                  <el-input
                    v-model="profileForm.department"
                    placeholder="请输入所属部门"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="个人简介">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="请输入个人简介"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="注册时间">
              <el-input :value="formatDate(userInfo.created_at)" disabled />
            </el-form-item>

            <el-form-item label="最后登录">
              <el-input :value="formatDate(userInfo.last_login)" disabled />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="password-card">
          <template #header>
            <h3>修改密码</h3>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="current_password">
              <el-input
                v-model="passwordForm.current_password"
                type="password"
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="changePassword"
                :loading="changingPassword"
              >
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm"> 重置 </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：统计信息 -->
      <el-col :span="8">
        <el-card class="stats-card">
          <template #header>
            <h3>活动统计</h3>
          </template>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_items || 0 }}</div>
              <div class="stat-label">管理的物品</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_movements || 0 }}</div>
              <div class="stat-label">移动记录</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.labs_count || 0 }}</div>
              <div class="stat-label">可访问实验室</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.devices_count || 0 }}</div>
              <div class="stat-label">可访问设备</div>
            </div>
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card class="activity-card">
          <template #header>
            <h3>最近活动</h3>
          </template>

          <div class="activity-list" v-loading="loadingActivity">
            <div
              v-for="activity in recentActivities"
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-icon">
                <el-icon :size="16">
                  <component :is="getActivityIcon(activity.type)" />
                </el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-text">{{ activity.description }}</div>
                <div class="activity-time">
                  {{ formatRelativeTime(activity.created_at) }}
                </div>
              </div>
            </div>
            <div v-if="recentActivities.length === 0" class="no-activity">
              <el-empty description="暂无活动记录" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import api, { apiMethods } from "@/services/api";
import {
  User,
  Box,
  Position,
  Edit,
  Plus,
  Delete,
} from "@element-plus/icons-vue";

const authStore = useAuthStore();

// 响应式数据
const isEditing = ref(false);
const saving = ref(false);
const changingPassword = ref(false);
const loadingActivity = ref(false);
const profileFormRef = ref();
const passwordFormRef = ref();
const userInfo = ref({});
const stats = ref({});
const recentActivities = ref([]);

// 表单数据
const profileForm = reactive({
  username: "",
  real_name: "",
  email: "",
  phone: "",
  department: "",
  bio: "",
  role: "",
});

const passwordForm = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

// 验证规则
const profileRules = {
  real_name: [
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" },
  ],
  email: [{ type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号码",
      trigger: "blur",
    },
  ],
};

const passwordRules = {
  current_password: [
    { required: true, message: "请输入当前密码", trigger: "blur" },
  ],
  new_password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, max: 20, message: "密码长度在 6 到 20 个字符", trigger: "blur" },
  ],
  confirm_password: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

// 方法
const fetchUserProfile = async () => {
  try {
    const response = await apiMethods.user.getProfile();
    userInfo.value = response.data.user;
    Object.assign(profileForm, response.data.user);
  } catch (error) {
    ElMessage.error("获取用户信息失败");
    console.error("Error fetching user profile:", error);
  }
};

const fetchUserStats = async () => {
  try {
    const response = await apiMethods.user.getStats();
    stats.value = response.data;
  } catch (error) {
    console.error("Error fetching user stats:", error);
  }
};

const fetchRecentActivities = async () => {
  loadingActivity.value = true;
  try {
    const response = await apiMethods.user.getActivities({ limit: 10 });
    recentActivities.value = response.data.movements || [];
  } catch (error) {
    console.error("Error fetching recent activities:", error);
  } finally {
    loadingActivity.value = false;
  }
};

const enableEdit = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
  Object.assign(profileForm, userInfo.value);
};

const saveProfile = async () => {
  if (!profileFormRef.value) return;

  const valid = await profileFormRef.value.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const response = await apiMethods.user.updateProfile(profileForm);
    userInfo.value = response.data.user;
    // 更新本地存储的用户信息
    const updatedUser = { ...authStore.user, ...profileForm };
    authStore.user = updatedUser;
    localStorage.setItem("user", JSON.stringify(updatedUser));
    isEditing.value = false;
    ElMessage.success("保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
    console.error("Error saving profile:", error);
  } finally {
    saving.value = false;
  }
};

const changePassword = async () => {
  if (!passwordFormRef.value) return;

  const valid = await passwordFormRef.value.validate().catch(() => false);
  if (!valid) return;

  changingPassword.value = true;
  try {
    await apiMethods.user.changePassword({
      old_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
    ElMessage.success("密码修改成功");
    resetPasswordForm();
  } catch (error) {
    if (error.response?.status === 400) {
      ElMessage.error("当前密码错误");
    } else {
      ElMessage.error("密码修改失败");
    }
    console.error("Error changing password:", error);
  } finally {
    changingPassword.value = false;
  }
};

const resetPasswordForm = () => {
  passwordForm.current_password = "";
  passwordForm.new_password = "";
  passwordForm.confirm_password = "";
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields();
  }
};

const getRoleType = (role) => {
  const roleMap = {
    admin: "",
    manager: "warning",
    user: "info",
  };
  return roleMap[role] || "info";
};

const getRoleLabel = (role) => {
  const roleMap = {
    admin: "超级管理员",
    manager: "管理员",
    user: "普通用户",
  };
  return roleMap[role] || "未知角色";
};

const getActivityIcon = (type) => {
  const iconMap = {
    create: Plus,
    update: Edit,
    delete: Delete,
    move: Position,
    login: User,
  };
  return iconMap[type] || Box;
};

const formatDate = (dateString) => {
  if (!dateString) return "未知";
  return new Date(dateString).toLocaleString("zh-CN");
};

const formatRelativeTime = (dateString) => {
  if (!dateString) return "未知";

  const now = new Date();
  const date = new Date(dateString);
  const diff = now - date;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "刚刚";
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;

  return formatDate(dateString);
};

// 生命周期
onMounted(() => {
  fetchUserProfile();
  fetchUserStats();
  fetchRecentActivities();
});
</script>

<style scoped>
.profile {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.profile-card,
.password-card,
.stats-card,
.activity-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  background: #f0f9ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: #409eff;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.5;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.no-activity {
  text-align: center;
  padding: 40px 0;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
