<template>
  <div>
    <v-navigation-drawer app v-model="drawer" :width="240">
      <v-list nav density="comfortable">
        <v-list-item
          v-for="item in navItems"
          :key="item.to.name"
          :to="item.to"
          :prepend-icon="item.icon"
          :exact="item.exact || false"
          color="primary"
        >
          <v-list-item-title>{{ item.label }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar app>
      <v-btn variant="text" prepend-icon="mdi-menu" @click="drawer = !drawer">菜单</v-btn>
      <v-toolbar-title>校园文创</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn to="/profile" variant="text" prepend-icon="mdi-account">个人中心</v-btn>
      <v-btn to="/cart" variant="text" prepend-icon="mdi-cart">购物车</v-btn>
      <v-btn variant="text" prepend-icon="mdi-logout" @click="logout">退出登录</v-btn>
    </v-app-bar>
    <v-main>
      <RouterView />
    </v-main>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";

const drawer = ref(true);
const auth = useAuthStore();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push("/login");
};

const navConfig = {
  CONSUMER: [
    { label: "首页", to: { name: "dashboard" }, icon: "mdi-view-dashboard", exact: true },
    { label: "店铺", to: { name: "store" }, icon: "mdi-store" },
    { label: "我的订单", to: { name: "my-orders" }, icon: "mdi-receipt" },
    { label: "商品", to: { name: "consumer-products" }, icon: "mdi-tag" },
    { label: "好物聚焦", to: { name: "focus" }, icon: "mdi-video" },
    { label: "互动社区", to: { name: "community" }, icon: "mdi-forum" },
    { label: "购物车", to: { name: "cart" }, icon: "mdi-cart" },
    { label: "个人中心", to: { name: "profile" }, icon: "mdi-account" },
  ],
  MERCHANT: [
    { label: "商品管理", to: { name: "product-management" }, icon: "mdi-package-variant" },
    { label: "订单管理", to: { name: "orders" }, icon: "mdi-clipboard-list" },
    { label: "好物聚焦", to: { name: "focus" }, icon: "mdi-video" },
    { label: "互动社区", to: { name: "community" }, icon: "mdi-forum" },
    { label: "个人中心", to: { name: "profile" }, icon: "mdi-account" },
  ],
  ADMIN: [
    { label: "用户管理", to: { name: "user-management" }, icon: "mdi-account-multiple" },
    { label: "商家管理", to: { name: "merchant-management" }, icon: "mdi-store" },
    { label: "分类管理", to: { name: "category-management" }, icon: "mdi-tag" },
    { label: "商品管理", to: { name: "product-management" }, icon: "mdi-package-variant" },
    { label: "订单管理", to: { name: "orders" }, icon: "mdi-clipboard-list" },
    { label: "数据统计", to: { name: "data-stats" }, icon: "mdi-chart-bar" },
    { label: "好物聚焦管理", to: { name: "focus-admin" }, icon: "mdi-video-check" },
    { label: "系统管理", to: { name: "system-management" }, icon: "mdi-cog" },
    { label: "互动社区", to: { name: "community" }, icon: "mdi-forum" },
    { label: "个人中心", to: { name: "profile" }, icon: "mdi-account" },
    { label: "模拟终端", to: { name: "terminal" }, icon: "mdi-console" },
  ],
};

const navItems = computed(() => navConfig[auth.user?.role] || []);
</script>
