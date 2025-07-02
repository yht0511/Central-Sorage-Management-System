import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// 路由组件
import Login from "@/views/Login.vue";
import Layout from "@/components/Layout.vue";
import Dashboard from "@/views/Dashboard.vue";
import Laboratories from "@/views/Laboratories.vue";
import StorageDevices from "@/views/StorageDevices.vue";
import Sections from "@/views/Sections.vue";
import Items from "@/views/Items.vue";
import MovementHistory from "@/views/MovementHistory.vue";
import Profile from "@/views/Profile.vue";
import Users from "@/views/Users.vue";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { guest: true },
  },
  {
    path: "/",
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "Dashboard",
        component: Dashboard,
        meta: { title: "总览" },
      },
      {
        path: "/laboratories",
        name: "Laboratories",
        component: Laboratories,
        meta: { title: "实验室管理" },
      },
      {
        path: "/storage-devices",
        name: "StorageDevices",
        component: StorageDevices,
        meta: { title: "存储装置管理" },
      },
      {
        path: "/storages",
        name: "Storages",
        component: StorageDevices,
        meta: { title: "存储装置管理" },
      },
      {
        path: "/partitions",
        name: "Partitions",
        component: Sections,
        meta: { title: "分区管理" },
      },
      {
        path: "/sections",
        name: "Sections",
        component: Sections,
        meta: { title: "分区管理" },
      },
      {
        path: "/items",
        name: "Items",
        component: Items,
        meta: { title: "物品管理" },
      },
      {
        path: "/movements",
        name: "MovementHistory",
        component: MovementHistory,
        meta: { title: "移动记录" },
      },
      {
        path: "/profile",
        name: "Profile",
        component: Profile,
        meta: { title: "个人资料" },
      },
      {
        path: "/users",
        name: "Users",
        component: Users,
        meta: { title: "用户管理", requiresAdmin: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next("/");
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next("/"); // 非管理员重定向到首页
  } else {
    next();
  }
});

export default router;
