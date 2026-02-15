<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../../store/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const navItems = computed(() => [
  { label: "首页", to: { name: "dashboard" }, icon: "🏠" },
  { label: "店铺", to: { name: "store" }, icon: "🏬" },
  { label: "产品", to: { name: "consumer-products" }, icon: "🛍️" },
  { label: "好物聚焦", to: { name: "focus" }, icon: "✨" },
  { label: "购物车", to: { name: "cart" }, icon: "🛒" },
  { label: "互动社区", to: { name: "community" }, icon: "💬" },
  { label: "个人中心", to: { name: "profile" }, icon: "👤" },
]);

const isActive = (item) => {
  if (item.to.name === "store" && route.name === "store-detail") return true;
  return route.name === item.to.name;
};

const go = (item) => {
  if (!isActive(item)) {
    router.push(item.to);
  }
};

const handleLogout = () => {
  auth.logout().finally(() => {
    router.push({ path: "/login" });
  });
};
</script>

<template>
  <nav class="consumer-nav" aria-label="消费者导航">
    <div class="nav-center">
      <button
        v-for="item in navItems"
        :key="item.label"
        :class="['nav-pill', { active: isActive(item) }]"
        @click="go(item)"
      >
        <span class="icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>
    <button class="ghost" type="button" @click="handleLogout">退出</button>
  </nav>
</template>

<style scoped>
.consumer-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 40px 0;
  gap: 16px;
}

.nav-center {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  flex: 1;
}

.nav-pill {
  border-radius: 16px;
  padding: 12px 20px;
  border: 1px solid rgba(15, 45, 31, 0.18);
  background: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-pill.active {
  background: rgba(15, 45, 31, 0.1);
  border-color: rgba(15, 45, 31, 0.4);
  color: #0f2d1f;
}

.icon {
  font-size: 1rem;
}

.ghost {
  border: 1px solid rgba(15, 45, 31, 0.35);
  border-radius: 12px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-weight: 600;
}

@media (max-width: 768px) {
  .consumer-nav {
    flex-direction: column;
    padding: 16px 20px 0;
  }

  .ghost {
    width: 100%;
  }
}
</style>
