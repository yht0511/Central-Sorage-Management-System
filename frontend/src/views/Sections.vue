<template>
  <div class="sections">
    <div class="page-header">
      <h2>分区管理</h2>
      <el-button
        v-if="authStore.isAdmin"
        type="primary"
        @click="showCreateDialog = true"
        :icon="Plus"
      >
        新增分区
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索分区名称"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedDevice"
            placeholder="筛选存储装置"
            clearable
            @change="handleDeviceFilter"
          >
            <el-option
              v-for="device in storageDevices"
              :key="device?.id"
              :label="device?.name"
              :value="device?.id"
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
            <el-option label="可用" value="可用" />
            <el-option label="已满" value="已满" />
            <el-option label="维护中" value="维护中" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedLaboratory"
            placeholder="筛选实验室"
            clearable
            @change="handleLaboratoryFilter"
          >
            <el-option
              v-for="lab in laboratories"
              :key="lab.id"
              :label="lab.name"
              :value="lab.id"
            />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 分区表格 -->
    <el-table
      :data="sections"
      v-loading="loading"
      stripe
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column
        prop="code"
        label="分区编号"
        width="120"
        sortable="custom"
      />
      <el-table-column
        prop="name"
        label="分区名称"
        min-width="150"
        sortable="custom"
      />
      <el-table-column
        prop="storage_device_name"
        label="所属装置"
        width="150"
        sortable="custom"
      />
      <el-table-column
        prop="position"
        label="位置"
        width="120"
        sortable="custom"
      />
      <el-table-column prop="status" label="状态" width="100" sortable="custom">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" size="small">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="security_level"
        label="安全等级"
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          <el-tag
            :type="getSecurityLevelType(scope.row.security_level)"
            size="small"
          >
            {{ scope.row.security_level }}级
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="容量使用" width="150">
        <template #default="scope">
          <div class="capacity-info">
            <div class="capacity-text">
              {{ scope.row.used_capacity || 0 }} / {{ scope.row.capacity || 0 }}
            </div>
            <el-progress
              :percentage="getCapacityPercentage(scope.row)"
              :color="getCapacityColor(scope.row)"
              :stroke-width="6"
              :show-text="false"
            />
          </div>
        </template>
      </el-table-column>
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
      <el-table-column
        prop="created_at"
        label="创建时间"
        width="160"
        sortable="custom"
      >
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
          <el-button size="small" @click="editSection(scope.row)">
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteSection(scope.row)"
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
      :title="editingSection ? '编辑分区' : '新增分区'"
      width="600px"
      :before-close="handleClose"
    >
      <el-form
        ref="sectionFormRef"
        :model="sectionForm"
        :rules="sectionRules"
        label-width="100px"
      >
        <el-form-item label="分区编号" prop="code">
          <el-input v-model="sectionForm.code" placeholder="请输入分区编号" />
        </el-form-item>

        <el-form-item label="分区名称" prop="name">
          <el-input v-model="sectionForm.name" placeholder="请输入分区名称" />
        </el-form-item>

        <el-form-item label="存储装置" prop="storage_id">
          <el-row :gutter="12" style="width: 600px">
            <el-col :span="12">
              <div class="select-label">实验室</div>
              <el-select
                v-model="sectionForm.laboratory_id"
                placeholder="选择实验室"
                @change="onLaboratoryChange"
                style="width: 100%"
                size="default"
              >
                <el-option
                  v-for="lab in laboratories"
                  :key="lab.id"
                  :label="lab.name"
                  :value="lab.id"
                />
              </el-select>
            </el-col>
            <el-col :span="12">
              <div class="select-label">存储装置</div>
              <el-select
                v-model="sectionForm.storage_id"
                placeholder="选择存储装置"
                :disabled="!sectionForm.laboratory_id"
                style="width: 100%"
                size="default"
              >
                <el-option
                  v-for="device in storageDevices"
                  :key="device?.id"
                  :label="device?.name"
                  :value="device?.id"
                />
              </el-select>
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item label="位置" prop="position">
          <el-input
            v-model="sectionForm.position"
            placeholder="请输入分区位置"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="sectionForm.status" style="width: 100%">
            <el-option label="可用" value="可用" />
            <el-option label="已满" value="已满" />
            <el-option label="维护中" value="维护中" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>

        <el-form-item label="安全等级" prop="security_level">
          <el-select
            v-model="sectionForm.security_level"
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
            v-model="sectionForm.capacity"
            :min="0"
            :max="999999"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="已用容量">
          <el-input-number
            v-model="sectionForm.used_capacity"
            :min="0"
            :max="sectionForm.capacity || 999999"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="sectionForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分区描述"
          />
        </el-form-item>

        <el-form-item label="自定义属性">
          <PropertyEditor
            v-model="sectionForm.properties"
            title="分区属性"
            :show-json-editor="true"
            :max-properties="20"
            @validate="handleSectionPropertyValidation"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="saveSection" :loading="saving">
            {{ editingSection ? "更新" : "创建" }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 属性查看对话框 -->
    <el-dialog v-model="showPropertiesDialog" title="分区属性" width="500px">
      <div v-if="selectedSectionProperties">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in selectedSectionProperties"
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
const sections = ref([]);
const storageDevices = ref([]);
const laboratories = ref([]); // 新增实验室列表
const searchQuery = ref("");
const selectedDevice = ref("");
const selectedStatus = ref("");
const selectedLaboratory = ref(""); // 新增：选中的实验室
const showCreateDialog = ref(false);
const showPropertiesDialog = ref(false);
const editingSection = ref(null);
const sectionFormRef = ref();
const selectedSectionProperties = ref(null);
const sectionPropertyValidation = ref({ isValid: true, errors: [] }); // 新增属性验证状态
const sortBy = ref(""); // 新增：排序字段
const sortDesc = ref(false); // 新增：排序顺序

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const totalPages = ref(0);

// 表单数据
const sectionForm = reactive({
  code: "",
  name: "",
  laboratory_id: "", // 新增实验室ID字段
  storage_id: "", // 使用与后端JSON标签一致的字段名
  position: "",
  status: "可用",
  security_level: 1,
  capacity: 0,
  used_capacity: 0,
  description: "",
  properties: {},
});

// 表单验证规则
const sectionRules = {
  code: [
    { required: true, message: "请输入分区编号", trigger: "blur" },
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" },
  ],
  name: [
    { required: true, message: "请输入分区名称", trigger: "blur" },
    { min: 2, max: 100, message: "长度在 2 到 100 个字符", trigger: "blur" },
  ],
  storage_id: [
    { required: true, message: "请选择存储装置", trigger: "change" },
  ],
  position: [{ required: true, message: "请输入分区位置", trigger: "blur" }],
  status: [{ required: true, message: "请选择分区状态", trigger: "change" }],
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

// 方法
const fetchSections = async () => {
  loading.value = true;
  try {
    const maxPageSize = 100;
    const params = {
      page: currentPage.value,
      page_size: Math.min(pageSize.value, maxPageSize),
      search: searchQuery.value,
      storage_id: selectedDevice.value,
      laboratory_id: selectedLaboratory.value,
      status: selectedStatus.value,
      sort_by: sortBy.value || undefined,
      sort_desc: sortBy.value ? sortDesc.value : undefined,
    };
    // 清理空参数
    Object.keys(params).forEach(
      (k) => (params[k] === "" || params[k] == null) && delete params[k]
    );
    const response = await api.get("/sections", { params });
    // 兼容后端分页结构
    const d = response.data;
    if (d && Array.isArray(d.data)) {
      sections.value = d.data.map((section) => ({
        ...section,
        storage_device_name: section.storage?.name || "未知装置",
      }));
      total.value = d.total || 0;
      totalPages.value = d.total_pages || 0;
      currentPage.value = d.page || 1;
      pageSize.value = d.page_size || pageSize.value;
    } else {
      sections.value = [];
      total.value = 0;
    }
  } catch (error) {
    ElMessage.error("获取分区列表失败");
    console.error("Error fetching sections:", error);
  } finally {
    loading.value = false;
  }
};

const fetchLaboratories = async () => {
  try {
    const maxPageSize = 100;
    const params = { page: 1, page_size: maxPageSize };
    const response = await api.get("/laboratories", { params });
    laboratories.value = response.data.data || response.data.laboratories || [];
  } catch (error) {
    console.error("获取实验室失败:", error);
    laboratories.value = [];
  }
};

const fetchStorageDevices = async () => {
  try {
    const maxPageSize = 100;
    const params = { page: 1, page_size: maxPageSize };
    const response = await api.get("/storages", { params });
    storageDevices.value = response.data.data || response.data.storages || [];
  } catch (error) {
    console.error("Error fetching storage devices:", error);
    storageDevices.value = [];
  }
};

const onLaboratoryChange = async (labId) => {
  sectionForm.storage_id = "";
  storageDevices.value = [];

  if (labId) {
    try {
      const response = await api.get("/storages", {
        params: { laboratory_id: labId, page: 1, page_size: 100 },
      });
      console.log("Storages response:", response.data.data);

      // 处理不同的数据格式
      let allStorages = response.data.data;

      storageDevices.value = allStorages.filter(
        (storage) => storage.lab_id === labId
      );
    } catch (error) {
      console.error("获取存储装置失败:", error);
    }
  }
};

// 搜索和筛选事件
const handleSearch = () => {
  currentPage.value = 1;
  fetchSections();
};
const handleDeviceFilter = () => {
  currentPage.value = 1;
  fetchSections();
};
const handleStatusFilter = () => {
  currentPage.value = 1;
  fetchSections();
};
const handleLaboratoryFilter = () => {
  currentPage.value = 1;
  fetchSections();
};
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchSections();
};
const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchSections();
};
// 新增：表格排序事件，联动后端
const handleSortChange = (sort) => {
  if (!sort || !sort.prop) {
    sortBy.value = "";
    sortDesc.value = false;
  } else {
    sortBy.value = sort.prop;
    sortDesc.value = sort.order === "descending";
  }
  currentPage.value = 1;
  fetchSections();
};

const getStatusType = (status) => {
  const statusMap = {
    可用: "success",
    已满: "warning",
    维护中: "info",
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

const getCapacityPercentage = (section) => {
  if (!section.capacity || section.capacity === 0) return 0;
  return Math.round(((section.used_capacity || 0) / section.capacity) * 100);
};

const getCapacityColor = (section) => {
  const percentage = getCapacityPercentage(section);
  if (percentage >= 90) return "#f56c6c";
  if (percentage >= 70) return "#e6a23c";
  return "#67c23a";
};

const formatDate = (dateString) => {
  if (!dateString) return "未知";
  return new Date(dateString).toLocaleString("zh-CN");
};

const resetForm = () => {
  Object.assign(sectionForm, {
    code: "",
    name: "",
    laboratory_id: "",
    storage_id: "",
    position: "",
    status: "可用",
    security_level: 1,
    capacity: 0,
    used_capacity: 0,
    description: "",
    properties: {},
  });
  editingSection.value = null;
  if (sectionFormRef.value) {
    sectionFormRef.value.resetFields();
  }
};

const editSection = async (section) => {
  // 先重置表单，但不重置 editingSection
  Object.assign(sectionForm, {
    code: "",
    name: "",
    laboratory_id: "",
    storage_id: "",
    position: "",
    status: "可用",
    security_level: 1,
    capacity: 0,
    used_capacity: 0,
    description: "",
    properties: {},
  });
  if (sectionFormRef.value) {
    sectionFormRef.value.resetFields();
  }

  // 设置编辑状态
  editingSection.value = section;

  // 只提取表单需要的字段，避免赋值嵌套对象
  Object.assign(sectionForm, {
    code: section.code || "",
    name: section.name || "",
    storage_id: section.storage_id || "",
    position: section.position || "",
    status: section.status || "可用",
    security_level: section.security_level || 1,
    capacity: section.capacity || 0,
    used_capacity: section.used_capacity || 0,
    description: section.description || "",
    properties: JSON.parse(JSON.stringify(section.properties || {})), // 深拷贝
  });

  // 如果分区有存储装置，需要先加载实验室数据并选中对应的实验室
  if (section.storage_id && section.storage) {
    const labId = section.storage.lab_id;
    if (labId) {
      sectionForm.laboratory_id = labId;
      // 加载该实验室下的存储装置
      await onLaboratoryChange(labId);
      // 设置存储装置ID
      sectionForm.storage_id = section.storage_id;
    }
  }

  showCreateDialog.value = true;
};

const saveSection = async () => {
  if (!sectionFormRef.value) return;

  const valid = await sectionFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 验证属性
  if (!sectionPropertyValidation.value.isValid) {
    ElMessage.error(
      `属性配置有误：${sectionPropertyValidation.value.errors.join(", ")}`
    );
    return;
  }

  saving.value = true;
  try {
    // 只提取后端需要的字段，过滤掉冗余字段
    const data = {
      code: sectionForm.code,
      name: sectionForm.name,
      storage_id: sectionForm.storage_id,
      position: sectionForm.position,
      status: sectionForm.status,
      security_level: sectionForm.security_level,
      capacity: sectionForm.capacity,
      used_capacity: sectionForm.used_capacity,
      description: sectionForm.description,
      properties: sectionForm.properties,
    };

    console.log("Saving section data:", data);

    if (editingSection.value) {
      await api.put(`/admin/sections/${editingSection.value.id}`, data);
      ElMessage.success("更新分区成功");
    } else {
      await api.post("/admin/sections", data);
      ElMessage.success("创建分区成功");
    }

    showCreateDialog.value = false;
    resetForm();
    fetchSections();
  } catch (error) {
    ElMessage.error(editingSection.value ? "更新分区失败" : "创建分区失败");
    console.error("Error saving section:", error);
  } finally {
    saving.value = false;
  }
};

const deleteSection = async (section) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分区 "${section.name}" 吗？此操作不可撤销。`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/admin/sections/${section.id}`);
    ElMessage.success("删除分区成功");
    fetchSections();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除分区失败");
      console.error("Error deleting section:", error);
    }
  }
};

const showProperties = (section) => {
  selectedSectionProperties.value = section.properties;
  showPropertiesDialog.value = true;
};

const handleClose = () => {
  showCreateDialog.value = false;
  resetForm();
};

// 处理分区属性验证
const handleSectionPropertyValidation = (validation) => {
  sectionPropertyValidation.value = validation;
};

// 生命周期
onMounted(() => {
  fetchSections();
  fetchLaboratories();
  fetchStorageDevices();
});
</script>

<style scoped>
.sections {
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

.capacity-info {
  width: 100%;
}

.capacity-text {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  text-align: center;
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

.select-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  font-weight: 500;
}
</style>
