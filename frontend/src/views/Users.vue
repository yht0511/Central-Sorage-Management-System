<template>
  <div class="users-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button
          type="info"
          @click="fetchUsers"
          :icon="Refresh"
          :loading="loading"
        >
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
          添加用户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名、邮箱或姓名"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedRole"
            placeholder="筛选角色"
            clearable
            @change="handleRoleFilter"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedStatus"
            placeholder="筛选状态"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 用户表格 -->
    <el-table :data="users" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="real_name" label="真实姓名" min-width="120">
        <template #default="scope">
          {{ scope.row.real_name || "-" }}
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="电话" min-width="120">
        <template #default="scope">
          {{ scope.row.phone || "-" }}
        </template>
      </el-table-column>
      <el-table-column prop="department" label="部门" min-width="120">
        <template #default="scope">
          {{ scope.row.department || "-" }}
        </template>
      </el-table-column>
      <el-table-column prop="role" label="角色" width="100">
        <template #default="scope">
          <el-tag
            :type="scope.row.role === 'admin' ? 'danger' : 'info'"
            size="small"
          >
            {{ scope.row.role === "admin" ? "管理员" : "普通用户" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="active" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.active ? 'success' : 'danger'" size="small">
            {{ scope.row.active ? "激活" : "禁用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button
            type="primary"
            size="small"
            @click="editUser(scope.row)"
            :icon="Edit"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteUser(scope.row)"
            :icon="Delete"
            :disabled="scope.row.id === currentUserId"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-if="total > pageSize"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :small="false"
      :background="true"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      class="pagination"
    />

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="editingUser"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="真实姓名">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="电话">
          <el-input v-model="form.phone" placeholder="请输入电话号码" />
        </el-form-item>

        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="请输入部门" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="active">
          <el-switch v-model="form.active" />
        </el-form-item>

        <el-form-item label="个人简介">
          <el-input
            v-model="form.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">
          {{ editingUser ? "更新" : "创建" }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Search, Refresh, Edit, Delete } from "@element-plus/icons-vue";
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// 响应式数据
const loading = ref(false);
const saving = ref(false);
const users = ref([]);
const showCreateDialog = ref(false);
const editingUser = ref(null);

// 搜索和筛选
const searchQuery = ref("");
const selectedRole = ref("");
const selectedStatus = ref("");

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 表单数据
const formRef = ref();
const form = reactive({
  username: "",
  email: "",
  password: "",
  real_name: "",
  phone: "",
  department: "",
  role: "user",
  active: true,
  bio: "",
});

// 当前用户ID，用于防止删除自己
const currentUserId = computed(() => authStore.user?.id);

const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度至少 6 个字符", trigger: "blur" },
  ],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
};

// 方法
const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
    };

    if (selectedRole.value) {
      params.role = selectedRole.value;
    }
    if (selectedStatus.value !== "") {
      params.active = selectedStatus.value;
    }

    const response = await api.get("/admin/users", { params });
    users.value = response.data.data || [];
    total.value = response.data.total || 0;
  } catch (error) {
    ElMessage.error("获取用户列表失败");
    console.error("Error fetching users:", error);
    users.value = [];
  } finally {
    loading.value = false;
  }
};

const editUser = (user) => {
  editingUser.value = user;
  Object.assign(form, {
    username: user.username,
    email: user.email,
    password: "",
    real_name: user.real_name || "",
    phone: user.phone || "",
    department: user.department || "",
    role: user.role,
    active: user.active,
    bio: user.bio || "",
  });
  showCreateDialog.value = true;
};

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/admin/users/${user.id}`);
    ElMessage.success("用户删除成功");
    fetchUsers();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("用户删除失败");
      console.error("Error deleting user:", error);
    }
  }
};

const saveUser = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    saving.value = true;

    if (editingUser.value) {
      // 更新用户
      const updateData = {
        email: form.email,
        real_name: form.real_name,
        phone: form.phone,
        department: form.department,
        role: form.role,
        active: form.active,
        bio: form.bio,
      };
      await api.put(`/admin/users/${editingUser.value.id}`, updateData);
      ElMessage.success("用户更新成功");
    } else {
      // 创建用户
      await api.post("/admin/register", form);
      ElMessage.success("用户创建成功");
    }

    showCreateDialog.value = false;
    resetForm();
    fetchUsers();
  } catch (error) {
    ElMessage.error(editingUser.value ? "用户更新失败" : "用户创建失败");
    console.error("Error saving user:", error);
  } finally {
    saving.value = false;
  }
};

const cancelEdit = () => {
  showCreateDialog.value = false;
  resetForm();
};

const resetForm = () => {
  editingUser.value = null;
  Object.assign(form, {
    username: "",
    email: "",
    password: "",
    real_name: "",
    phone: "",
    department: "",
    role: "user",
    active: true,
    bio: "",
  });
  formRef.value?.resetFields();
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString("zh-CN");
};

// 筛选和分页处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchUsers();
};

const handleRoleFilter = () => {
  currentPage.value = 1;
  fetchUsers();
};

const handleStatusFilter = () => {
  currentPage.value = 1;
  fetchUsers();
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchUsers();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchUsers();
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.users-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
}
</style>
