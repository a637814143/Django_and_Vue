<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
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
const pageSize = 30;
const copiedCode = ref("");

const pagedVoucherHistory = computed(() => {
  const start = (voucherPage.value - 1) * pageSize;
  return voucherHistory.value.slice(start, start + pageSize);
});
const voucherPageCount = computed(() => Math.max(1, Math.ceil(voucherHistory.value.length / pageSize)));

const changeVoucherPage = (delta) => {
  const next = voucherPage.value + delta;
  if (next < 1 || next > voucherPageCount.value) return;
  voucherPage.value = next;
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
  <GlassCard title="系统管理" subtitle="钱包挡位 & 兑换码">
    <p v-if="loading" class="hint">加载中...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="form">
      <label>
        低档免审核上限（元）
        <input
          type="number"
          min="0"
          step="10"
          v-model.number="config.low_tier_limit"
          placeholder="例如 200"
        />
        <span class="hint">低于或等于该金额的订单直接扣款；超过则进入高档</span>
      </label>
      <label class="switch-row">
        <input type="checkbox" v-model="config.high_tier_requires_review" />
        <span>高档交易需审核后才能扣款</span>
      </label>
      <label class="switch-row">
        <input type="checkbox" v-model="config.enable_tiers" />
        <span>启用高/低挡规则（关闭后全部按余额直接扣款）</span>
      </label>
      <div class="actions">
        <button class="btn-outline" type="button" :disabled="saving" @click="loadConfig">重置</button>
        <button class="btn-primary" type="button" :disabled="saving" @click="saveConfig">
          {{ saving ? "保存中..." : "保存挡位" }}
        </button>
      </div>
      <p v-if="configSuccess" class="success">{{ configSuccess }}</p>

      <div class="divider"></div>

      <h4>生成兑换码</h4>
      <label>
        单个金额
        <input type="number" min="1" step="1" v-model.number="voucherAmount" />
      </label>
      <label>
        生成数量
        <input type="number" min="1" max="50" step="1" v-model.number="voucherCount" />
      </label>
      <div class="actions">
        <button class="btn-primary" type="button" :disabled="voucherSaving" @click="generateVouchers">
          {{ voucherSaving ? "生成中..." : "生成" }}
        </button>
      </div>
      <p v-if="voucherError" class="error">{{ voucherError }}</p>
      <p v-if="voucherSuccess" class="success">{{ voucherSuccess }}</p>
      <div v-if="voucherResult.length" class="voucher-list">
        <p class="hint">已生成兑换码（同时已扣除管理员余额）：</p>
        <div v-for="code in voucherResult" :key="code.code" class="voucher-chip" @click="copyCode(code.code)">
          <code>{{ code.code }}</code>
          <span>¥{{ code.amount }}</span>
          <small>创建于 {{ code.created_at ? new Date(code.created_at).toLocaleString() : "" }}</small>
          <small v-if="code.is_redeemed">已兑</small>
          <small v-if="copiedCode === code.code" class="copied">已复制</small>
        </div>
      </div>

      <div class="divider"></div>
      <div class="history-head">
        <h4>兑换码历史</h4>
        <div class="actions">
          <button class="btn-outline" type="button" :disabled="voucherHistoryLoading" @click="loadVoucherHistory">
            {{ voucherHistoryLoading ? "加载中..." : "刷新" }}
          </button>
        </div>
      </div>
      <p v-if="voucherHistoryError" class="error">{{ voucherHistoryError }}</p>
      <div class="voucher-list" v-if="voucherHistory.length">
        <div
          v-for="code in pagedVoucherHistory"
          :key="code.code"
          class="voucher-chip"
          @click="copyCode(code.code)"
        >
          <code>{{ code.code }}</code>
          <span>¥{{ code.amount }}</span>
          <small>创建：{{ code.created_at ? new Date(code.created_at).toLocaleString() : "-" }}</small>
          <small v-if="code.is_redeemed">
            已兑给 {{ code.redeemed_by || "用户" }} · {{ code.redeemed_at ? new Date(code.redeemed_at).toLocaleString() : "" }}
          </small>
          <small v-else>未兑换</small>
          <small v-if="copiedCode === code.code" class="copied">已复制</small>
        </div>
      </div>
      <p v-else-if="!voucherHistoryLoading" class="hint">暂无历史兑换码</p>
      <div class="pager" v-if="voucherHistory.length">
        <button class="btn-outline" :disabled="voucherPage === 1" @click="changeVoucherPage(-1)">上一页</button>
        <span class="hint">第 {{ voucherPage }} / {{ voucherPageCount }} 页</span>
        <button class="btn-outline" :disabled="voucherPage === voucherPageCount" @click="changeVoucherPage(1)">下一页</button>
      </div>
    </div>
  </GlassCard>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #0f2d1f;
  font-weight: 600;
}

input[type="number"] {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15, 45, 31, 0.12);
}

.switch-row {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-weight: 500;
  background: rgba(15, 45, 31, 0.04);
  padding: 10px 12px;
  border-radius: 12px;
}

.switch-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
}

.switch-row span {
  flex: 1;
  line-height: 1.4;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.hint {
  color: #60756a;
}

.error {
  color: #b42318;
  margin: 0;
}

.success {
  color: #0f5132;
  margin: 0;
}

.divider {
  height: 1px;
  background: rgba(15, 45, 31, 0.08);
}

.voucher-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.history-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.voucher-chip {
  background: rgba(15, 45, 31, 0.06);
  padding: 8px 10px;
  border-radius: 10px;
  display: grid;
  gap: 2px;
  min-width: 160px;
  cursor: pointer;
}

.copied {
  color: #0f5132;
}

.pager {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
</style>
