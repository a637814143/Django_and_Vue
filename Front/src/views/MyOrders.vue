<script setup>
import { computed, onMounted, ref } from "vue";
import { orderApi, walletApi } from "../api";

const orders = ref([]);
const loading = ref(false);
const error = ref("");
const statusFilter = ref("ALL");
const refundLoading = ref(null);
const payLoading = ref(null);

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
  REJECTED: "商家已拒绝",
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

const canRefund = (order) =>
  ["PAID", "FULFILLED", "SHIPPED", "COMPLETED"].includes(order.status) &&
  (!order.refund_status || order.refund_status === "NONE" || order.refund_status === "REJECTED");

const requestRefund = async (order) => {
  refundLoading.value = order.id;
  error.value = "";
  try {
    await walletApi.refund({ order_id: order.id, action: "REQUEST" });
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "申请退款失败";
  } finally {
    refundLoading.value = null;
  }
};

const payOrder = async (order) => {
  payLoading.value = order.id;
  error.value = "";
  try {
    const items = [];
    for (const item of order.items || []) {
      const pid = Number(item.product_id ?? item.productId ?? item.product);
      if (!Number.isFinite(pid)) {
        throw new Error("订单商品缺少有效的商品ID，无法支付");
      }
      items.push({
        product_id: pid,
        quantity: item.quantity || 1,
        custom_details: item.custom_details || "",
      });
    }

    await walletApi.pay({
      order_id: order.id,
      amount: order.total_amount,
      items,
      note: order.note || "",
      shipping_address: order.shipping_address || "",
    });
    await loadOrders();
  } catch (err) {
    error.value = err?.response?.data?.detail || "支付失败";
  } finally {
    payLoading.value = null;
  }
};

onMounted(loadOrders);
</script>

<template>
  <v-container fluid>
    <v-card>
      <v-card-title>我的订单</v-card-title>
      <v-card-subtitle>查看购买记录并申请退款</v-card-subtitle>
      <v-card-text>
        <div class="d-flex ga-4 mb-4">
          <v-select
            v-model="statusFilter"
            :items="statusOptions"
            label="筛选订单状态"
            @update:modelValue="loadOrders"
            style="max-width: 220px"
          />
          <v-btn @click="loadOrders" :loading="loading">刷新</v-btn>
        </div>
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-progress-circular v-if="loading" indeterminate />
        <v-expansion-panels v-else>
          <v-expansion-panel v-for="order in filteredOrders" :key="order.id">
            <v-expansion-panel-title>
              #{{ order.order_number }}
              <v-chip
                class="ml-3"
                :color="order.status === 'COMPLETED' ? 'success' : order.status === 'CANCELLED' ? 'grey' : 'info'"
                size="small"
              >
                {{ statusLabels[order.status] || order.status }}
              </v-chip>
              <v-chip
                v-if="order.refund_status && order.refund_status !== 'NONE'"
                class="ml-2"
                color="warning"
                size="small"
              >
                {{ refundLabels[order.refund_status] || order.refund_status }}
              </v-chip>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <p>下单时间：{{ new Date(order.created_at).toLocaleString() }}</p>
              <p>总额：¥{{ Number(order.total_amount).toFixed(2) }}</p>
              <p>收货地址：{{ order.shipping_address || "未填写" }}</p>
              <p>支付方式：{{ order.payment_method || "钱包/线下" }}</p>
              <v-list density="compact">
                <v-list-item v-for="item in order.items" :key="item.id">
                  <v-list-item-title>{{ item.product }} × {{ item.quantity }}</v-list-item-title>
                  <v-list-item-subtitle>¥{{ Number(item.unit_price).toFixed(2) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <div class="d-flex ga-2 mt-3">
                <v-btn
                  v-if="order.status === 'CREATED'"
                  color="primary"
                  variant="tonal"
                  :loading="payLoading === order.id"
                  @click="payOrder(order)"
                >
                  支付
                </v-btn>
                <v-btn
                  v-if="canRefund(order)"
                  color="error"
                  variant="tonal"
                  :loading="refundLoading === order.id"
                  @click="requestRefund(order)"
                >
                  申请退款
                </v-btn>
                <v-chip v-else-if="order.refund_status && order.refund_status !== 'NONE'" color="warning" size="small">
                  {{ refundLabels[order.refund_status] || order.refund_status }}
                </v-chip>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
        <p v-if="!filteredOrders.length && !loading" class="mt-4">暂无订单</p>
      </v-card-text>
    </v-card>
  </v-container>
</template>
