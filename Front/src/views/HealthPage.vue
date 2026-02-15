<script setup>
import { onMounted, ref } from "vue";
import { API_BASE_URL } from "../api/http";

const loading = ref(true);
const error = ref("");
const payload = ref(null);

const loadHealth = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await fetch(`${API_BASE_URL}health/`, { credentials: "include" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    payload.value = await res.json();
  } catch (err) {
    error.value = err?.message || "加载失败";
  } finally {
    loading.value = false;
  }
};

onMounted(loadHealth);
</script>

<template>
  <div>
    <h1>Health Check</h1>
    <p v-if="loading">加载中...</p>
    <p v-else-if="error" style="color: red">{{ error }}</p>
    <pre v-else>{{ JSON.stringify(payload, null, 2) }}</pre>
    <button type="button" @click="loadHealth">刷新</button>
  </div>
</template>
