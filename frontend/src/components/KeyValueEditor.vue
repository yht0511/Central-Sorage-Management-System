<template>
  <div class="key-value-editor">
    <div class="editor-header">
      <span class="editor-title">{{ title }}</span>
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="addKeyValue"
        class="add-key-value-btn"
      >
        添加属性
      </el-button>
    </div>

    <div v-if="pairs.length === 0" class="empty-state">
      <el-empty description="暂无属性" :image-size="80" />
    </div>

    <div v-else class="key-value-list">
      <div
        v-for="(pair, index) in pairs"
        :key="`${pair.id}-${index}`"
        class="key-value-item"
      >
        <el-input
          v-model="pair.key"
          placeholder="属性名"
          size="small"
          style="width: 150px"
          @input="updateValue"
        />
        <span class="separator">:</span>
        <el-input
          v-model="pair.value"
          placeholder="属性值"
          size="small"
          style="flex: 1"
          @input="updateValue"
        />
        <el-button
          type="danger"
          size="small"
          :icon="Delete"
          @click="removeKeyValue(index)"
          circle
        />
      </div>
    </div>

    <!-- 预览JSON -->
    <div v-if="pairs.length > 0" class="json-preview">
      <el-text type="info" size="small"> JSON预览: {{ jsonPreview }} </el-text>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { Plus, Delete } from "@element-plus/icons-vue";

const props = defineProps({
  modelValue: {
    type: [Object, String],
    default: () => ({}),
  },
  title: {
    type: String,
    default: "自定义属性",
  },
});

const emit = defineEmits(["update:modelValue"]);

const pairs = ref([]);
let pairIdCounter = 0;

// 生成唯一ID
const generatePairId = () => {
  return ++pairIdCounter;
};

// 将对象转换为键值对数组
const objectToPairs = (obj) => {
  if (!obj || typeof obj !== "object") return [];

  return Object.entries(obj).map(([key, value]) => ({
    id: generatePairId(),
    key,
    value: String(value),
  }));
};

// 将键值对数组转换为对象
const pairsToObject = (pairsList) => {
  const result = {};
  pairsList.forEach((pair) => {
    if (pair.key && pair.key.trim()) {
      result[pair.key.trim()] = pair.value || "";
    }
  });
  return result;
};

// 初始化数据
const initializePairs = () => {
  let initialValue = props.modelValue;

  // 如果是字符串，尝试解析为JSON
  if (typeof initialValue === "string") {
    try {
      initialValue = JSON.parse(initialValue);
    } catch {
      initialValue = {};
    }
  }

  pairs.value = objectToPairs(initialValue);
};

// JSON预览
const jsonPreview = computed(() => {
  const obj = pairsToObject(pairs.value);
  return JSON.stringify(obj, null, 2);
});

// 添加新的键值对
const addKeyValue = () => {
  pairs.value.push({
    id: generatePairId(),
    key: "",
    value: "",
  });
};

// 删除键值对
const removeKeyValue = (index) => {
  pairs.value.splice(index, 1);
  updateValue();
};

// 更新值
const updateValue = () => {
  const obj = pairsToObject(pairs.value);
  emit("update:modelValue", obj);
};

// 监听外部值变化
watch(
  () => props.modelValue,
  (newVal, oldVal) => {
    // 只有当外部值真正变化时才重新初始化
    if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      initializePairs();
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.key-value-editor {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 16px;
  background-color: #fafafa;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-title {
  font-weight: 500;
  color: #303133;
}

.key-value-list {
  margin-bottom: 12px;
}

.key-value-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.key-value-item:last-child {
  margin-bottom: 0;
}

.separator {
  color: #909399;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 20px 0;
}

.json-preview {
  margin-top: 12px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
  font-size: 12px;
  max-height: 120px;
  overflow-y: auto;
}
</style>
