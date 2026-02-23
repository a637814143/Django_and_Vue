<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { walletApi } from "../api";

const config = reactive({
  low_tier_limit: 200,
  high_tier_requires_review: true,
  enable_tiers: true,
});

const loading = ref(false);
const saving = ref(false);
const error = ref("");
const configSuccess = ref("");

const voucherAmount = ref(50);
const voucherCount = ref(1);
const voucherResult = ref([]);
const voucherError = ref("");
const voucherSaving = ref(false);
const voucherSuccess = ref("");

const voucherHistory = ref([]);
const voucherHistoryLoading = ref(false);
const voucherHistoryError = ref("");
const voucherPage = ref(1);
const pageSize = 10;
const copiedCode = ref("");

const voucherHistoryHeaders = [
    { text: 'Code', value: 'code' },
    { text: 'Amount', value: 'amount' },
    { text: 'Created At', value: 'created_at' },
    { text: 'Redeemed', value: 'is_redeemed' },
    { text: 'Redeemed By', value: 'redeemed_by' },
    { text: 'Redeemed At', value: 'redeemed_at' },
    { text: 'Actions', value: 'actions', sortable: false },
]

const pagedVoucherHistory = computed(() => {
  const start = (voucherPage.value - 1) * pageSize;
  return voucherHistory.value.slice(start, start + pageSize);
});
const voucherPageCount = computed(() => Math.max(1, Math.ceil(voucherHistory.value.length / pageSize)));

const changeVoucherPage = (page) => {
  voucherPage.value = page;
};

const loadConfig = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await walletApi.config();
    config.low_tier_limit = Number(res.low_tier_limit ?? res.free_limit ?? 200);
    config.high_tier_requires_review = res.high_tier_requires_review ?? true;
    config.enable_tiers = res.enable_tiers ?? true;
  } catch (err) {
    error.value = err?.response?.data?.detail || "无法加载钱包挡位配置";
  } finally {
    loading.value = false;
  }
};

const saveConfig = async () => {
  error.value = "";
  configSuccess.value = "";
  saving.value = true;
  try {
    const payload = {
      low_tier_limit: Number(config.low_tier_limit) || 0,
      high_tier_requires_review: Boolean(config.high_tier_requires_review),
      enable_tiers: Boolean(config.enable_tiers),
    };
    const res = await walletApi.updateConfig(payload);
    configSuccess.value = res?.detail || "已保存挡位设置";
  } catch (err) {
    error.value = err?.response?.data?.detail || "保存失败，请稍后重试";
  } finally {
    saving.value = false;
  }
};

const loadVoucherHistory = async () => {
  voucherHistoryLoading.value = true;
  voucherHistoryError.value = "";
  try {
    const res = await walletApi.vouchers();
    voucherHistory.value = res ?? [];
    voucherPage.value = 1;
  } catch (err) {
    voucherHistoryError.value = err?.response?.data?.detail || "兑换码列表加载失败";
  } finally {
    voucherHistoryLoading.value = false;
  }
};

const generateVouchers = async () => {
  voucherError.value = "";
  voucherSuccess.value = "";
  voucherResult.value = [];
  if (!voucherAmount.value || voucherAmount.value <= 0) {
    voucherError.value = "请输入兑换码金额";
    return;
  }
  if (!voucherCount.value || voucherCount.value < 1) {
    voucherError.value = "请输入生成数量";
    return;
  }
  voucherSaving.value = true;
  try {
    const res = await walletApi.generateVouchers({
      amount: Number(voucherAmount.value),
      count: Number(voucherCount.value),
    });
    voucherResult.value = res.codes || [];
    voucherSuccess.value = res.detail || "兑换码已生成";
    await loadVoucherHistory();
  } catch (err) {
    voucherError.value = err?.response?.data?.detail || "生成失败，请稍后重试";
  } finally {
    voucherSaving.value = false;
  }
};

const copyCode = async (code) => {
  copiedCode.value = "";
  try {
    await navigator.clipboard.writeText(code);
    copiedCode.value = code;
    setTimeout(() => {
      if (copiedCode.value === code) copiedCode.value = "";
    }, 1800);
  } catch {
    // ignore
  }
};

onMounted(() => {
  loadConfig();
  loadVoucherHistory();
});
</script>

<template>
    <v-container fluid>
        <v-card>
            <v-card-title>系统管理</v-card-title>
            <v-card-subtitle>钱包挡位 & 兑换码</v-card-subtitle>
            <v-card-text>
                <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
                <v-alert v-else-if="error" type="error">{{ error }}</v-alert>
                <v-form v-else>
                    <v-text-field
                        v-model.number="config.low_tier_limit"
                        label="低档免审核上限（元）"
                        type="number"
                        min="0"
                        step="10"
                        placeholder="例如 200"
                        hint="低于或等于该金额的订单直接扣款；超过则进入高档"
                        persistent-hint
                    ></v-text-field>
                    <v-switch v-model="config.high_tier_requires_review" label="高档交易需审核后才能扣款" color="primary"></v-switch>
                    <v-switch v-model="config.enable_tiers" label="启用高/低挡规则（关闭后全部按余额直接扣款）" color="primary"></v-switch>
                    <div class="d-flex ga-2">
                        <v-btn @click="loadConfig" :disabled="saving">重置</v-btn>
                        <v-btn color="primary" @click="saveConfig" :loading="saving">{{ saving ? "保存中..." : "保存挡位" }}</v-btn>
                    </div>
                     <v-alert v-if="configSuccess" type="success" class="mt-4">{{ configSuccess }}</v-alert>
                </v-form>
                <v-divider class="my-4"></v-divider>
                <h4>生成兑换码</h4>
                <v-form>
                    <v-text-field v-model.number="voucherAmount" label="单个金额" type="number" min="1" step="1"></v-text-field>
                    <v-text-field v-model.number="voucherCount" label="生成数量" type="number" min="1" max="50" step="1"></v-text-field>
                    <v-btn color="primary" @click="generateVouchers" :loading="voucherSaving">{{ voucherSaving ? "生成中..." : "生成" }}</v-btn>
                    <v-alert v-if="voucherError" type="error" class="mt-4">{{ voucherError }}</v-alert>
                    <v-alert v-if="voucherSuccess" type="success" class="mt-4">{{ voucherSuccess }}</v-alert>
                    <v-chip-group v-if="voucherResult.length" class="mt-4" column>
                        <v-chip v-for="code in voucherResult" :key="code.code" @click="copyCode(code.code)">
                            {{ code.code }} - ¥{{ code.amount }}
                            <v-icon v-if="copiedCode === code.code" right>mdi-content-copy</v-icon>
                        </v-chip>
                    </v-chip-group>
                </v-form>
                <v-divider class="my-4"></v-divider>
                 <div class="d-flex justify-space-between align-center">
                    <h4>兑换码历史</h4>
                    <v-btn @click="loadVoucherHistory" :loading="voucherHistoryLoading">{{ voucherHistoryLoading ? '加载中...' : '刷新' }}</v-btn>
                </div>
                <v-alert v-if="voucherHistoryError" type="error" class="mt-4">{{ voucherHistoryError }}</v-alert>
                <v-data-table
                    :headers="voucherHistoryHeaders"
                    :items="voucherHistory"
                    :loading="voucherHistoryLoading"
                    :page.sync="voucherPage"
                    :items-per-page="pageSize"
                    @page-count="voucherPageCount = $event"
                    class="elevation-1 mt-4"
                >
                    <template v-slot:item.is_redeemed="{ item }">
                        <v-chip :color="item.is_redeemed ? 'success' : 'grey'">{{ item.is_redeemed ? '已兑换' : '未兑换' }}</v-chip>
                    </template>
                     <template v-slot:item.actions="{ item }">
                        <v-btn size="small" variant="text" prepend-icon="mdi-content-copy" @click="copyCode(item.code)">
                            复制
                        </v-btn>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-container>
</template>
