<script setup>
import { computed, onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { orderApi } from "../api";

const orders = ref([]);
const loading = ref(false);
const error = ref("");
const statusFilter = ref("ALL");
const actionLoading = ref(null);

const statusLabels = {
  CREATED: "待付款",
  PAID: "已支付",
  FULFILLED: "已备货",
  SHIPPED: "已发货",
  COMPLETED: "已完成",
  CANCELLED: "已取消/退款",
};

const statusOptions = [
  { value: "ALL", label: "全部" },
  { value: "CREATED", label: "待付款" },
  { value: "PAID", label: "已支付" },
  { value: "FULFILLED", label: "已备货" },
  { value: "SHIPPED", label: "已发货" },
  { value: "COMPLETED", label: "已完成" },
  { value: "CANCELLED", label: "已取消" },
];

const filteredOrders = computed(() => {
  if (statusFilter.value === "ALL") return orders.value;
  return orders.value.filter((o) => o.status === statusFilter.value);
});

const loadOrders = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = statusFilter.value === "ALL" ? {} : { status: statusFilter.value };
    const res = await orderApi.list({ ...params, page_size: 100 });
    orders.value = res.results ?? res ?? [];
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载订单失败";
  } finally {
    loading.value = false;
  }
};

const updateStatus = async (order, status) => {
  actionLoading.value = order.id;
  try {
    await orderApi.updateStatus(order.id, { status });
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "更新状态失败";
  } finally {
    actionLoading.value = null;
  }
};

const availableActions = (order) => {
  const actions = [];
  if (order.status === "PAID") actions.push({ label: "标记备货", value: "FULFILLED" });
  if (order.status === "FULFILLED") actions.push({ label: "标记发货", value: "SHIPPED" });
  if (order.status === "SHIPPED") actions.push({ label: "完成订单", value: "COMPLETED" });
  if (["PAID", "FULFILLED", "SHIPPED"].includes(order.status))
    actions.push({ label: "取消/退款", value: "CANCELLED" });
  return actions;
};

onMounted(loadOrders);
</script>

<template>
  <div class="page">
    <header class="page-head">
      <div>
        <p class="eyebrow">订单管理</p>
        <h1>商家订单中心</h1>
        <p class="hint">查看消费者订单、跟进发货与处理退款</p>
      </div>
      <div class="filters">
        <select v-model="statusFilter" @change="loadOrders">
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <button class="btn-outline" type="button" @click="loadOrders">刷新</button>
      </div>
    </header>

    <GlassCard title="订单列表">
      <p v-if="loading" class="hint">加载中...</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="order-list">
        <article v-for="order in filteredOrders" :key="order.id" class="order-card">
          <header>
            <div>
              <p class="eyebrow">#{{ order.order_number }}</p>
              <h3>{{ order.consumer }}</h3>
              <p class="hint">下单时间：{{ new Date(order.created_at).toLocaleString() }}</p>
            </div>
            <div class="status-pill" :data-status="order.status">
              {{ statusLabels[order.status] || order.status }}
            </div>
          </header>
          <div class="items">
            <div v-for="item in order.items" :key="item.id" class="item-row">
              <span>{{ item.product }} × {{ item.quantity }}</span>
              <span>¥{{ Number(item.unit_price).toFixed(2) }}</span>
            </div>
          </div>
          <div class="meta">
            <span>总额：<strong>¥{{ Number(order.total_amount).toFixed(2) }}</strong></span>
            <span>支付方式：{{ order.payment_method || "钱包/线下" }}</span>
            <span>收货：{{ order.shipping_address || "未填写" }}</span>
          </div>
          <div class="actions" v-if="availableActions(order).length">
            <button
              v-for="action in availableActions(order)"
              :key="action.value"
              class="btn-outline"
              :disabled="actionLoading === order.id"
              @click="updateStatus(order, action.value)"
            >
              {{ actionLoading === order.id ? "处理中..." : action.label }}
            </button>
          </div>
        </article>
        <p v-if="!filteredOrders.length && !loading" class="empty">暂无订单</p>
      </div>
    </GlassCard>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(15, 45, 31, 0.12);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  border: 1px solid rgba(15, 45, 31, 0.1);
  border-radius: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.85);
}

header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.status-pill {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 45, 31, 0.08);
  font-weight: 600;
}

.status-pill[data-status="PAID"] {
  background: rgba(111, 207, 151, 0.2);
}

.status-pill[data-status="SHIPPED"],
.status-pill[data-status="FULFILLED"] {
  background: rgba(59, 130, 246, 0.15);
}

.status-pill[data-status="COMPLETED"] {
  background: rgba(16, 185, 129, 0.2);
}

.status-pill[data-status="CANCELLED"] {
  background: rgba(255, 99, 132, 0.2);
}

.items {
  margin: 10px 0;
  display: grid;
  gap: 6px;
}

.item-row {
  display: flex;
  justify-content: space-between;
  color: #0f2d1f;
}

.meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  color: #4d6359;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.empty {
  color: #6b7f73;
}

.hint {
  color: #4d6359;
  margin: 0;
}

.error {
  color: #b42318;
}

.btn-outline {
  border: 1px solid rgba(15, 45, 31, 0.2);
  border-radius: 10px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
}
</style>
