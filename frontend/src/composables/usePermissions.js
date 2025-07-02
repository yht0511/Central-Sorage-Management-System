import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export function usePermissions() {
  const authStore = useAuthStore();

  // 基础权限检查
  const isAdmin = computed(() => authStore.isAdmin);
  const isAuthenticated = computed(() => authStore.isAuthenticated);

  // 模块权限检查
  const permissions = computed(() => ({
    // 用户管理 - 仅管理员
    users: {
      view: isAdmin.value,
      create: isAdmin.value,
      update: isAdmin.value,
      delete: isAdmin.value,
    },

    // 实验室管理 - 仅管理员
    laboratories: {
      view: isAuthenticated.value,
      create: isAdmin.value,
      update: isAdmin.value,
      delete: isAdmin.value,
    },

    // 存储装置管理 - 仅管理员
    storages: {
      view: isAuthenticated.value,
      create: isAdmin.value,
      update: isAdmin.value,
      delete: isAdmin.value,
    },

    // 分区管理 - 仅管理员
    sections: {
      view: isAuthenticated.value,
      create: isAdmin.value,
      update: isAdmin.value,
      delete: isAdmin.value,
    },

    // 物品管理 - 所有用户
    items: {
      view: isAuthenticated.value,
      create: isAuthenticated.value,
      update: isAuthenticated.value,
      delete: isAuthenticated.value,
      adjustQuantity: isAuthenticated.value,
    },

    // 移动记录 - 普通用户只能查看
    movements: {
      view: isAuthenticated.value,
      create: isAdmin.value,
      update: isAdmin.value,
      delete: isAdmin.value,
      export: isAuthenticated.value,
    },

    // 统计数据 - 所有用户
    stats: {
      view: isAuthenticated.value,
    },
  }));

  // 便捷方法
  const canView = (module, action = "view") => {
    return permissions.value[module]?.[action] || false;
  };

  const canCreate = (module) => {
    return permissions.value[module]?.create || false;
  };

  const canUpdate = (module) => {
    return permissions.value[module]?.update || false;
  };

  const canDelete = (module) => {
    return permissions.value[module]?.delete || false;
  };

  return {
    isAdmin,
    isAuthenticated,
    permissions,
    canView,
    canCreate,
    canUpdate,
    canDelete,
  };
}
