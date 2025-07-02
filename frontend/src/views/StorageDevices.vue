<template>
  <div class="storage-devices">
    <div class="page-header">
      <h2>存储装置管理</h2>
      <el-button
        v-if="authStore.isAdmin"
        type="primary"
        @click="showCreateDialog = true"
        :icon="Plus"
      >
        新增存储装置
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索存储装置名称"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedLaboratory"
            placeholder="筛选实验室"
            clearable
            @change="handleLabFilter"
          >
            <el-option
              v-for="lab in laboratories"
              :key="`lab-${lab?.id || 'unknown'}`"
              :label="lab?.name || '未命名实验室'"
              :value="lab?.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedStatus"
            placeholder="筛选状态"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="运行中" value="运行中" />
            <el-option label="维护中" value="维护中" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 存储装置表格 -->
    <el-table :data="devices" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="装置名称" min-width="150" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="laboratory_name" label="所属实验室" width="150" />
      <el-table-column prop="location" label="位置" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" size="small">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="security_level" label="安全等级" width="120">
        <template #default="scope">
          <el-tag
            :type="getSecurityLevelType(scope.row.security_level)"
            size="small"
          >
            {{ scope.row.security_level }}级
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="capacity" label="容量" width="100" />
      <el-table-column label="属性" width="100">
        <template #default="scope">
          <el-button
            size="small"
            type="info"
            @click="showProperties(scope.row)"
            :disabled="
              !scope.row.properties ||
              Object.keys(scope.row.properties).length === 0
            "
          >
            查看 ({{
              scope.row.properties
                ? Object.keys(scope.row.properties).length
                : 0
            }})
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column
        v-if="authStore.isAdmin"
        label="操作"
        width="180"
        fixed="right"
      >
        <template #default="scope">
          <el-button size="small" @click="editDevice(scope.row)">
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteDevice(scope.row)"
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

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingDevice ? '编辑存储装置' : '新增存储装置'"
      width="600px"
      :before-close="handleClose"
    >
      <el-form
        ref="deviceFormRef"
        :model="deviceForm"
        :rules="deviceRules"
        label-width="100px"
      >
        <el-form-item label="装置编号" prop="code">
          <el-input v-model="deviceForm.code" placeholder="请输入装置编号" />
        </el-form-item>

        <el-form-item label="装置名称" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入装置名称" />
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-input v-model="deviceForm.type" placeholder="请输入装置类型" />
        </el-form-item>

        <el-form-item label="所属实验室" prop="lab_id">
          <el-select
            v-model="deviceForm.lab_id"
            placeholder="请选择实验室"
            style="width: 100%"
          >
            <el-option
              v-for="lab in laboratories"
              :key="`form-lab-${lab?.id || 'unknown'}`"
              :label="lab?.name || '未命名实验室'"
              :value="lab?.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="位置" prop="location">
          <el-input
            v-model="deviceForm.location"
            placeholder="请输入装置位置"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="deviceForm.status" style="width: 100%">
            <el-option label="运行中" value="运行中" />
            <el-option label="维护中" value="维护中" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>

        <el-form-item label="安全等级" prop="security_level">
          <el-select
            v-model="deviceForm.security_level"
            placeholder="选择安全等级"
          >
            <el-option
              v-for="level in securityLevels"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="容量" prop="capacity">
          <el-input-number
            v-model="deviceForm.capacity"
            :min="0"
            :max="999999"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="deviceForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入装置描述"
          />
        </el-form-item>

        <el-form-item label="自定义属性">
          <PropertyEditor
            v-model="deviceForm.properties"
            title="装置属性"
            :show-json-editor="true"
            :max-properties="20"
            @validate="handleDevicePropertyValidation"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="saveDevice" :loading="saving">
            {{ editingDevice ? "更新" : "创建" }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 属性查看对话框 -->
    <el-dialog v-model="showPropertiesDialog" title="装置属性" width="500px">
      <div v-if="selectedDeviceProperties">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in selectedDeviceProperties"
            :key="key"
            :label="key"
          >
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="no-properties">
        <el-empty description="暂无自定义属性" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Search } from "@element-plus/icons-vue";
import api from "@/services/api";
import PropertyEditor from "@/components/PropertyEditor.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// 响应式数据
const loading = ref(false);
const saving = ref(false);
const devices = ref([]);
const laboratories = ref([]);
const searchQuery = ref("");
const selectedLaboratory = ref("");
const selectedStatus = ref("");
const showCreateDialog = ref(false);
const showPropertiesDialog = ref(false);
const editingDevice = ref(null);
const deviceFormRef = ref();
const selectedDeviceProperties = ref(null);
const devicePropertyValidation = ref({ isValid: true, errors: [] }); // 新增属性验证状态

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const totalPages = ref(0);

// 表单数据
const deviceForm = reactive({
  code: "", // 新增编号字段
  name: "",
  type: "",
  lab_id: null,
  location: "",
  status: "运行中",
  security_level: 1,
  capacity: 0,
  description: "",
  properties: {},
});

// 表单验证规则
const deviceRules = {
  code: [
    { required: true, message: "请输入装置编号", trigger: "blur" },
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" },
  ],
  name: [
    { required: true, message: "请输入装置名称", trigger: "blur" },
    { min: 2, max: 100, message: "长度在 2 到 100 个字符", trigger: "blur" },
  ],
  type: [{ required: true, message: "请输入装置类型", trigger: "blur" }],
  lab_id: [{ required: true, message: "请选择所属实验室", trigger: "change" }],
  location: [{ required: true, message: "请输入装置位置", trigger: "blur" }],
  status: [{ required: true, message: "请选择装置状态", trigger: "change" }],
  security_level: [
    { required: true, message: "请选择安全等级", trigger: "change" },
  ],
};

// 安全等级选项
const securityLevels = [
  { value: 1, label: "1级 - 公开访问（任何人都可以接触）" },
  { value: 2, label: "2级 - 低保密性（一般工作人员可访问）" },
  { value: 3, label: "3级 - 中等保密性（授权人员可访问）" },
  { value: 4, label: "4级 - 高保密性（特定权限人员可访问）" },
  { value: 5, label: "5级 - 极端保密（最高权限人员可访问）" },
];

// 移除本地筛选分页，全部后端化
const fetchDevices = async () => {
  loading.value = true;
  try {
    const maxPageSize = 100; // 后端允许的最大page_size
    const params = {
      page: currentPage.value || 1,
      page_size: Math.min(pageSize.value || 20, maxPageSize),
      search: searchQuery.value,
      lab_id: selectedLaboratory.value,
      status: selectedStatus.value,
    };
    // 清理空参数
    Object.keys(params).forEach(
      (k) => (params[k] === "" || params[k] == null) && delete params[k]
    );
    const response = await api.get("/storages", { params });
    // 兼容后端分页结构
    const d = response.data;
    let arr = [];
    if (d && Array.isArray(d.data)) {
      arr = d.data;
      total.value = d.total || 0;
      totalPages.value = d.total_pages || 0;
      currentPage.value = d.page || 1;
      pageSize.value = d.page_size || pageSize.value;
    } else if (Array.isArray(d.storages)) {
      arr = d.storages;
      total.value = arr.length;
    }
    devices.value = arr.map((device) => ({
      ...device,
      laboratory_name: device.laboratory?.name || "未知实验室",
    }));
  } catch (error) {
    ElMessage.error("获取存储装置列表失败");
    console.error("Error fetching devices:", error);
  } finally {
    loading.value = false;
  }
};

const fetchLaboratories = async () => {
  try {
    const maxPageSize = 100; // 后端允许的最大page_size
    const params = { page: 1, page_size: maxPageSize };
    const response = await api.get("/laboratories", { params });
    if (Array.isArray(response.data.data)) {
      laboratories.value = response.data.data;
    } else if (Array.isArray(response.data.laboratories)) {
      laboratories.value = response.data.laboratories;
    } else {
      laboratories.value = [];
    }
  } catch (error) {
    console.error("Error fetching laboratories:", error);
    laboratories.value = [];
  }
};

// 移除本地筛选分页，el-table数据源直接用 devices，分页事件直接调用 fetchDevices
const filteredDevices = computed(() => devices.value);

const handleSearch = () => {
  currentPage.value = 1;
  fetchDevices();
};
const handleLabFilter = () => {
  currentPage.value = 1;
  fetchDevices();
};
const handleStatusFilter = () => {
  currentPage.value = 1;
  fetchDevices();
};
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchDevices();
};
const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchDevices();
};

const getStatusType = (status) => {
  const statusMap = {
    运行中: "success",
    维护中: "warning",
    停用: "danger",
  };
  return statusMap[status] || "info";
};

const getSecurityLevelType = (level) => {
  switch (level) {
    case 1:
      return "success"; // 绿色 - 公开访问，安全
    case 2:
      return "info"; // 蓝色 - 低保密性
    case 3:
      return "warning"; // 橙色 - 中等保密性
    case 4:
      return "danger"; // 红色 - 高保密性
    case 5:
      return "danger"; // 红色 - 极端保密
    default:
      return "info";
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "未知";
  return new Date(dateString).toLocaleString("zh-CN");
};

const resetForm = () => {
  Object.assign(deviceForm, {
    code: "",
    name: "",
    type: "",
    lab_id: null,
    location: "",
    status: "运行中",
    security_level: 1,
    capacity: 0,
    description: "",
    properties: {},
  });
  editingDevice.value = null;
  if (deviceFormRef.value) {
    deviceFormRef.value.resetFields();
  }
};

const editDevice = (device) => {
  editingDevice.value = device;
  // 只提取表单需要的字段，避免赋值嵌套对象
  Object.assign(deviceForm, {
    code: device.code || "",
    name: device.name || "",
    type: device.type || "",
    lab_id: device.lab_id || null,
    location: device.location || "",
    status: device.status || "运行中",
    security_level: device.security_level || 1,
    capacity: device.capacity || 0,
    description: device.description || "",
    properties: JSON.parse(JSON.stringify(device.properties || {})), // 深拷贝
  });
  showCreateDialog.value = true;
};

const saveDevice = async () => {
  if (!deviceFormRef.value) return;

  const valid = await deviceFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 验证属性
  if (!devicePropertyValidation.value.isValid) {
    ElMessage.error(
      `属性配置有误：${devicePropertyValidation.value.errors.join(", ")}`
    );
    return;
  }

  saving.value = true;
  try {
    // 只提取后端需要的字段，过滤掉冗余字段
    const data = {
      code: deviceForm.code,
      name: deviceForm.name,
      type: deviceForm.type,
      lab_id: deviceForm.lab_id,
      location: deviceForm.location,
      status: deviceForm.status,
      security_level: deviceForm.security_level,
      capacity: deviceForm.capacity,
      description: deviceForm.description,
      properties: deviceForm.properties,
    };

    console.log("Saving device data:", data);
    console.log("Lab ID type:", typeof data.lab_id);
    console.log("Lab ID value:", data.lab_id);

    if (editingDevice.value) {
      await api.put(`/admin/storages/${editingDevice.value.id}`, data);
      ElMessage.success("更新存储装置成功");
    } else {
      await api.post("/admin/storages", data);
      ElMessage.success("创建存储装置成功");
    }

    showCreateDialog.value = false;
    resetForm();
    fetchDevices();
  } catch (error) {
    ElMessage.error(
      editingDevice.value ? "更新存储装置失败" : "创建存储装置失败"
    );
    console.error("Error saving device:", error);
  } finally {
    saving.value = false;
  }
};

const deleteDevice = async (device) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除存储装置 "${device.name}" 吗？此操作不可撤销。`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/admin/storages/${device.id}`);
    ElMessage.success("删除存储装置成功");
    fetchDevices();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除存储装置失败");
      console.error("Error deleting device:", error);
    }
  }
};

const showProperties = (device) => {
  selectedDeviceProperties.value = device.properties;
  showPropertiesDialog.value = true;
};

const handleClose = () => {
  showCreateDialog.value = false;
  resetForm();
};

// 处理装置属性验证
const handleDevicePropertyValidation = (validation) => {
  devicePropertyValidation.value = validation;
};

// 生命周期
onMounted(() => {
  fetchDevices();
  fetchLaboratories();
});
</script>

<style scoped>
.storage-devices {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.no-properties {
  text-align: center;
  padding: 40px 0;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
}
</style>
