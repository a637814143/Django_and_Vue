<script setup>
import { onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { adminApi } from "../api";

const logs = ref([]);
const command = ref("");
const running = ref(false);
const error = ref("");

const loadHistory = async () => {
  try {
    const data = await adminApi.history();
    logs.value = data;
  } catch (err) {
    error.value = err?.response?.data?.detail || "无法加载历史记录";
  }
};

const execute = async () => {
  if (!command.value.trim() || running.value) return;
  running.value = true;
  error.value = "";
  try {
    const result = await adminApi.runCommand({ command: command.value });
    logs.value = [result, ...logs.value].slice(0, 20);
    command.value = "";
  } catch (err) {
    error.value = err?.response?.data?.detail || "执行失败";
  } finally {
    running.value = false;
  }
};

onMounted(loadHistory);
</script>

<template>
  <GlassCard title="模拟终端" subtitle="管理员专属">
    <div class="terminal">
      <div v-for="log in logs" :key="log.id" class="entry">
        <p class="command">💻 {{ log.command }}</p>
        <pre>{{ log.output || "(无输出)" }}</pre>
        <div class="meta">
          <span>退出码: {{ log.exit_code }}</span>
          <span>{{ new Date(log.created_at).toLocaleString() }}</span>
        </div>
      </div>
      <p v-if="!logs.length" class="placeholder">暂无历史命令</p>
    </div>
    <form @submit.prevent="execute" class="form">
      <input v-model="command" placeholder="例：python manage.py showmigrations" />
      <button class="btn-primary" :disabled="running">运行</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </GlassCard>
</template>

<style scoped>
.terminal {
  min-height: 280px;
  max-height: 480px;
  background: #0f2d1f;
  color: #b1f2d0;
  border-radius: 16px;
  padding: 16px;
  font-family: "Fira Code", "JetBrains Mono", monospace;
  margin-bottom: 16px;
  overflow-y: auto;
}

.entry + .entry {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.command {
  margin: 0 0 8px;
  color: #7efbb5;
}

pre {
  margin: 0;
  white-space: pre-wrap;
}

.meta {
  margin-top: 6px;
  font-size: 0.85rem;
  color: #8fbfa9;
  display: flex;
  justify-content: space-between;
}

.placeholder {
  color: #7aa590;
}

.form {
  display: flex;
  gap: 12px;
}

.form input {
  flex: 1;
}

.error {
  color: #f87171;
  margin-top: 8px;
}
</style>
