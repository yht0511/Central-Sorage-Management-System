import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api";

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("token"));
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === "admin");

  const login = async (credentials) => {
    try {
      const response = await api.post("/login", credentials);
      const { token: newToken, user: userData } = response.data;

      token.value = newToken;
      user.value = userData;

      localStorage.setItem("token", newToken);
      localStorage.setItem("user", JSON.stringify(userData));

      // 设置axios默认header
      api.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;

      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || "登录失败",
      };
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    delete api.defaults.headers.common["Authorization"];
  };

  const checkAuth = () => {
    if (token.value) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token.value}`;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put("/profile", profileData);
      user.value = { ...user.value, ...profileData };
      localStorage.setItem("user", JSON.stringify(user.value));
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || "更新失败",
      };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await api.post("/change-password", passwordData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || "密码修改失败",
      };
    }
  };

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword,
  };
});
