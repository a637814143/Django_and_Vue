<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../../store/auth";

const props = defineProps({
  collapsed: { type: Boolean, default: false },
});
const emit = defineEmits(["toggle"]);

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const navItems = computed(() => {
  const userRole = auth.user?.role;
  if (!userRole) return [];

  return router.getRoutes()
    .filter(route =>
      route.meta &&
      route.meta.roles &&
      route.meta.roles.includes(userRole) &&
      route.meta.label
    )
    .map(route => ({
      label: route.meta.label,
      icon: route.meta.icon,
      to: { name: route.name },
    }));
});

const isActive = (item) => {
  if (item.to.name === "store" && route.name === "store-detail") return true;
  return route.name === item.to.name;
};

const go = (item) => {
  if (!isActive(item)) router.push(item.to);
};

const handleLogout = async () => {
  await auth.logout();
  router.push({ path: "/login" });
};

const isAdmin = computed(() => auth.user?.role === "ADMIN");
</script>

<template>
  <aside :class="['sidebar', { collapsed: collapsed, 'sidebar--admin': isAdmin }]">
    <div class="sidebar__brand">
      <div class="logo">
        <span>W</span>
      </div>
      <div v-if="!collapsed">
        <p class="brand-title">文创 Studio</p>
        <p class="brand-sub">校园灵感实验室</p>
      </div>
    </div>

    <nav class="sidebar__nav">
      <button
        v-for="item in navItems"
        :key="item.label"
        @click="go(item)"
        :class="['nav-link', { active: isActive(item) }]"
        :title="collapsed ? item.label : undefined"
      >
        <span>{{ item.icon }}</span>
        <span v-if="!collapsed">{{ item.label }}</span>
      </button>
    </nav>

    <div class="sidebar__footer">
      <div class="user-card" v-if="!collapsed">
        <div class="avatar">{{ auth.user?.username?.slice(0, 1)?.toUpperCase() }}</div>
        <div>
          <p class="username">{{ auth.user?.username }}</p>
          <p class="role">{{ auth.user?.role }}</p>
        </div>
      </div>
      <div class="footer-actions">
        <button class="logout" type="button" @click="emit('toggle')">
          {{ collapsed ? "展开" : "收起" }}
        </button>
        <button v-if="!collapsed" class="logout" type="button" @click="handleLogout">退出登录</button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  padding: 18px 16px;
  background: linear-gradient(180deg, rgba(245, 255, 250, 0.95), rgba(230, 248, 239, 0.95));
  border-right: 1px solid rgba(20, 120, 80, 0.1);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: width 0.2s ease, padding 0.2s ease;
}

.sidebar.collapsed {
  padding: 20px 12px;
  width: 88px;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6fcf97, #a8e6cf);
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 1.4rem;
  color: #0f3d2e;
}

.brand-title {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
}

.brand-sub {
  margin: 2px 0 0;
  font-size: 0.82rem;
  color: #4d6359;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.nav-link {
  border: none;
  border-radius: 14px;
  padding: 14px 18px;
  background: transparent;
  color: #1c3d2f;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 12px;
}

.nav-link:hover {
  background: rgba(111, 207, 151, 0.15);
}

.nav-link.active {
  background: linear-gradient(135deg, rgba(111, 207, 151, 0.4), rgba(168, 230, 207, 0.6));
  box-shadow: inset 0 0 0 1px rgba(111, 207, 151, 0.5);
}

.sidebar--admin .nav-link {
  font-size: 0.8rem;
}

.sidebar__footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #0f3d2e;
  color: white;
  display: grid;
  place-items: center;
  font-weight: 600;
}

.username {
  margin: 0;
  font-weight: 600;
}

.role {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: #4d6359;
}

.footer-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.logout {
  color: #1c3d2f;
  font-weight: 500;
  border: 1px solid rgba(20, 120, 80, 0.15);
  border-radius: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
}

.sidebar.collapsed .logout {
  text-align: center;
  padding: 10px 8px;
}

@media (max-width: 1024px) {
  .sidebar {
    flex-direction: row;
    align-items: center;
    flex-wrap: wrap;
    width: auto;
  }

  .sidebar.collapsed {
    width: auto;
    padding: 16px;
  }

  .sidebar__nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>
