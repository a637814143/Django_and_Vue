import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import AppShell from "../layouts/AppShell.vue";

import AuthLogin from "../views/AuthLogin.vue";
import AuthRegister from "../views/AuthRegister.vue";
import DashboardHome from "../views/DashboardHome.vue";
import CatalogPage from "../views/CatalogPage.vue";
import StoreDetail from "../views/StoreDetail.vue";
import CartPage from "../views/CartPage.vue";
import ProfileCenter from "../views/ProfileCenter.vue";
import AnalyticsPage from "../views/AnalyticsPage.vue";
import CategoryManagement from "../views/CategoryManagement.vue";
import CommunityPage from "../views/CommunityPage.vue";
import ConsumerProducts from "../views/ConsumerProducts.vue";
import CustomizationPage from "../views/CustomizationPage.vue";
import DataStats from "../views/DataStats.vue";
import FeaturedFocus from "../views/FeaturedFocus.vue";
import FocusAdmin from "../views/FocusAdmin.vue";
import MerchantManagement from "../views/MerchantManagement.vue";
import SalesPage from "../views/SalesPage.vue";
import StorePage from "../views/StorePage.vue";
import SystemManagement from "../views/SystemManagement.vue";
import TerminalPage from "../views/TerminalPage.vue";
import UserManagement from "../views/UserManagement.vue";
import MyOrders from "../views/MyOrders.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "Login", component: AuthLogin, meta: { public: true } },
    { path: "/register", name: "Register", component: AuthRegister, meta: { public: true } },
    {
      path: "/",
      component: AppShell,
      children: [
        { path: "", name: "dashboard", component: DashboardHome, meta: { label: "首页", icon: "mdi-view-dashboard", roles: ["CONSUMER", "MERCHANT", "ADMIN"] } },
        { path: "user-management", name: "user-management", component: UserManagement, meta: { label: "用户管理", icon: "mdi-account-multiple", roles: ["ADMIN"] } },
        { path: "merchant-management", name: "merchant-management", component: MerchantManagement, meta: { label: "商家管理", icon: "mdi-store", roles: ["ADMIN"] } },
        { path: "category-management", name: "category-management", component: CategoryManagement, meta: { label: "分类管理", icon: "mdi-tag", roles: ["ADMIN", "MERCHANT"] } },
        { path: "catalog", name: "product-management", component: CatalogPage, meta: { label: "商品管理", icon: "mdi-book-open-page-variant", roles: ["ADMIN", "MERCHANT"] } },
        { path: "sales", name: "orders", component: SalesPage, meta: { label: "订单管理", icon: "mdi-chart-bar", roles: ["MERCHANT", "ADMIN"] } },
        { path: "customization", name: "customization", component: CustomizationPage, meta: { label: "个性定制", icon: "mdi-tshirt-crew", roles: ["CONSUMER", "MERCHANT", "ADMIN"] } },
        { path: "community", name: "community", component: CommunityPage, meta: { label: "互动社区", icon: "mdi-forum", roles: ["CONSUMER", "MERCHANT", "ADMIN"] } },
        { path: "focus", name: "focus", component: FeaturedFocus, meta: { label: "好物聚焦", icon: "mdi-video", roles: ["CONSUMER", "MERCHANT"] } },
        { path: "focus-admin", name: "focus-admin", component: FocusAdmin, meta: { label: "好物聚焦管理", icon: "mdi-video-check", roles: ["ADMIN"] } },
        { path: "analytics", name: "analytics", component: AnalyticsPage, meta: { label: "销售分析", icon: "mdi-chart-pie", roles: ["ADMIN", "MERCHANT"] } },
        { path: "system-management", name: "system-management", component: SystemManagement, meta: { label: "系统管理", icon: "mdi-cog", roles: ["ADMIN"] } },
        { path: "terminal", name: "terminal", component: TerminalPage, meta: { label: "模拟终端", icon: "mdi-console", roles: ["ADMIN"] } },
        { path: "store", name: "store", component: StorePage, meta: { label: "店铺", icon: "mdi-store-outline", roles: ["CONSUMER"] } },
        { path: "store/:id", name: "store-detail", component: StoreDetail, meta: { roles: ["CONSUMER"] } },
        { path: "my-orders", name: "my-orders", component: MyOrders, meta: { label: "我的订单", icon: "mdi-receipt", roles: ["CONSUMER"] } },
        { path: "cart", name: "cart", component: CartPage, meta: { label: "购物车", icon: "mdi-cart", roles: ["CONSUMER"] } },
        { path: "profile", name: "profile", component: ProfileCenter, meta: { label: "个人中心", icon: "mdi-account", roles: ["CONSUMER", "MERCHANT", "ADMIN"] } },
        { path: "consumer-products", name: "consumer-products", component: ConsumerProducts, meta: { label: "商品", icon: "mdi-shopping", roles: ["CONSUMER"] } },
        { path: "data-stats", name: "data-stats", component: DataStats, meta: { label: "数据统计", icon: "mdi-chart-areaspline", roles: ["ADMIN"] } },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.initialized) {
    await auth.bootstrap();
  }

  if (to.meta.public) {
    if (auth.isAuthenticated && to.name !== "Login" && to.name !== "Register") {
      const redirectTarget = typeof to.query.redirect === "string" ? to.query.redirect : "/";
      return { path: redirectTarget || "/" };
    }
    return true;
  }

  if (!auth.isAuthenticated) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    return { path: "/" };
  }

  if ((to.name === "dashboard" || to.path === "/") && auth.user?.role === "ADMIN") {
    return { name: "user-management" };
  }

  return true;
});

export default router;
