<script setup>
import { onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import MetricCard from "../components/ui/MetricCard.vue";
import { analyticsApi } from "../api";

const overview = ref(null);
const metrics = ref([]);

const loadAnalytics = async () => {
  const [ov, metricData] = await Promise.all([analyticsApi.overview(), analyticsApi.metrics()]);
  overview.value = ov;
  metrics.value = metricData.results ?? metricData;
};

onMounted(loadAnalytics);
</script>

<template>
  <section class="grid-3" v-if="overview">
    <MetricCard title="七日销售额" :value="`¥${Number(overview.sales_last_7_days).toFixed(2)}`" trend="稳步上扬" />
    <MetricCard title="七日订单" :value="overview.orders_last_7_days" trend="客流高峰" />
    <MetricCard title="定制心愿" :value="overview.custom_requests_last_7_days" trend="灵感不断" />
  </section>

  <GlassCard title="指标快照" subtitle="自动采集">
    <table>
      <thead>
        <tr>
          <th>Key</th>
          <th>值</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="metric in metrics" :key="metric.id">
          <td>{{ metric.key }}</td>
          <td>{{ metric.value }}</td>
          <td>{{ new Date(metric.captured_at).toLocaleString() }}</td>
        </tr>
        <tr v-if="!metrics.length">
          <td colspan="3">暂无指标数据，请稍后再试</td>
        </tr>
      </tbody>
    </table>
  </GlassCard>
</template>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(15, 45, 31, 0.08);
}
</style>
