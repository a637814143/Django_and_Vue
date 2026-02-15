<script setup>
import { ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";

const loading = ref(false);
const error = ref("");
const stats = ref([]);
</script>

<template>
  <GlassCard title="数据统计" subtitle="等待接入真实数据">
    <p v-if="loading" class="muted">加载中...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="stats.length" class="muted">数据即将展示</p>
    <p v-else class="empty">暂无数据，接入后显示真实统计结果。</p>
  </GlassCard>
</template>

<style scoped>
.muted {
  color: #60756a;
}

.error {
  color: #b42318;
}

.empty {
  color: #6b7f73;
}
</style>
