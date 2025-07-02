<template>
  <div class="movement-history">
    <div class="page-header">
      <h2>移动记录</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
          记录移动
        </el-button>
        <el-button
          type="success"
          @click="exportRecords"
          :icon="Download"
          :loading="exporting"
        >
          导出记录
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="5">
          <el-input
            v-model="searchQuery"
            placeholder="搜索物品名称"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedUser"
            placeholder="筛选操作人"
            clearable
            @change="handleUserFilter"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.real_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedType"
            placeholder="筛选移动类型"
            clearable
            @change="handleTypeFilter"
          >
            <el-option label="入库" value="入库" />
            <el-option label="出库" value="出库" />
            <el-option label="转移" value="转移" />
            <el-option label="盘点" value="盘点" />
            <el-option label="损坏" value="损坏" />
            <el-option label="报废" value="报废" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleDateFilter"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 移动记录表格 -->
    <el-table :data="movements" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="item_name" label="物品名称" min-width="150" />
      <el-table-column prop="movement_type" label="移动类型" width="100">
        <template #default="scope">
          <el-tag
            :type="getMovementTypeTag(scope.row.movement_type)"
            size="small"
          >
            {{ scope.row.movement_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="from_location" label="源位置" min-width="120" />
      <el-table-column prop="to_location" label="目标位置" min-width="120" />
      <el-table-column prop="quantity" label="数量" width="80" />
      <el-table-column prop="reason" label="原因" min-width="150" />
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="created_at" label="时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
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

    <!-- 创建移动记录对话框 -->
    <el-dialog v-model="showCreateDialog" title="记录移动" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="物品" prop="item_id">
          <el-select
            v-model="form.item_id"
            placeholder="选择物品"
            filterable
            remote
            :remote-method="searchItems"
            :loading="searchingItems"
            style="width: 100%"
          >
            <el-option
              v-for="item in searchableItems"
              :key="item.id"
              :label="`${item.name} (${item.code})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="移动类型" prop="movement_type">
          <el-select v-model="form.movement_type" style="width: 100%">
            <el-option label="入库" value="入库" />
            <el-option label="出库" value="出库" />
            <el-option label="转移" value="转移" />
            <el-option label="盘点" value="盘点" />
            <el-option label="损坏" value="损坏" />
            <el-option label="报废" value="报废" />
          </el-select>
        </el-form-item>

        <el-form-item label="数量" prop="quantity">
          <el-input-number
            v-model="form.quantity"
            :min="1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="源位置">
          <el-input v-model="form.from_location" placeholder="请输入源位置" />
        </el-form-item>

        <el-form-item label="目标位置">
          <el-input v-model="form.to_location" placeholder="请输入目标位置" />
        </el-form-item>

        <el-form-item label="原因" prop="reason">
          <el-input v-model="form.reason" placeholder="请输入移动原因" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveMovement">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Plus, Download, Search } from "@element-plus/icons-vue";
import api from "@/services/api";

// 响应式数据
const loading = ref(false);
const exporting = ref(false);
const saving = ref(false);
const searchingItems = ref(false);
const movements = ref([]);
const users = ref([]);
const searchableItems = ref([]);
const showCreateDialog = ref(false);

// 搜索和筛选
const searchQuery = ref("");
const selectedUser = ref("");
const selectedType = ref("");
const dateRange = ref([]);

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 表单数据
const formRef = ref();
const form = reactive({
  item_id: null,
  movement_type: "",
  quantity: 1,
  from_location: "",
  to_location: "",
  reason: "",
  notes: "",
});

const rules = {
  item_id: [{ required: true, message: "请选择物品", trigger: "change" }],
  movement_type: [
    { required: true, message: "请选择移动类型", trigger: "change" },
  ],
  quantity: [{ required: true, message: "请输入数量", trigger: "blur" }],
  reason: [{ required: true, message: "请输入移动原因", trigger: "blur" }],
};

// 方法
const fetchMovements = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
    };

    if (selectedUser.value) {
      params.user_id = selectedUser.value;
    }
    if (selectedType.value) {
      params.movement_type = selectedType.value;
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split("T")[0];
      params.end_date = dateRange.value[1].toISOString().split("T")[0];
    }

    const response = await api.get("/movements", { params });
    if (response.data && Array.isArray(response.data.data)) {
      movements.value = response.data.data;
      total.value = response.data.total || 0;
    } else {
      movements.value = [];
      total.value = 0;
    }
  } catch (error) {
    ElMessage.error("获取移动记录失败");
    console.error("Error fetching movements:", error);
    movements.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchUsers = async () => {
  try {
    const response = await api.get("/admin/users");
    users.value = response.data.data || [];
  } catch (error) {
    console.error("Error fetching users:", error);
  }
};

const searchItems = async (query) => {
  if (!query) {
    searchableItems.value = [];
    return;
  }

  searchingItems.value = true;
  try {
    const response = await api.get("/items", {
      params: { search: query, page: 1, page_size: 20 },
    });
    searchableItems.value = response.data.data || [];
  } catch (error) {
    console.error("Error searching items:", error);
  } finally {
    searchingItems.value = false;
  }
};

const saveMovement = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    saving.value = true;

    await api.post("/movements", form);
    ElMessage.success("记录成功");
    showCreateDialog.value = false;
    resetForm();
    fetchMovements();
  } catch (error) {
    ElMessage.error("记录失败");
    console.error("Error saving movement:", error);
  } finally {
    saving.value = false;
  }
};

const resetForm = () => {
  Object.assign(form, {
    item_id: null,
    movement_type: "",
    quantity: 1,
    from_location: "",
    to_location: "",
    reason: "",
    notes: "",
  });
  searchableItems.value = [];
  formRef.value?.resetFields();
};

const exportRecords = async () => {
  exporting.value = true;
  try {
    const response = await api.get("/movements/export", {
      responseType: "blob",
    });

    const blob = new Blob([response.data], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `movements_${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);

    ElMessage.success("导出成功");
  } catch (error) {
    ElMessage.error("导出失败");
    console.error("Error exporting records:", error);
  } finally {
    exporting.value = false;
  }
};

const getMovementTypeTag = (type) => {
  switch (type) {
    case "入库":
      return "success";
    case "出库":
      return "danger";
    case "转移":
      return "warning";
    case "盘点":
      return "info";
    case "损坏":
    case "报废":
      return "danger";
    default:
      return "info";
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString("zh-CN");
};

// 筛选和分页处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchMovements();
};

const handleUserFilter = () => {
  currentPage.value = 1;
  fetchMovements();
};

const handleTypeFilter = () => {
  currentPage.value = 1;
  fetchMovements();
};

const handleDateFilter = () => {
  currentPage.value = 1;
  fetchMovements();
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchMovements();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchMovements();
};

onMounted(() => {
  fetchMovements();
  fetchUsers();
});
</script>

<style scoped>
.movement-history {
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
