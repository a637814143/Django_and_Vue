import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";

const AppShell = () => import("../layouts/AppShell.vue");
const DashboardHome = () => import("../views/DashboardHome.vue");
const CatalogPage = () => import("../views/CatalogPage.vue");
const SalesPage = () => import("../views/SalesPage.vue");
const CustomizationPage = () => import("../views/CustomizationPage.vue");
const AnalyticsPage = () => import("../views/AnalyticsPage.vue");
const CommunityPage = () => import("../views/CommunityPage.vue");
const TerminalPage = () => import("../views/TerminalPage.vue");
const StorePage = () => import("../views/StorePage.vue");
const StoreDetail = () => import("../views/StoreDetail.vue");
const ConsumerProducts = () => import("../views/ConsumerProducts.vue");
const FeaturedFocus = () => import("../views/FeaturedFocus.vue");
const CartPage = () => import("../views/CartPage.vue");
const ProfileCenter = () => import("../views/ProfileCenter.vue");
const UserManagement = () => import("../views/UserManagement.vue");
const MerchantManagement = () => import("../views/MerchantManagement.vue");
const CategoryManagement = () => import("../views/CategoryManagement.vue");
const DataStats = () => import("../views/DataStats.vue");
const FocusAdmin = () => import("../views/FocusAdmin.vue");
const SystemManagement = () => import("../views/SystemManagement.vue");
const HealthPage = () => import("../views/HealthPage.vue");
const AuthLogin = () => import("../views/AuthLogin.vue");
const AuthRegister = () => import("../views/AuthRegister.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: AuthLogin,
      meta: { public: true },
    },
    {
      path: "/register",
      name: "register",
      component: AuthRegister,
      meta: { public: true },
    },
    {
      path: "/",
      component: AppShell,
      children: [
        {
          path: "",
          name: "dashboard",
          component: DashboardHome,
          meta: { label: "首页", icon: "🏠", roles: ["CONSUMER", "MERCHANT"] },
        },
        {
          path: "manage/users",
          name: "user-management",
          component: UserManagement,
          meta: { label: "用户管理", icon: "👥", roles: ["ADMIN"] },
        },
        {
          path: "manage/merchants",
          name: "merchant-management",
          component: MerchantManagement,
          meta: { label: "商家管理", icon: "🏬", roles: ["ADMIN"] },
        },
        {
          path: "manage/categories",
          name: "category-management",
          component: CategoryManagement,
          meta: { label: "分类管理", icon: "🗂️", roles: ["ADMIN", "MERCHANT"] },
        },
        {
          path: "catalog",
          name: "product-management",
          component: CatalogPage,
          meta: { label: "产品管理", icon: "📦", roles: ["ADMIN", "MERCHANT"] },
        },
        {
          path: "orders",
          name: "orders",
          component: SalesPage,
          meta: { label: "订单管理", icon: "📑", roles: ["MERCHANT"] },
        },
        {
          path: "store",
          name: "store",
          component: StorePage,
          meta: { label: "店铺", icon: "🏬", roles: ["CONSUMER"] },
        },
        {
          path: "store/:id",
          name: "store-detail",
          component: StoreDetail,
          meta: { roles: ["CONSUMER"] },
        },
        {
          path: "products",
          name: "consumer-products",
          component: ConsumerProducts,
          meta: { label: "产品", icon: "🛍️", roles: ["CONSUMER"] },
        },
        {
          path: "focus",
          name: "focus",
          component: FeaturedFocus,
          meta: { label: "好物聚焦", icon: "⭐", roles: ["CONSUMER", "MERCHANT"] },
        },
        {
          path: "cart",
          name: "cart",
          component: CartPage,
          meta: { label: "购物车", icon: "🛒", roles: ["CONSUMER"] },
        },
        {
          path: "profile",
          name: "profile",
          component: ProfileCenter,
          meta: { label: "个人中心", icon: "👤", roles: ["CONSUMER", "MERCHANT", "ADMIN"] },
        },
        {
          path: "custom",
          name: "custom",
          component: CustomizationPage,
          meta: { label: "个性定制", icon: "🎨", roles: ["CONSUMER", "MERCHANT", "ADMIN"] },
        },
        {
          path: "analytics",
          name: "analytics",
          component: AnalyticsPage,
          meta: { label: "销售分析", icon: "📈", roles: ["ADMIN", "MERCHANT"] },
        },
        {
          path: "stats",
          name: "data-stats",
          component: DataStats,
          meta: { label: "数据统计", icon: "📊", roles: ["ADMIN"] },
        },
        {
          path: "community",
          name: "community",
          component: CommunityPage,
          meta: { label: "互动社区", icon: "💬", roles: ["CONSUMER", "MERCHANT", "ADMIN"] },
        },
        {
          path: "terminal",
          name: "terminal",
          component: TerminalPage,
          meta: { label: "模拟终端", icon: "🖥️", roles: ["ADMIN"] },
        },
        {
          path: "focus-admin",
          name: "focus-admin",
          component: FocusAdmin,
          meta: { label: "好物聚焦管理", icon: "⭐", roles: ["ADMIN"] },
        },
        {
          path: "system",
          name: "system-management",
          component: SystemManagement,
          meta: { label: "系统管理", icon: "⚙️", roles: ["ADMIN"] },
        },
        {
          path: "health",
          name: "health",
          component: HealthPage,
          meta: { label: "健康状况", icon: "❤️‍🩹", roles: ["ADMIN"] },
        },
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
    if (auth.isAuthenticated && to.name !== "register") {
      const redirectTarget =
        typeof to.query.redirect === "string" ? to.query.redirect : "/";
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
