<template>
  <div class="items">
    <div class="page-header">
      <h2>物品管理</h2>
      <el-button
        type="primary"
        @click="showDialog = true"
        :icon="Plus"
        v-if="canCreate('items')"
      >
        新增物品
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索物品名称或编号"
            :prefix-icon="Search"
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="filterCategory"
            placeholder="选择类别"
            clearable
            @change="handleCategoryFilter"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="filterSection"
            placeholder="选择分区"
            clearable
            @change="handleSectionFilter"
          >
            <el-option
              v-for="section in sections"
              :key="section.id"
              :label="`${section.name} (${section.storage?.name})`"
              :value="section.id"
            />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-checkbox v-model="showLowStock" @change="handleLowStockFilter">
            仅显示低库存
          </el-checkbox>
        </el-col>
        <el-col :span="3">
          <el-checkbox v-model="showExpiring" @change="handleExpiringFilter">
            即将过期
          </el-checkbox>
        </el-col>
      </el-row>
    </div>

    <!-- 表格和移动端卡片视图 -->
    <div class="table-container" :class="{ 'mobile-card-view': isMobile }">
      <!-- 桌面端表格 -->
      <el-table
        :data="items"
        v-loading="loading"
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column label="编号" min-width="120">
          <template #default="{ row }">
            {{ row.item?.code || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="名称" min-width="180">
          <template #default="{ row }">
            {{ row.item?.name || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="类别" min-width="120">
          <template #default="{ row }">
            {{ row.item?.category || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="位置" min-width="250">
          <template #default="{ row }">
            <div v-if="row.section">
              <div>
                {{ row.section.storage?.laboratory?.name || "未知实验室" }}
              </div>
              <el-text type="info" size="small">
                {{ row.section.storage?.name || "未知装置" }} →
                {{ row.section.name || "未知分区" }}
              </el-text>
            </div>
            <div v-else class="text-placeholder">未设置位置</div>
          </template>
        </el-table-column>
        <el-table-column label="库存" min-width="200">
          <template #default="{ row }">
            <div class="quantity-controls">
              <div class="quantity-info">
                <span
                  :class="{
                    'low-stock': row.item?.quantity <= row.item?.min_quantity,
                  }"
                >
                  {{ row.item?.quantity || 0 }} {{ row.item?.unit || "" }}
                </span>
                <el-text type="info" size="small">
                  最低: {{ row.item?.min_quantity || 0 }}
                </el-text>
              </div>
              <div class="quantity-buttons">
                <el-button
                  size="small"
                  type="success"
                  :icon="Plus"
                  @click="adjustQuantity(row, 1)"
                  :loading="row.adjusting"
                  title="增加库存"
                />
                <el-button
                  size="small"
                  type="warning"
                  :icon="Minus"
                  @click="adjustQuantity(row, -1)"
                  :loading="row.adjusting"
                  :disabled="(row.item?.quantity || 0) <= 0"
                  title="减少库存"
                />
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="价格" min-width="100">
          <template #default="{ row }"> ¥{{ row.item?.price || 0 }} </template>
        </el-table-column>
        <el-table-column label="状态" min-width="160">
          <template #default="{ row }">
            <div class="status-tags">
              <el-tag
                v-if="row.item?.quantity <= row.item?.min_quantity"
                type="warning"
                size="small"
                effect="dark"
              >
                <el-icon><WarningFilled /></el-icon>
                低库存
              </el-tag>
              <el-tag
                v-if="isExpiring(row.item?.expiry_date)"
                type="danger"
                size="small"
                effect="dark"
              >
                <el-icon><AlarmClock /></el-icon>
                即将过期
              </el-tag>
              <el-tag
                v-if="isExpired(row.item?.expiry_date)"
                type="danger"
                size="small"
                effect="dark"
              >
                <el-icon><CircleCloseFilled /></el-icon>
                已过期
              </el-tag>
              <el-tag
                v-if="!row.item?.quantity || row.item.quantity === 0"
                type="info"
                size="small"
                effect="plain"
              >
                缺货
              </el-tag>
              <span
                v-if="
                  !isExpiring(row.item?.expiry_date) &&
                  !isExpired(row.item?.expiry_date) &&
                  row.item?.quantity > row.item?.min_quantity
                "
                class="status-normal"
              >
                正常
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="180"
          fixed="right"
          v-if="canUpdate('items') || canDelete('items')"
        >
          <template #default="{ row }">
            <div class="table-actions">
              <el-button
                type="primary"
                size="small"
                :icon="View"
                @click="viewItem(row)"
              >
                详情
              </el-button>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="editItem(row)"
                v-if="canUpdate('items')"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="deleteItem(row)"
                v-if="canDelete('items')"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 移动端卡片视图 -->
      <div class="mobile-cards" v-if="isMobile">
        <div v-for="row in items" :key="row.id" class="mobile-card">
          <div class="mobile-card-header">
            <div class="mobile-card-title">{{ row.item?.name || "-" }}</div>
            <div class="mobile-card-code">{{ row.item?.code || "-" }}</div>
          </div>

          <div class="mobile-card-content">
            <div class="mobile-card-field">
              <span class="mobile-card-label">类别:</span>
              <span class="mobile-card-value">{{
                row.item?.category || "-"
              }}</span>
            </div>

            <div class="mobile-card-field">
              <span class="mobile-card-label">位置:</span>
              <span class="mobile-card-value">
                <div v-if="row.section">
                  <div>
                    {{ row.section.storage?.laboratory?.name || "未知实验室" }}
                  </div>
                  <div style="font-size: 12px; color: #909399">
                    {{ row.section.storage?.name || "未知装置" }} →
                    {{ row.section.name || "未知分区" }}
                  </div>
                </div>
                <span v-else>未设置位置</span>
              </span>
            </div>

            <div class="mobile-card-field">
              <span class="mobile-card-label">库存:</span>
              <span class="mobile-card-value">
                <span
                  :class="{
                    'low-stock': row.item?.quantity <= row.item?.min_quantity,
                  }"
                >
                  {{ row.item?.quantity || 0 }} {{ row.item?.unit || "" }}
                </span>
                <div style="font-size: 12px; color: #909399">
                  最低: {{ row.item?.min_quantity || 0 }}
                </div>
              </span>
            </div>

            <div class="mobile-card-field">
              <span class="mobile-card-label">价格:</span>
              <span class="mobile-card-value">¥{{ row.item?.price || 0 }}</span>
            </div>

            <div class="mobile-card-field">
              <span class="mobile-card-label">状态:</span>
              <span class="mobile-card-value">
                <div class="status-tags">
                  <el-tag
                    v-if="row.item?.quantity <= row.item?.min_quantity"
                    type="warning"
                    size="small"
                    effect="dark"
                  >
                    低库存
                  </el-tag>
                  <el-tag
                    v-if="isExpiring(row.item?.expiry_date)"
                    type="danger"
                    size="small"
                    effect="dark"
                  >
                    即将过期
                  </el-tag>
                  <el-tag
                    v-if="isExpired(row.item?.expiry_date)"
                    type="danger"
                    size="small"
                    effect="dark"
                  >
                    已过期
                  </el-tag>
                  <el-tag
                    v-if="!row.item?.quantity || row.item.quantity === 0"
                    type="info"
                    size="small"
                    effect="plain"
                  >
                    缺货
                  </el-tag>
                  <span
                    v-if="
                      !isExpiring(row.item?.expiry_date) &&
                      !isExpired(row.item?.expiry_date) &&
                      row.item?.quantity > row.item?.min_quantity
                    "
                    class="status-normal"
                  >
                    正常
                  </span>
                </div>
              </span>
            </div>
          </div>

          <div class="mobile-card-actions">
            <!-- 库存调整按钮 -->
            <el-button
              size="small"
              type="success"
              :icon="Plus"
              @click="adjustQuantity(row, 1)"
              :loading="row.adjusting"
              title="增加库存"
            />
            <el-button
              size="small"
              type="warning"
              :icon="Minus"
              @click="adjustQuantity(row, -1)"
              :loading="row.adjusting"
              :disabled="(row.item?.quantity || 0) <= 0"
              title="减少库存"
            />

            <!-- 操作按钮 -->
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="viewItem(row)"
            >
              详情
            </el-button>
            <el-button
              type="primary"
              size="small"
              :icon="Edit"
              @click="editItem(row)"
              v-if="canUpdate('items')"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="deleteItem(row)"
              v-if="canDelete('items')"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

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

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingItem ? '编辑物品' : '新增物品'"
      width="900px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <div class="form-section">
          <div class="form-section-title">基本信息</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="编号" prop="code">
                <el-input v-model="form.code" placeholder="请输入物品编号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入物品名称" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="类别" prop="category">
                <el-input
                  v-model="form.category"
                  placeholder="请输入物品类别"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="单位" prop="unit">
                <el-input
                  v-model="form.unit"
                  placeholder="如：个、瓶、毫升等"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="描述">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入物品描述"
            />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="form-section-title">库存信息</div>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="当前数量" prop="quantity">
                <el-input-number
                  v-model="form.quantity"
                  :min="0"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="最低库存" prop="min_quantity">
                <el-input-number
                  v-model="form.min_quantity"
                  :min="0"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="价格" prop="price">
                <el-input-number
                  v-model="form.price"
                  :min="0"
                  :precision="2"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="存放位置" prop="section_id">
                <el-row :gutter="12" style="width: 600px">
                  <el-col :span="8">
                    <div class="select-label">实验室</div>
                    <el-select
                      v-model="form.laboratory_id"
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
                  <el-col :span="8">
                    <div class="select-label">存储装置</div>
                    <el-select
                      v-model="form.storage_id"
                      placeholder="选择存储装置"
                      @change="onStorageChange"
                      :disabled="!form.laboratory_id"
                      style="width: 100%"
                      size="default"
                    >
                      <el-option
                        v-for="storage in storages"
                        :key="storage.id"
                        :label="storage.name"
                        :value="storage.id"
                      />
                    </el-select>
                  </el-col>
                  <el-col :span="8">
                    <div class="select-label">分区</div>
                    <el-select
                      v-model="form.section_id"
                      placeholder="选择分区"
                      :disabled="!form.storage_id"
                      style="width: 100%"
                      size="default"
                    >
                      <el-option
                        v-for="section in sections"
                        :key="section.id"
                        :label="section.name"
                        :value="section.id"
                      />
                    </el-select>
                  </el-col>
                </el-row>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="供应商">
                <el-input v-model="form.supplier" placeholder="请输入供应商" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="采购日期">
                <el-date-picker
                  v-model="form.purchase_date"
                  type="date"
                  placeholder="选择采购日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="过期日期">
                <el-date-picker
                  v-model="form.expiry_date"
                  type="date"
                  placeholder="选择过期日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="form-section-title">自定义属性</div>
          <PropertyEditor
            v-model="form.properties"
            title="物品属性"
            :show-json-editor="true"
            :max-properties="20"
            @validate="handlePropertyValidation"
          />
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ editingItem ? "更新" : "创建" }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="物品详情" width="600px">
      <div v-if="viewingItem" class="item-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="编号">
            {{ viewingItem.item.code }}
          </el-descriptions-item>
          <el-descriptions-item label="名称">
            {{ viewingItem.item.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类别">
            {{ viewingItem.item.category }}
          </el-descriptions-item>
          <el-descriptions-item label="单位">
            {{ viewingItem.item.unit }}
          </el-descriptions-item>
          <el-descriptions-item label="当前库存">
            <span
              :class="{
                'low-stock':
                  viewingItem.item.quantity <= viewingItem.item.min_quantity,
              }"
            >
              {{ viewingItem.item.quantity }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="最低库存">
            {{ viewingItem.item.min_quantity }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">
            ¥{{ viewingItem.item.price }}
          </el-descriptions-item>
          <el-descriptions-item label="供应商">
            {{ viewingItem.item.supplier || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="采购日期">
            {{ formatDate(viewingItem.item.purchase_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="过期日期">
            <span>{{ formatDate(viewingItem.item.expiry_date) }}</span>
            <el-tag
              v-if="isExpired(viewingItem.item.expiry_date)"
              type="danger"
              size="small"
              style="margin-left: 8px"
            >
              已过期
            </el-tag>
            <el-tag
              v-else-if="isExpiring(viewingItem.item.expiry_date)"
              type="warning"
              size="small"
              style="margin-left: 8px"
            >
              即将过期
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态" span="2">
            <div class="detail-status">
              <el-tag
                v-if="
                  viewingItem.item.quantity <= viewingItem.item.min_quantity
                "
                type="warning"
                size="small"
              >
                低库存
              </el-tag>
              <el-tag
                v-if="isExpiring(viewingItem.item.expiry_date)"
                type="danger"
                size="small"
              >
                即将过期
              </el-tag>
              <el-tag
                v-if="isExpired(viewingItem.item.expiry_date)"
                type="danger"
                size="small"
              >
                已过期
              </el-tag>
              <span
                v-if="
                  !isExpiring(viewingItem.item.expiry_date) &&
                  !isExpired(viewingItem.item.expiry_date) &&
                  viewingItem.item.quantity > viewingItem.item.min_quantity
                "
                style="color: #67c23a; font-weight: 500"
              >
                正常
              </span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="位置" span="2">
            {{ viewingItem.location?.full_path || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" span="2">
            {{ viewingItem.item.description || "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <div
          v-if="
            viewingItem.item.properties &&
            Object.keys(viewingItem.item.properties).length > 0
          "
          class="properties-section"
        >
          <h4>自定义属性</h4>
          <div class="properties-display">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item
                v-for="[key, value] in Object.entries(
                  viewingItem.item.properties
                )"
                :key="key"
                :label="key"
              >
                <span v-if="Array.isArray(value)" class="array-value">
                  <el-tag
                    v-for="(item, index) in value"
                    :key="index"
                    size="small"
                    type="info"
                    class="array-tag"
                  >
                    {{ item }}
                  </el-tag>
                </span>
                <el-tag
                  v-else-if="typeof value === 'boolean'"
                  :type="value ? 'success' : 'danger'"
                  size="small"
                >
                  {{ value ? "是" : "否" }}
                </el-tag>
                <span
                  v-else-if="typeof value === 'number'"
                  class="number-value"
                  >{{ value }}</span
                >
                <span v-else>{{ value }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  computed,
  onMounted,
  onBeforeUnmount,
  nextTick,
} from "vue";
import { useAuthStore } from "@/stores/auth";
import { usePermissions } from "@/composables/usePermissions";
import api from "@/services/api";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Minus,
  Search,
  View,
  Edit,
  Delete,
  WarningFilled,
  AlarmClock,
  CircleCloseFilled,
} from "@element-plus/icons-vue";
import PropertyEditor from "@/components/PropertyEditor.vue";

const authStore = useAuthStore();
const { canUpdate, canDelete, canCreate } = usePermissions();

// 移动端检测
const isMobile = ref(false);

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
};

// 响应式数据
const items = ref([]);
const categories = ref([]);
const sections = ref([]);
const laboratories = ref([]);
const storages = ref([]);
const loading = ref(false);
const showDialog = ref(false);
const showDetailDialog = ref(false);
const submitting = ref(false);
const editingItem = ref(null);
const viewingItem = ref(null);
const propertyValidation = ref({ isValid: true, errors: [] }); // 新增属性验证状态
const formRef = ref(); // 添加表单引用

// 分页相关
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const totalPages = ref(0);

// 搜索和筛选
const searchQuery = ref("");
const filterCategory = ref("");
const filterSection = ref("");
const showLowStock = ref(false);
const showExpiring = ref(false);
const sortBy = ref("created_at");
const sortDesc = ref(true);

const form = reactive({
  code: "",
  name: "",
  description: "",
  category: "",
  properties: {},
  price: 0,
  quantity: 0,
  min_quantity: 0,
  unit: "",
  supplier: "",
  purchase_date: null,
  expiry_date: null,
  laboratory_id: null,
  storage_id: null,
  section_id: null,
});

const rules = {
  code: [
    { required: true, message: "请输入物品编号", trigger: "blur" },
    {
      validator: async (rule, value, callback) => {
        if (!value) {
          callback();
          return;
        }

        // 如果是编辑模式且编号未改变，跳过检查
        if (editingItem.value && editingItem.value.item.code === value) {
          callback();
          return;
        }

        try {
          const response = await api.get(`/items/check-code?code=${value}`);
          if (response.data.exists) {
            callback(new Error("物品编号已存在，请使用不同的编号"));
          } else {
            callback();
          }
        } catch (error) {
          console.error("检查编号失败:", error);
          callback(); // 网络错误时不阻止提交
        }
      },
      trigger: "blur",
    },
  ],
  name: [{ required: true, message: "请输入物品名称", trigger: "blur" }],
  category: [{ required: true, message: "请输入物品类别", trigger: "blur" }],
  unit: [{ required: true, message: "请输入单位", trigger: "blur" }],
  quantity: [{ required: true, message: "请输入数量", trigger: "blur" }],
  min_quantity: [
    { required: true, message: "请输入最低库存", trigger: "blur" },
  ],
  section_id: [
    { required: true, message: "请选择存放位置", trigger: "change" },
  ],
};

// 搜索和筛选处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchItems();
};

const handleCategoryFilter = () => {
  currentPage.value = 1;
  fetchItems();
};

const handleSectionFilter = () => {
  currentPage.value = 1;
  fetchItems();
};

const handleLowStockFilter = () => {
  currentPage.value = 1;
  fetchItems();
};

const handleExpiringFilter = () => {
  currentPage.value = 1;
  fetchItems();
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchItems();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchItems();
};

// 排序处理
const handleSortChange = ({ prop, order }) => {
  if (prop) {
    sortBy.value = prop;
    sortDesc.value = order === "descending";
  } else {
    sortBy.value = "created_at";
    sortDesc.value = true;
  }
  currentPage.value = 1;
  fetchItems();
};

const fetchItems = async () => {
  try {
    loading.value = true;

    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      sort_by: sortBy.value,
      sort_desc: sortDesc.value,
    };

    // 添加筛选条件
    if (filterCategory.value) {
      params.category = filterCategory.value;
    }
    if (filterSection.value) {
      params.section_id = filterSection.value;
    }
    if (showLowStock.value) {
      params.low_stock = "true";
    }
    if (showExpiring.value) {
      params.expiring = "true";
    }

    const response = await api.get("/items", { params });

    if (response.data.data) {
      items.value = response.data.data.map((item) => ({
        ...item,
        adjusting: false, // 初始化调整状态
      }));
      total.value = response.data.total;
      totalPages.value = response.data.total_pages;
      currentPage.value = response.data.page;
      pageSize.value = response.data.page_size;
    } else {
      items.value = [];
      total.value = 0;
    }
  } catch (error) {
    ElMessage.error("获取物品列表失败");
    console.error("获取物品失败:", error);
  } finally {
    loading.value = false;
  }
};

const fetchCategories = async () => {
  try {
    const response = await api.get("/items/categories");
    categories.value = response.data.categories || [];
  } catch (error) {
    console.error("获取类别失败:", error);
  }
};

const fetchSections = async () => {
  try {
    // 必须传递分页参数，防止后端校验失败
    const params = {
      page: 1, // 拉全部分区时可用大页码
      page_size: 100,
    };
    const response = await api.get("/sections", { params });
    // 兼容后端分页结构
    if (response.data.data) {
      sections.value = response.data.data;
    } else if (response.data.sections) {
      sections.value = response.data.sections;
    } else {
      sections.value = [];
    }
    console.log("Sections API response:", response.data);
  } catch (error) {
    console.error("获取分区失败:", error);
  }
};

const fetchLaboratories = async () => {
  try {
    // 必须传递分页参数，防止后端校验失败
    const maxPageSize = 100; // 后端允许的最大page_size
    const params = {
      page: 1,
      page_size: maxPageSize,
    };
    const response = await api.get("/laboratories", { params });
    // 兼容后端分页结构
    if (response.data.data) {
      laboratories.value = response.data.data;
    } else if (response.data.laboratories) {
      laboratories.value = response.data.laboratories;
    } else {
      laboratories.value = [];
    }
  } catch (error) {
    console.error("获取实验室失败:", error);
  }
};

const onLaboratoryChange = async (labId) => {
  form.storage_id = null;
  form.section_id = null;
  storages.value = [];
  sections.value = [];

  if (labId) {
    try {
      const response = await api.get("/storages", {
        params: { lab_id: labId, page: 1, page_size: 100 },
      });
      console.log("Storages response:", response.data);

      // 处理不同的数据格式
      let allStorages = response.data.data || response.data.storages || [];

      storages.value = allStorages;
    } catch (error) {
      console.error("获取存储装置失败:", error);
    }
  }
};

const onStorageChange = async (storageId) => {
  form.section_id = null;
  sections.value = [];

  if (storageId) {
    try {
      const response = await api.get("/sections", {
        params: { storage_id: storageId, page: 1, page_size: 100 },
      });
      console.log("Sections response:", response.data);

      // 处理不同的数据格式
      let allSections = response.data.data || response.data.sections || [];
      sections.value = allSections;
    } catch (error) {
      console.error("获取分区失败:", error);
    }
  }
};

const isExpiring = (expiryDate) => {
  if (!expiryDate) return false;

  console.log("Checking expiry date:", expiryDate);

  const expiry = new Date(expiryDate);
  const now = new Date();
  const daysDiff = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));

  console.log("Days until expiry:", daysDiff);
  console.log("Is expiring?", daysDiff <= 60 && daysDiff >= 0);

  return daysDiff <= 60 && daysDiff >= 0; // 改为60天内过期就显示警告
};

const isExpired = (expiryDate) => {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const now = new Date();
  return expiry < now;
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString("zh-CN");
};

const getPropertiesArray = (properties) => {
  if (!properties || typeof properties !== "object") return [];
  return Object.entries(properties).map(([key, value]) => ({ key, value }));
};

const viewItem = (itemData) => {
  viewingItem.value = itemData;
  showDetailDialog.value = true;
};

const editItem = async (itemData) => {
  editingItem.value = itemData;

  console.log("编辑物品数据:", itemData);
  console.log("物品属性:", itemData.item.properties);

  // 安全处理属性数据，防止异常数据导致死循环
  let safeProperties = {};
  try {
    const props = itemData.item.properties || {};
    // 限制属性数量和深度，防止数据爆炸
    if (typeof props === "object" && props !== null && !Array.isArray(props)) {
      const entries = Object.entries(props);
      if (entries.length <= 50) {
        // 最多50个属性
        safeProperties = JSON.parse(JSON.stringify(props));
      } else {
        console.warn("属性数量过多，已截断:", entries.length);
        safeProperties = Object.fromEntries(entries.slice(0, 50));
      }
    }
  } catch (error) {
    console.error("处理属性数据出错:", error);
    safeProperties = {};
  }

  // 设置完整的表单数据
  Object.assign(form, {
    code: itemData.item.code,
    name: itemData.item.name,
    description: itemData.item.description,
    category: itemData.item.category,
    properties: safeProperties,
    price: itemData.item.price,
    quantity: itemData.item.quantity,
    min_quantity: itemData.item.min_quantity,
    unit: itemData.item.unit,
    supplier: itemData.item.supplier,
    section_id: itemData.item.section_id,
    laboratory_id: itemData.section?.storage?.lab_id,
    storage_id: itemData.section?.storage_id,
    purchase_date: itemData.item.purchase_date
      ? new Date(itemData.item.purchase_date)
      : null,
    expiry_date: itemData.item.expiry_date
      ? new Date(itemData.item.expiry_date)
      : null,
  });

  console.log("表单数据设置后:", form);
  console.log("表单属性:", form.properties);

  // 按顺序预加载相关的存储装置和分区数据
  if (itemData.section?.storage?.lab_id) {
    console.log("正在加载实验室数据:", itemData.section.storage.lab_id);
    await onLaboratoryChange(itemData.section.storage.lab_id);

    // 等待实验室数据加载完成后，再加载存储装置数据
    if (itemData.section?.storage_id) {
      console.log("正在加载存储装置数据:", itemData.section.storage_id);
      await onStorageChange(itemData.section.storage_id);

      // 手动设置storage_id和section_id，确保级联选择器显示正确值
      await nextTick(); // 等待DOM更新

      // 确保存储装置在选项列表中
      const storageExists = storages.value.some(
        (s) => s.id === itemData.section.storage_id
      );
      if (storageExists) {
        form.storage_id = itemData.section.storage_id;
        console.log("设置存储装置ID:", form.storage_id);
      } else {
        console.warn(
          "存储装置不在列表中:",
          itemData.section.storage_id,
          storages.value
        );
      }

      // 确保分区在选项列表中
      const sectionExists = sections.value.some(
        (s) => s.id === itemData.item.section_id
      );
      if (sectionExists) {
        form.section_id = itemData.item.section_id;
        console.log("设置分区ID:", form.section_id);
      } else {
        console.warn(
          "分区不在列表中:",
          itemData.item.section_id,
          sections.value
        );
      }
    }
  }

  console.log("最终表单状态:", {
    laboratory_id: form.laboratory_id,
    storage_id: form.storage_id,
    section_id: form.section_id,
    storages: storages.value,
    sections: sections.value,
  });

  showDialog.value = true;
};

const deleteItem = async (itemData) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除物品"${itemData.item.name}"吗？`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/items/${itemData.item.id}`);
    ElMessage.success("删除成功");
    fetchItems();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error.response?.data?.error || "删除失败");
    }
  }
};

const adjustQuantity = async (row, change) => {
  const newQuantity = (row.item.quantity || 0) + change;
  if (newQuantity < 0) {
    ElMessage.warning("库存不能为负数");
    return;
  }

  // 设置加载状态
  row.adjusting = true;

  try {
    // 调用后端API更新库存
    await api.put(`/items/${row.item.id}/quantity`, {
      quantity: newQuantity,
    });

    // 更新本地数据
    row.item.quantity = newQuantity;

    ElMessage.success(
      `库存${change > 0 ? "增加" : "减少"}成功：${Math.abs(change)} ${
        row.item.unit || "个"
      }`
    );
  } catch (error) {
    ElMessage.error("库存调整失败");
    console.error("库存调整失败:", error);
  } finally {
    row.adjusting = false;
  }
};

const submitForm = async () => {
  if (!formRef.value) return;

  try {
    // 验证表单
    await formRef.value.validate();

    // 验证属性
    if (!propertyValidation.value.isValid) {
      ElMessage.error(
        `属性配置有误：${propertyValidation.value.errors.join(", ")}`
      );
      return;
    }

    submitting.value = true;

    // 创建提交数据，排除id字段以避免冲突
    const submitData = {
      code: form.code,
      name: form.name,
      description: form.description,
      category: form.category,
      properties: form.properties,
      price: form.price,
      quantity: form.quantity,
      min_quantity: form.min_quantity,
      unit: form.unit,
      supplier: form.supplier,
      section_id: form.section_id,
      purchase_date: form.purchase_date
        ? form.purchase_date.toISOString().split("T")[0]
        : null,
      expiry_date: form.expiry_date
        ? form.expiry_date.toISOString().split("T")[0]
        : null,
    };

    if (editingItem.value) {
      await api.put(`/items/${editingItem.value.item.id}`, submitData);
      ElMessage.success("更新成功");
    } else {
      await api.post("/items", submitData);
      ElMessage.success("创建成功");
    }

    showDialog.value = false;
    fetchItems();
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error);
    } else {
      ElMessage.error(editingItem.value ? "更新失败" : "创建失败");
    }
    console.error("Error submitting form:", error);
  } finally {
    submitting.value = false;
  }
};

const resetForm = () => {
  editingItem.value = null;
  Object.assign(form, {
    code: "",
    name: "",
    description: "",
    category: "",
    properties: {},
    price: 0,
    quantity: 0,
    min_quantity: 0,
    unit: "",
    supplier: "",
    purchase_date: null,
    expiry_date: null,
    laboratory_id: null,
    storage_id: null,
    section_id: null,
  });

  // 清空级联选择的数据
  storages.value = [];
  sections.value = [];

  formRef.value?.resetFields();
};

// 处理属性验证
const handlePropertyValidation = (validation) => {
  propertyValidation.value = validation;
};

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
  fetchItems();
  fetchCategories();
  fetchSections();
  fetchLaboratories();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", checkMobile);
});
</script>

<style scoped>
/* 页面通用样式 */
.items {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.filter-section .el-select {
  width: 100%;
}

/* 级联选择器样式 */
.select-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

.el-select {
  width: 100%;
}

.el-select .el-input__inner {
  height: 40px;
  line-height: 40px;
}

/* 表单样式 */
.form-section {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

.form-section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.text-placeholder {
  color: #909399;
  font-style: italic;
}

.search-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.quantity-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.low-stock {
  color: #e6a23c;
  font-weight: 500;
}

.status-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-tags .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-normal {
  color: #67c23a;
  font-size: 12px;
  font-weight: 500;
}

.item-detail {
  margin-bottom: 20px;
}

.detail-status {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.properties-section {
  margin-top: 24px;
}

.properties-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.properties-display {
  margin-top: 12px;
}

.array-value {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.array-tag {
  margin: 0;
}

.number-value {
  font-weight: 500;
  color: #409eff;
}

/* 表单部分样式优化 */
.form-section {
  margin-bottom: 24px;
  padding: 20px;
  background-color: #fafbfc;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.form-section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

/* 库存控制按钮样式 */
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.quantity-buttons {
  display: flex;
  gap: 4px;
}

.quantity-buttons .el-button {
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 移动端卡片样式 */
.mobile-cards {
  display: none;
}

.mobile-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.mobile-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.mobile-card-code {
  font-size: 14px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.mobile-card-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.mobile-card-field {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
  min-height: 32px;
}

.mobile-card-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
  min-width: 60px;
  flex-shrink: 0;
}

.mobile-card-value {
  font-size: 14px;
  color: #606266;
  text-align: right;
  flex: 1;
  margin-left: 12px;
}

.mobile-card-actions {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.mobile-card-actions .el-button {
  padding: 6px 12px;
  font-size: 12px;
  flex: 0 0 auto;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .items {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .search-section {
    padding: 12px;
  }

  .search-section .el-row {
    flex-direction: column;
  }

  .search-section .el-col {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 12px;
  }

  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .quantity-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .table-actions {
    flex-direction: column;
    gap: 4px;
  }

  .table-actions .el-button {
    width: 100%;
    margin: 0;
  }
}

@media (max-width: 480px) {
  .mobile-card-view .el-table,
  .mobile-card-view .el-table__header-wrapper,
  .mobile-card-view .el-table__body-wrapper {
    display: none;
  }

  .mobile-cards {
    display: block !important;
  }

  .mobile-card-actions {
    justify-content: center;
  }

  .mobile-card-actions .el-button {
    flex: 1;
    min-width: 0;
    max-width: 80px;
  }

  .status-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: flex-end;
  }

  .status-tags .el-tag {
    font-size: 10px;
    padding: 2px 6px;
  }
}
</style>
