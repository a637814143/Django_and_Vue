<script setup>
import { onMounted, ref } from "vue";
import { analyticsApi } from "../api";

const overview = ref(null);
const metrics = ref([]);
const loading = ref(true);

const headers = [
  { text: 'Key', value: 'key' },
  { text: '值', value: 'value' },
  { text: '时间', value: 'captured_at' },
];

const loadAnalytics = async () => {
  loading.value = true;
  try {
    const [ov, metricData] = await Promise.all([analyticsApi.overview(), analyticsApi.metrics()]);
    overview.value = ov;
    metrics.value = metricData.results ?? metricData;
  } finally {
    loading.value = false;
  }
};

onMounted(loadAnalytics);
</script>

<template>
  <v-container fluid>
    <v-row v-if="overview">
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>七日销售额</v-card-title>
          <v-card-text>
            <p class="text-h4">¥{{ Number(overview.sales_last_7_days).toFixed(2) }}</p>
            <p>稳步上扬</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>七日订单</v-card-title>
          <v-card-text>
            <p class="text-h4">{{ overview.orders_last_7_days }}</p>
            <p>客流高峰</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>定制心愿</v-card-title>
          <v-card-text>
            <p class="text-h4">{{ overview.custom_requests_last_7_days }}</p>
            <p>灵感不断</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-4">
      <v-card-title>指标快照</v-card-title>
      <v-card-subtitle>自动采集</v-card-subtitle>
      <v-data-table
        :headers="headers"
        :items="metrics"
        :loading="loading"
        class="elevation-1"
        no-data-text="暂无指标数据，请稍后再试"
      >
        <template v-slot:item.captured_at="{ item }">
          {{ new Date(item.captured_at).toLocaleString() }}
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>
