<template>
  <div class="property-editor">
    <div class="editor-header">
      <h4 class="editor-title">{{ title }}</h4>
      <div class="header-actions">
        <el-button
          type="primary"
          size="small"
          :icon="Plus"
          @click="addProperty"
        >
          添加属性
        </el-button>
        <el-button
          v-if="showJsonEditor"
          type="info"
          size="small"
          @click="toggleJsonMode"
        >
          {{ isJsonMode ? "表单模式" : "JSON模式" }}
        </el-button>
      </div>
    </div>

    <!-- JSON模式 -->
    <div v-if="isJsonMode" class="json-editor">
      <el-input
        v-model="jsonText"
        type="textarea"
        :rows="10"
        placeholder="请输入有效的JSON格式..."
        @input="handleJsonInput"
      />
      <div v-if="jsonError" class="json-error">
        <el-text type="danger" size="small">
          <el-icon><Warning /></el-icon>
          {{ jsonError }}
        </el-text>
      </div>
    </div>

    <!-- 表单模式 -->
    <div v-else>
      <!-- 空状态 -->
      <div v-if="properties.length === 0" class="empty-state">
        <el-empty description="暂无属性，点击上方按钮添加" :image-size="80" />
      </div>

      <!-- 属性列表 -->
      <div v-else class="properties-list">
        <div
          v-for="(property, index) in properties"
          :key="property.id"
          class="property-item"
        >
          <div class="property-controls">
            <!-- 属性名 -->
            <el-input
              v-model="property.key"
              placeholder="属性名"
              size="default"
              class="property-key"
              :class="{ 'error-input': !isValidKey(property.key) }"
              @input="validateAndUpdate"
            />

            <!-- 数据类型选择 -->
            <el-select
              v-model="property.type"
              placeholder="类型"
              size="default"
              class="property-type"
              @change="handleTypeChange(property)"
            >
              <el-option label="文本" value="string" />
              <el-option label="数字" value="number" />
              <el-option label="布尔" value="boolean" />
              <el-option label="日期" value="date" />
              <el-option label="数组" value="array" />
            </el-select>

            <!-- 属性值 -->
            <div class="property-value">
              <!-- 字符串输入 -->
              <el-input
                v-if="property.type === 'string'"
                v-model="property.value"
                placeholder="属性值"
                size="default"
                @input="validateAndUpdate"
              />

              <!-- 数字输入 -->
              <el-input-number
                v-else-if="property.type === 'number'"
                v-model="property.value"
                placeholder="数字值"
                size="default"
                :controls="false"
                @change="validateAndUpdate"
              />

              <!-- 布尔选择 -->
              <el-select
                v-else-if="property.type === 'boolean'"
                v-model="property.value"
                placeholder="选择"
                size="default"
                @change="validateAndUpdate"
              >
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>

              <!-- 日期选择 -->
              <el-date-picker
                v-else-if="property.type === 'date'"
                v-model="property.value"
                type="date"
                placeholder="选择日期"
                size="default"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="validateAndUpdate"
              />

              <!-- 数组输入 -->
              <el-input
                v-else-if="property.type === 'array'"
                v-model="property.arrayText"
                placeholder="用逗号分隔多个值"
                size="default"
                @input="handleArrayInput(property)"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="property-actions">
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                circle
                @click="removeProperty(index)"
              />
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="property.error" class="property-error">
            <el-text type="danger" size="small">
              <el-icon><Warning /></el-icon>
              {{ property.error }}
            </el-text>
          </div>
        </div>
      </div>

      <!-- 预览和验证 -->
      <div v-if="properties.length > 0" class="preview-section">
        <el-divider />
        <div class="preview-header">
          <span class="preview-title">预览结果</span>
          <el-badge
            :value="validationErrors.length"
            :hidden="validationErrors.length === 0"
            type="danger"
          >
            <el-text type="info" size="small"
              >{{ Object.keys(result).length }} 个有效属性</el-text
            >
          </el-badge>
        </div>

        <!-- 验证错误 -->
        <div v-if="validationErrors.length > 0" class="validation-errors">
          <el-alert
            title="请修复以下问题："
            type="error"
            :closable="false"
            show-icon
          >
            <ul class="error-list">
              <li v-for="error in validationErrors" :key="error">
                {{ error }}
              </li>
            </ul>
          </el-alert>
        </div>

        <!-- JSON预览 -->
        <div class="json-preview">
          <pre><code>{{ formattedJson }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { Plus, Delete, Warning } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const props = defineProps({
  modelValue: {
    type: [Object, String],
    default: () => ({}),
  },
  title: {
    type: String,
    default: "属性编辑器",
  },
  showJsonEditor: {
    type: Boolean,
    default: true,
  },
  maxProperties: {
    type: Number,
    default: 50,
  },
});

const emit = defineEmits(["update:modelValue", "validate"]);

// 响应式数据
const properties = ref([]);
const isJsonMode = ref(false);
const jsonText = ref("");
const jsonError = ref("");
let propertyIdCounter = 0;

// 生成唯一ID
const generateId = () => `prop_${++propertyIdCounter}`;

// 创建默认属性
const createProperty = (key = "", value = "", type = "string") => ({
  id: generateId(),
  key,
  value,
  type,
  arrayText: Array.isArray(value) ? value.join(", ") : "",
  error: "",
});

// 验证属性名
const isValidKey = (key) => {
  if (!key || typeof key !== "string") return false;
  // 属性名不能为空，不能包含特殊字符
  return key.trim().length > 0 && /^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(key.trim());
};

// 验证错误列表
const validationErrors = computed(() => {
  const errors = [];
  const keyMap = new Map();

  // 限制验证的属性数量，防止性能问题
  const propsToValidate = properties.value.slice(0, 100);

  propsToValidate.forEach((property, index) => {
    const key = property.key?.trim();

    // 检查属性名
    if (!key) {
      errors.push(`第 ${index + 1} 个属性名不能为空`);
    } else if (!isValidKey(key)) {
      errors.push(`第 ${index + 1} 个属性名格式不正确（${key}）`);
    } else if (keyMap.has(key)) {
      errors.push(`属性名重复：${key}`);
    } else {
      keyMap.set(key, true);
    }

    // 检查属性值
    if (
      property.type === "number" &&
      property.value !== null &&
      property.value !== undefined
    ) {
      if (isNaN(property.value)) {
        errors.push(`属性 ${key} 的值不是有效数字`);
      }
    }
  });

  return errors;
});

// 计算最终结果
const result = computed(() => {
  // 防止在大量属性时频繁计算
  if (properties.value.length > 50) {
    console.warn("属性数量过多，可能影响性能:", properties.value.length);
  }

  const obj = {};

  for (const property of properties.value) {
    const key = property.key?.trim();
    if (!key || !isValidKey(key)) continue;

    let value = property.value;

    // 根据类型转换值
    switch (property.type) {
      case "number":
        value =
          value === "" || value === null || value === undefined
            ? 0
            : Number(value);
        if (isNaN(value)) value = 0;
        break;
      case "boolean":
        value = Boolean(value);
        break;
      case "array":
        value = property.arrayText
          ? property.arrayText
              .split(",")
              .map((item) => item.trim())
              .filter((item) => item)
          : [];
        break;
      case "date":
        // 保持日期字符串格式
        break;
      default:
        value = String(value || "");
    }

    obj[key] = value;
  }

  return obj;
});

// 格式化JSON显示
const formattedJson = computed(() => {
  try {
    return JSON.stringify(result.value, null, 2);
  } catch (error) {
    return "无效的JSON格式";
  }
});

// 初始化数据
const initializeProperties = (shouldEmit = false) => {
  let initialValue = props.modelValue;

  // 添加性能保护
  const startTime = performance.now();

  // 处理字符串输入
  if (typeof initialValue === "string") {
    try {
      initialValue = initialValue ? JSON.parse(initialValue) : {};
    } catch (error) {
      console.warn("无法解析JSON字符串:", error);
      initialValue = {};
    }
  }

  // 确保是对象
  if (
    !initialValue ||
    typeof initialValue !== "object" ||
    Array.isArray(initialValue)
  ) {
    initialValue = {};
  }

  // 限制处理的属性数量，防止性能问题
  const entries = Object.entries(initialValue);
  if (entries.length > 50) {
    console.warn(`属性数量过多(${entries.length})，已截断到50个`);
    initialValue = Object.fromEntries(entries.slice(0, 50));
  }

  // 转换为属性数组
  properties.value = Object.entries(initialValue).map(([key, value]) => {
    let type = "string";
    let arrayText = "";

    // 推断类型
    if (typeof value === "number") {
      type = "number";
    } else if (typeof value === "boolean") {
      type = "boolean";
    } else if (Array.isArray(value)) {
      type = "array";
      arrayText = value.join(", ");
    } else if (
      value &&
      typeof value === "string" &&
      /^\d{4}-\d{2}-\d{2}$/.test(value)
    ) {
      type = "date";
    }

    return createProperty(key, value, type);
  });

  // 更新JSON文本
  try {
    jsonText.value = JSON.stringify(initialValue, null, 2);
  } catch (error) {
    console.error("JSON序列化失败:", error);
    jsonText.value = "{}";
  }

  // 性能监控
  const endTime = performance.now();
  if (endTime - startTime > 100) {
    console.warn(`PropertyEditor初始化耗时过长: ${endTime - startTime}ms`);
  }

  // 只有明确要求时才触发验证更新
  if (shouldEmit) {
    nextTick(() => {
      validateAndUpdate();
    });
  }
};

// 添加属性
const addProperty = () => {
  if (properties.value.length >= props.maxProperties) {
    ElMessage.warning(`最多只能添加 ${props.maxProperties} 个属性`);
    return;
  }

  properties.value.push(createProperty());
  validateAndUpdate();
};

// 删除属性
const removeProperty = (index) => {
  properties.value.splice(index, 1);
  validateAndUpdate();
};

// 处理类型变化
const handleTypeChange = (property) => {
  // 根据新类型转换值
  switch (property.type) {
    case "number":
      property.value = property.value ? Number(property.value) || 0 : 0;
      break;
    case "boolean":
      property.value = Boolean(property.value);
      break;
    case "array":
      if (!Array.isArray(property.value)) {
        property.arrayText = property.value ? String(property.value) : "";
      }
      break;
    case "date":
      if (property.value && !/^\d{4}-\d{2}-\d{2}$/.test(property.value)) {
        property.value = "";
      }
      break;
    default:
      property.value = String(property.value || "");
  }

  validateAndUpdate();
};

// 处理数组输入
const handleArrayInput = (property) => {
  property.value = property.arrayText
    ? property.arrayText
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item)
    : [];
  validateAndUpdate();
};

// 验证并更新
const validateAndUpdate = () => {
  // 清除旧的错误
  properties.value.forEach((property) => {
    property.error = "";
  });

  // 设置更新标志，防止触发watch
  isUpdating = true;

  // 发出事件
  emit("update:modelValue", result.value);
  emit("validate", {
    isValid: validationErrors.value.length === 0,
    errors: validationErrors.value,
    result: result.value,
  });

  // 下一个tick后重置标志
  nextTick(() => {
    isUpdating = false;
  });
};

// 切换JSON模式
const toggleJsonMode = () => {
  if (isJsonMode.value) {
    // 从JSON模式切换到表单模式
    handleJsonSubmit();
  } else {
    // 从表单模式切换到JSON模式
    jsonText.value = JSON.stringify(result.value, null, 2);
    jsonError.value = "";
  }
  isJsonMode.value = !isJsonMode.value;
};

// 处理JSON输入
const handleJsonInput = () => {
  try {
    const parsed = JSON.parse(jsonText.value);
    if (typeof parsed === "object" && !Array.isArray(parsed)) {
      jsonError.value = "";
    } else {
      jsonError.value = "必须是有效的JSON对象";
    }
  } catch (error) {
    jsonError.value = `JSON格式错误: ${error.message}`;
  }
};

// 提交JSON
const handleJsonSubmit = () => {
  try {
    const parsed = JSON.parse(jsonText.value);
    if (typeof parsed === "object" && !Array.isArray(parsed)) {
      // 重新初始化属性
      properties.value = Object.entries(parsed).map(([key, value]) => {
        let type = "string";
        let arrayText = "";

        if (typeof value === "number") {
          type = "number";
        } else if (typeof value === "boolean") {
          type = "boolean";
        } else if (Array.isArray(value)) {
          type = "array";
          arrayText = value.join(", ");
        } else if (
          value &&
          typeof value === "string" &&
          /^\d{4}-\d{2}-\d{2}$/.test(value)
        ) {
          type = "date";
        }

        return createProperty(key, value, type);
      });

      validateAndUpdate();
      jsonError.value = "";
      ElMessage.success("JSON导入成功");
    } else {
      jsonError.value = "必须是有效的JSON对象";
    }
  } catch (error) {
    jsonError.value = `JSON格式错误: ${error.message}`;
    ElMessage.error("JSON格式不正确");
  }
};

// 监听外部值变化
let isUpdating = false; // 防止循环更新的标志
let lastHashValue = ""; // 用于检测真实的数据变化

// 安全的JSON字符串化函数
const safeStringify = (obj) => {
  try {
    // 限制JSON字符串长度，防止内存爆炸
    const str = JSON.stringify(obj || {});
    if (str.length > 10000) {
      console.warn("JSON数据过大，已截断");
      return JSON.stringify({});
    }
    return str;
  } catch (error) {
    console.error("JSON序列化失败:", error);
    return "{}";
  }
};

watch(
  () => props.modelValue,
  (newVal, oldVal) => {
    // 防止在内部更新时触发
    if (isUpdating) {
      return;
    }

    // 计算新值的哈希，避免不必要的字符串化
    const newHash = safeStringify(newVal);
    if (newHash === lastHashValue) {
      return; // 数据没有真正变化
    }

    console.log("PropertyEditor: 外部值变化，重新初始化", { newVal, oldVal });
    lastHashValue = newHash;
    initializeProperties();
  },
  { deep: true, immediate: true }
);
</script>

<style scoped>
.property-editor {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 20px;
  background-color: var(--el-bg-color);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.editor-title {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.json-editor {
  margin-bottom: 16px;
}

.json-error {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  background-color: var(--el-color-danger-light-9);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.properties-list {
  margin-bottom: 20px;
}

.property-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background-color: var(--el-fill-color-blank);
}

.property-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.property-key {
  width: 200px;
}

.property-type {
  width: 120px;
}

.property-value {
  flex: 1;
}

.property-actions {
  display: flex;
  gap: 8px;
}

.property-error {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  background-color: var(--el-color-danger-light-9);
}

.error-input {
  --el-input-border-color: var(--el-color-danger);
}

.preview-section {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.validation-errors {
  margin-bottom: 16px;
}

.error-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.error-list li {
  margin-bottom: 4px;
  color: var(--el-color-danger);
}

.json-preview {
  background-color: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

.json-preview pre {
  margin: 0;
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 13px;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.json-preview code {
  background: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .property-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .property-key,
  .property-type {
    width: 100%;
  }

  .property-actions {
    justify-content: center;
  }
}
</style>
