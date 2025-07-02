import axios from "axios";
import { ElMessage } from "element-plus";

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，跳转到登录页
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    } else if (error.response?.status === 403) {
      ElMessage.error("权限不足");
    } else if (error.response?.status >= 500) {
      ElMessage.error("服务器错误，请稍后重试");
    }
    return Promise.reject(error);
  }
);

// API 方法封装
export const apiMethods = {
  // 用户相关
  user: {
    getProfile: () => api.get("/profile"),
    updateProfile: (data) => api.put("/profile", data),
    changePassword: (data) => api.post("/change-password", data),
    getStats: () => api.get("/stats/user"),
    getActivities: (params) => api.get("/movements", { params }),
  },

  // 实验室
  laboratories: {
    getAll: (params) => api.get("/laboratories", { params }),
    getById: (id) => api.get(`/laboratories/${id}`),
    create: (data) => api.post("/laboratories", data),
    update: (id, data) => api.put(`/laboratories/${id}`, data),
    delete: (id) => api.delete(`/laboratories/${id}`),
  },

  // 存储装置
  storageDevices: {
    getAll: (params) => api.get("/storages", { params }),
    getById: (id) => api.get(`/storages/${id}`),
    create: (data) => api.post("/admin/storages", data),
    update: (id, data) => api.put(`/admin/storages/${id}`, data),
    delete: (id) => api.delete(`/admin/storages/${id}`),
  },

  // 分区
  sections: {
    getAll: (params) => api.get("/sections", { params }),
    getById: (id) => api.get(`/sections/${id}`),
    create: (data) => api.post("/admin/sections", data),
    update: (id, data) => api.put(`/admin/sections/${id}`, data),
    delete: (id) => api.delete(`/admin/sections/${id}`),
  },

  // 分区（旧命名，保持兼容性）
  partitions: {
    getAll: (params) => api.get("/sections", { params }),
    getById: (id) => api.get(`/sections/${id}`),
    create: (data) => api.post("/admin/sections", data),
    update: (id, data) => api.put(`/admin/sections/${id}`, data),
    delete: (id) => api.delete(`/admin/sections/${id}`),
  },

  // 物品
  items: {
    getAll: (params) => api.get("/items", { params }),
    getById: (id) => api.get(`/items/${id}`),
    create: (data) => api.post("/items", data),
    update: (id, data) => api.put(`/items/${id}`, data),
    delete: (id) => api.delete(`/items/${id}`),
    search: (query, limit = 20) =>
      api.get(`/items?search=${query}&limit=${limit}`),
    checkCode: (code) => api.get(`/items/check-code?code=${code}`), // 新增检查编号接口
  },

  // 移动记录
  movements: {
    getAll: (params) => api.get("/movements", { params }),
    getById: (id) => api.get(`/movements/${id}`),
    create: (data) => api.post("/movements", data),
    delete: (id) => api.delete(`/admin/movements/${id}`),
    exportCSV: (queryString) =>
      api.get(`/movements/export${queryString ? "?" + queryString : ""}`, {
        responseType: "blob", // 重要：指定响应类型为blob
      }),
  },

  // 导出移动记录的独立方法（向后兼容）
  exportMovementsCSV: (queryString) =>
    api.get(`/movements/export${queryString ? "?" + queryString : ""}`, {
      responseType: "blob",
    }),

  // 用户管理（管理员）
  users: {
    getAll: (params) => api.get("/admin/users", { params }),
    getById: (id) => api.get(`/admin/users/${id}`),
    create: (data) => api.post("/admin/register", data),
    update: (id, data) => api.put(`/admin/users/${id}`, data),
    delete: (id) => api.delete(`/admin/users/${id}`),
  },

  // 统计数据
  stats: {
    getDashboard: () => api.get("/stats/dashboard"),
  },
};

export default api;
