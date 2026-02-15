<script setup>
import { useAuthStore } from "../../store/auth";

const auth = useAuthStore();
</script>

<template>
  <header class="top-bar">
    <div>
      <p class="eyebrow">欢迎回来</p>
      <h2>{{ auth.user?.first_name || auth.user?.username }}，今日也要灵感满满</h2>
    </div>
  </header>
</template>

<style scoped>
.top-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.75rem;
  color: #5c6f63;
  margin: 0 0 8px;
}

h2 {
  margin: 0;
  font-size: 1.6rem;
  color: #0f2d1f;
}
</style>
