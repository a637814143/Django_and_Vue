<script setup>
import { onMounted, ref } from "vue";
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
    <v-container fluid>
        <v-card>
            <v-card-title>模拟终端</v-card-title>
            <v-card-subtitle>管理员专属</v-card-subtitle>
            <v-card-text>
                <v-card color="black" dark>
                    <v-card-text>
                        <div v-for="log in logs" :key="log.id">
                            <p class="command">> {{ log.command }}</p>
                            <pre>{{ log.output || "(无输出)" }}</pre>
                            <div class="meta">
                                <span>退出码: {{ log.exit_code }}</span>
                                <span>{{ new Date(log.created_at).toLocaleString() }}</span>
                            </div>
                        </div>
                        <p v-if="!logs.length">暂无历史命令</p>
                    </v-card-text>
                </v-card>
                 <v-form @submit.prevent="execute" class="mt-4">
                    <v-text-field
                        v-model="command"
                        label="输入命令"
                        placeholder="例：python manage.py showmigrations"
                        append-inner-icon="mdi-send"
                        @click:append-inner="execute"
                        :disabled="running"
                        :loading="running"
                    ></v-text-field>
                </v-form>
                <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<style scoped>
.command {
  color: #4caf50;
}
.meta {
    font-size: 0.8rem;
    color: #9e9e9e;
}
pre {
    white-space: pre-wrap;
    word-break: break-all;
}
</style>
