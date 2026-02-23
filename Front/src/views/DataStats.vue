<script setup>
import { computed, onMounted, ref } from "vue";
import { analyticsApi } from "../api";

const stats = ref([]);
const loading = ref(false);
const error = ref("");

const insights = ref({
  total_revenue: 0,
  merchant_count: 0,
  product_count: 0,
  monthly_sales: [],
  merchant_sales: [],
  window_start: "",
  window_end: "",
});
const insightsLoading = ref(false);
const insightsError = ref("");

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

const monthlySales = computed(() => insights.value?.monthly_sales || []);
const salesValues = computed(() => monthlySales.value.map((item) => Number(item.amount || 0)));
const salesStartLabel = computed(() => {
  const first = monthlySales.value[0];
  return first ? first.date.slice(5) : "";
});
const salesEndLabel = computed(() => {
  const last = monthlySales.value[monthlySales.value.length - 1];
  return last ? last.date.slice(5) : "";
});
const merchantBars = computed(() => {
  const list = insights.value?.merchant_sales || [];
  if (!list.length) return [];
  const total = list.reduce((acc, m) => acc + Number(m.amount || 0), 0) || 1;
  return list.map((m) => {
    const amount = Number(m.amount || 0);
    return {
      name: m.merchant || `商家#${m.merchant_id}`,
      amount,
      percent: Math.round((amount / total) * 1000) / 10,
    };
  });
});

const loadInsights = async () => {
  insightsLoading.value = true;
  insightsError.value = "";
  try {
    const data = await analyticsApi.commerceInsights();
    insights.value = data;
  } catch (err) {
    insightsError.value = err?.response?.data?.detail || "运营总览获取失败";
  } finally {
    insightsLoading.value = false;
  }
};

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

const reloadAll = () => {
  loadInsights();
  loadStats();
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

onMounted(() => {
  loadInsights();
  loadStats();
});
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between flex-wrap">
            <div>
              <div class="text-h6">文创经营总览</div>
              <div class="text-caption text-medium-emphasis">
                总流水、商家规模与商品数，近30天走势与对比
              </div>
            </div>
            <v-btn color="primary" variant="tonal" @click="reloadAll" :loading="loading || insightsLoading">
              刷新
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-alert v-if="insightsError" type="error" class="mb-4">{{ insightsError }}</v-alert>
            <v-row>
              <v-col cols="12" md="4">
                <v-sheet class="pa-4" border rounded="lg">
                  <div class="text-caption text-medium-emphasis mb-1">总流水</div>
                  <div class="text-h5 font-weight-bold">¥{{ Number(insights.total_revenue || 0).toFixed(2) }}</div>
                  <div class="text-caption text-medium-emphasis">口径：已支付至已完成订单</div>
                </v-sheet>
              </v-col>
              <v-col cols="12" md="4">
                <v-sheet class="pa-4" border rounded="lg">
                  <div class="text-caption text-medium-emphasis mb-1">入驻商家</div>
                  <div class="text-h5 font-weight-bold">{{ insights.merchant_count }}</div>
                  <div class="text-caption text-medium-emphasis">活跃与新入驻商家总数</div>
                </v-sheet>
              </v-col>
              <v-col cols="12" md="4">
                <v-sheet class="pa-4" border rounded="lg">
                  <div class="text-caption text-medium-emphasis mb-1">文创产品</div>
                  <div class="text-h5 font-weight-bold">{{ insights.product_count }}</div>
                  <div class="text-caption text-medium-emphasis">当前上架/可售商品数量</div>
                </v-sheet>
              </v-col>
            </v-row>

            <v-row class="mt-2">
              <v-col cols="12" md="8">
                <v-card variant="outlined">
                  <v-card-title>所有文创产品近30天流水</v-card-title>
                  <v-card-text>
                    <v-progress-circular v-if="insightsLoading" indeterminate />
                    <v-alert v-else-if="!monthlySales.length" type="info">
                      最近30天暂无流水数据
                    </v-alert>
                    <div v-else>
                      <v-sparkline
                        :model-value="salesValues"
                        :height="180"
                        color="primary"
                        :smooth="12"
                        line-width="3"
                        fill
                      />
                      <div class="d-flex justify-space-between text-caption text-medium-emphasis mt-2">
                        <span>{{ salesStartLabel }}</span>
                        <span>窗口 {{ insights.window_start }} ~ {{ insights.window_end }}</span>
                        <span>{{ salesEndLabel }}</span>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card variant="outlined" class="h-100">
                  <v-card-title>商家营业额对比</v-card-title>
                  <v-card-text>
                    <v-progress-circular v-if="insightsLoading" indeterminate />
                    <v-alert v-else-if="!merchantBars.length" type="info">
                      暂无商家成交记录
                    </v-alert>
                    <div v-else class="d-flex flex-column ga-3">
                      <div v-for="bar in merchantBars" :key="bar.name" class="d-flex align-center ga-3">
                        <div class="text-body-2" style="width: 140px;">{{ bar.name }}</div>
                        <v-progress-linear :model-value="bar.percent" height="14" rounded color="indigo">
                          <template #default>
                            <span class="text-caption text-white px-2">{{ bar.percent.toFixed(1) }}%</span>
                          </template>
                        </v-progress-linear>
                        <div class="text-body-2 font-weight-medium" style="width: 90px;">
                          ¥{{ bar.amount.toFixed(2) }}
                        </div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-4">
      <v-card-title>用户互动与消费明细</v-card-title>
      <v-card-subtitle>登录、消费、评价与退款概览</v-card-subtitle>
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
