<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实验室管理</span>
          <el-button
            v-if="authStore.isAdmin"
            type="primary"
            :icon="Plus"
            @click="showDialog = true"
          >
            新建实验室
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索实验室名称或编号"
          :prefix-icon="Search"
          style="width: 300px"
          @input="handleSearch"
        />
      </div>

      <!-- 表格 -->
      <el-table :data="filteredLaboratories" v-loading="loading">
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="location" label="位置" />
        <el-table-column
          prop="description"
          label="描述"
          show-overflow-tooltip
        />
        <el-table-column prop="security_level" label="安全等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getSecurityLevelType(row.security_level)">
              {{ row.security_level }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="存储装置数" width="120">
          <template #default="{ row }">
            {{ row.storages?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="authStore.isAdmin"
          label="操作"
          width="180"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="table-actions">
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="editLaboratory(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="deleteLaboratory(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingLab ? '编辑实验室' : '新建实验室'"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="编号" prop="code">
          <el-input v-model="form.code" placeholder="请输入实验室编号" />
        </el-form-item>

        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入实验室名称" />
        </el-form-item>

        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入实验室位置" />
        </el-form-item>

        <el-form-item label="安全等级" prop="security_level">
          <el-select v-model="form.security_level" placeholder="选择安全等级">
            <el-option
              v-for="level in securityLevels"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入实验室描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ editingLab ? "更新" : "创建" }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Search, Edit, Delete } from "@element-plus/icons-vue";

const authStore = useAuthStore();

const laboratories = ref([]);
const loading = ref(false);
const showDialog = ref(false);
const submitting = ref(false);
const editingLab = ref(null);
const searchQuery = ref("");
const formRef = ref();
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const totalPages = ref(0);

const form = reactive({
  code: "",
  name: "",
  location: "",
  description: "",
  security_level: 1,
});

const rules = {
  code: [{ required: true, message: "请输入实验室编号", trigger: "blur" }],
  name: [{ required: true, message: "请输入实验室名称", trigger: "blur" }],
  location: [{ required: true, message: "请输入实验室位置", trigger: "blur" }],
  security_level: [
    { required: true, message: "请选择安全等级", trigger: "change" },
  ],
};

const securityLevels = [
  { value: 1, label: "1级 - 公开访问（任何人都可以接触）" },
  { value: 2, label: "2级 - 低保密性（一般工作人员可访问）" },
  { value: 3, label: "3级 - 中等保密性（授权人员可访问）" },
  { value: 4, label: "4级 - 高保密性（特定权限人员可访问）" },
  { value: 5, label: "5级 - 极端保密（最高权限人员可访问）" },
];

const filteredLaboratories = computed(() => {
  if (!searchQuery.value) return laboratories.value;

  const query = searchQuery.value.toLowerCase();
  return laboratories.value.filter(
    (lab) =>
      lab.name.toLowerCase().includes(query) ||
      lab.code.toLowerCase().includes(query)
  );
});

const fetchLaboratories = async () => {
  try {
    loading.value = true;
    // 必须传递分页参数，防止后端校验失败
    const params = {
      page: currentPage?.value || 1,
      page_size: pageSize?.value || 20,
    };
    const response = await api.get("/laboratories", { params });
    // 兼容后端分页结构
    if (Array.isArray(response.data.data)) {
      laboratories.value = response.data.data;
      total.value = response.data.total || 0;
      totalPages.value = response.data.total_pages || 0;
      currentPage.value = response.data.page || 1;
      pageSize.value = response.data.page_size || pageSize.value;
    } else if (Array.isArray(response.data.laboratories)) {
      laboratories.value = response.data.laboratories;
      total.value = laboratories.value.length;
    } else {
      laboratories.value = [];
      total.value = 0;
    }
  } catch (error) {
    ElMessage.error("获取实验室列表失败");
  } finally {
    loading.value = false;
  }
};

// 分页事件联动
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchLaboratories();
};
const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchLaboratories();
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

const editLaboratory = (lab) => {
  editingLab.value = lab;
  // 只提取表单需要的字段，避免赋值嵌套对象
  Object.assign(form, {
    code: lab.code || "",
    name: lab.name || "",
    location: lab.location || "",
    description: lab.description || "",
    security_level: lab.security_level || 1,
  });
  showDialog.value = true;
};

const deleteLaboratory = async (lab) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除实验室"${lab.name}"吗？`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/admin/laboratories/${lab.id}`);
    ElMessage.success("删除成功");
    fetchLaboratories();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error.response?.data?.error || "删除失败");
    }
  }
};

const submitForm = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    submitting.value = true;

    if (editingLab.value) {
      await api.put(`/admin/laboratories/${editingLab.value.id}`, form);
      ElMessage.success("更新成功");
    } else {
      await api.post("/admin/laboratories", form);
      ElMessage.success("创建成功");
    }

    showDialog.value = false;
    fetchLaboratories();
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error);
    }
  } finally {
    submitting.value = false;
  }
};

const resetForm = () => {
  editingLab.value = null;
  Object.assign(form, {
    code: "",
    name: "",
    location: "",
    description: "",
    security_level: 1,
  });
  formRef.value?.resetFields();
};

const handleSearch = () => {
  // 搜索逻辑由计算属性处理
};

onMounted(() => {
  fetchLaboratories();
});
</script>

<style scoped>
.search-bar {
  margin-bottom: 20px;
}
</style>
