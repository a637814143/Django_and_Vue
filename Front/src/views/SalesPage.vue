<script setup>
import { computed, onMounted, ref } from "vue";
import { orderApi, walletApi } from "../api";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();

const orders = ref([]);
const loading = ref(false);
const error = ref("");
const statusFilter = ref("ALL");
const actionLoading = ref(null);

const statusLabels = {
  CREATED: "待支付",
  PAID: "已支付",
  FULFILLED: "已备货",
  SHIPPED: "已发货",
  COMPLETED: "已完成",
  CANCELLED: "已取消/退款",
};

const refundLabels = {
  NONE: "无退款",
  REQUESTED: "退款申请中",
  APPROVED: "已同意退款",
  REJECTED: "已拒绝",
};

const statusOptions = [
  { value: "ALL", title: "全部" },
  { value: "CREATED", title: "待支付" },
  { value: "PAID", title: "已支付" },
  { value: "FULFILLED", title: "已备货" },
  { value: "SHIPPED", title: "已发货" },
  { value: "COMPLETED", title: "已完成" },
  { value: "CANCELLED", title: "已取消/退款" },
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

const handleRefundAction = async (order, action) => {
  actionLoading.value = order.id;
  error.value = "";
  try {
    await walletApi.refund({ order_id: order.id, action });
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "处理退款失败";
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

const showRefundButtons = computed(() => auth.user?.role === "MERCHANT" || auth.user?.role === "ADMIN");
const showForceRefund = computed(() => auth.user?.role === "ADMIN");

onMounted(loadOrders);
</script>

<template>
  <v-container fluid>
    <v-card>
      <v-card-title>订单管理</v-card-title>
      <v-card-subtitle>查看并处理退款/发货</v-card-subtitle>
      <v-card-text>
        <div class="d-flex ga-4">
          <v-select
            v-model="statusFilter"
            :items="statusOptions"
            label="筛选订单状态"
            @update:modelValue="loadOrders"
            style="max-width: 220px"
          ></v-select>
          <v-btn @click="loadOrders" :loading="loading">刷新</v-btn>
        </div>
        <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
        <v-progress-circular v-if="loading" indeterminate class="mt-4"></v-progress-circular>
        <v-expansion-panels v-else>
          <v-expansion-panel v-for="order in filteredOrders" :key="order.id">
            <v-expansion-panel-title>
              #{{ order.order_number }} - {{ order.consumer }}
              <v-chip class="ml-2" size="small" color="info">{{ statusLabels[order.status] || order.status }}</v-chip>
              <v-chip
                v-if="order.refund_status && order.refund_status !== 'NONE'"
                class="ml-2"
                size="small"
                color="warning"
              >
                {{ refundLabels[order.refund_status] || order.refund_status }}
              </v-chip>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <p>下单时间：{{ new Date(order.created_at).toLocaleString() }}</p>
              <p>总额：¥{{ Number(order.total_amount).toFixed(2) }}</p>
              <p>支付方式：{{ order.payment_method || "钱包/线下" }}</p>
              <p>收货：{{ order.shipping_address || "未填写" }}</p>
              <v-list>
                <v-list-item v-for="item in order.items" :key="item.id">
                  <v-list-item-title>{{ item.product }} × {{ item.quantity }}</v-list-item-title>
                  <v-list-item-subtitle>¥{{ Number(item.unit_price).toFixed(2) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <div class="d-flex ga-2 mt-3" v-if="availableActions(order).length">
                <v-btn
                  v-for="action in availableActions(order)"
                  :key="action.value"
                  small
                  :loading="actionLoading === order.id"
                  @click="updateStatus(order, action.value)"
                >
                  {{ action.label }}
                </v-btn>
              </div>
              <div class="d-flex ga-2 mt-3" v-if="showRefundButtons">
                <v-btn
                  v-if="order.refund_status === 'REQUESTED'"
                  color="primary"
                  variant="tonal"
                  :loading="actionLoading === order.id"
                  @click="handleRefundAction(order, 'APPROVE')"
                >
                  同意退款
                </v-btn>
                <v-btn
                  v-if="order.refund_status === 'REQUESTED'"
                  color="warning"
                  variant="tonal"
                  :loading="actionLoading === order.id"
                  @click="handleRefundAction(order, 'REJECT')"
                >
                  拒绝退款
                </v-btn>
                <v-btn
                  v-if="showForceRefund"
                  color="error"
                  variant="flat"
                  :loading="actionLoading === order.id"
                  @click="handleRefundAction(order, 'FORCE')"
                >
                  强制退款
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </v-container>
</template>
