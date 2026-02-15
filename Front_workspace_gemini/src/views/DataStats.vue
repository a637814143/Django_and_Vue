<script setup>
import { onMounted, ref } from "vue";
import { analyticsApi } from "../api";

const loading = ref(false);
const error = ref("");
const stats = ref([]);

const headers = [
  { title: "用户", key: "username" },
  { title: "角色", key: "role" },
  { title: "登录次数", key: "login_count" },
  { title: "消费者消费额", key: "consumer_spend" },
  { title: "商家成交额", key: "merchant_sales" },
  { title: "评论次数", key: "comment_count" },
  { title: "退款次数", key: "refund_count" },
  { title: "日志", key: "actions", sortable: false },
];

const roleLabel = (role) => {
  switch (role) {
    case "ADMIN":
      return "管理员";
    case "MERCHANT":
      return "商家";
    case "CONSUMER":
      return "消费者";
    default:
      return role || "-";
  }
};

const logDialog = ref(false);
const logLoading = ref(false);
const logError = ref("");
const logUser = ref(null);
const loginLogs = ref([]);
const sessionLogs = ref([]);

const loadStats = async () => {
  loading.value = true;
  error.value = "";
  try {
    const data = await analyticsApi.userStats();
    stats.value = data;
  } catch (err) {
    error.value = err?.response?.data?.detail || "统计数据获取失败";
  } finally {
    loading.value = false;
  }
};

const openLogs = async (user) => {
  logDialog.value = true;
  logLoading.value = true;
  logError.value = "";
  logUser.value = user;
  loginLogs.value = [];
  sessionLogs.value = [];
  try {
    const data = await analyticsApi.userLogs(user.id);
    loginLogs.value = data.login_logs || [];
    sessionLogs.value = data.sessions || [];
  } catch (err) {
    logError.value = err?.response?.data?.detail || "日志获取失败";
  } finally {
    logLoading.value = false;
  }
};

onMounted(loadStats);
</script>

<template>
  <v-container fluid>
    <v-card>
      <v-card-title>数据统计</v-card-title>
      <v-card-subtitle>用户登录、消费与互动概览</v-card-subtitle>
      <v-card-text>
        <v-progress-circular v-if="loading" indeterminate />
        <v-alert v-else-if="error" type="error">{{ error }}</v-alert>
        <v-data-table
          v-else
          :headers="headers"
          :items="stats"
          item-value="id"
          class="elevation-1"
        >
          <template #item.role="{ item }">
            {{ roleLabel(item.role) }}
          </template>
          <template #item.consumer_spend="{ item }">
            ¥{{ Number(item.consumer_spend || 0).toFixed(2) }}
          </template>
          <template #item.merchant_sales="{ item }">
            ¥{{ Number(item.merchant_sales || 0).toFixed(2) }}
          </template>
          <template #item.actions="{ item }">
            <v-btn size="small" variant="tonal" @click="openLogs(item)">查看</v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="logDialog" max-width="900">
      <v-card>
        <v-card-title>
          日志 - {{ logUser?.username || "" }}
        </v-card-title>
        <v-card-text>
          <v-progress-circular v-if="logLoading" indeterminate />
          <v-alert v-else-if="logError" type="error">{{ logError }}</v-alert>
          <div v-else>
            <h4 class="mb-2">登录日志</h4>
            <v-table density="compact">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>IP</th>
                  <th>User-Agent/OS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(log, idx) in loginLogs" :key="idx">
                  <td>{{ new Date(log.created_at).toLocaleString() }}</td>
                  <td>{{ log.ip_address || "-" }}</td>
                  <td>{{ log.user_agent || "-" }}</td>
                </tr>
                <tr v-if="!loginLogs.length">
                  <td colspan="3" class="text-center">暂无登录日志</td>
                </tr>
              </tbody>
            </v-table>

            <h4 class="mt-6 mb-2">会话/过期</h4>
            <v-table density="compact">
              <thead>
                <tr>
                  <th>创建时间</th>
                  <th>过期时间</th>
                  <th>状态</th>
                  <th>User-Agent</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(sess, idx) in sessionLogs" :key="'s'+idx">
                  <td>{{ new Date(sess.created_at).toLocaleString() }}</td>
                  <td>{{ new Date(sess.expires_at).toLocaleString() }}</td>
                  <td>{{ sess.is_active ? "活跃" : "已失效" }}</td>
                  <td>{{ sess.user_agent || "-" }}</td>
                </tr>
                <tr v-if="!sessionLogs.length">
                  <td colspan="4" class="text-center">暂无会话记录</td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="logDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
