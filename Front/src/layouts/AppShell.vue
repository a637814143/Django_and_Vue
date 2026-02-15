<script setup>
import { ref } from "vue";
import SidebarNav from "../components/navigation/SidebarNav.vue";
import TopBar from "../components/navigation/TopBar.vue";
import { useAuthStore } from "../store/auth";

useAuthStore();
const isCollapsed = ref(false);
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<template>
  <div :class="['shell', { 'shell--collapsed': isCollapsed }]">
    <SidebarNav :collapsed="isCollapsed" @toggle="toggleSidebar" />
    <div class="shell__main">
      <TopBar />
      <main class="shell__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: 300px 1fr;
  min-height: 100vh;
  backdrop-filter: blur(20px);
  transition: grid-template-columns 0.2s ease;
}

.shell--collapsed {
  grid-template-columns: 88px 1fr;
}

.shell__main {
  background: linear-gradient(150deg, rgba(225, 250, 240, 0.9), rgba(235, 242, 255, 0.8));
  padding: 32px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100vh;
  overflow: hidden;
}

.shell__content {
  flex: 1;
  min-height: 0;
  max-height: calc(100vh - 140px);
  overflow: auto;
}

@media (max-width: 1024px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .shell--collapsed {
    grid-template-columns: 1fr;
  }

  .shell__main {
    padding: 24px 20px 48px;
  }
}
</style>
