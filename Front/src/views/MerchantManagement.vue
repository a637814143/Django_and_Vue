<script setup>
import { onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { accountApi } from "../api";

const merchants = ref([]);
const loading = ref(true);
const error = ref("");

const loadMerchants = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await accountApi.users({ role: "MERCHANT" });
    merchants.value = response.results ?? response;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载商家失败";
  } finally {
    loading.value = false;
  }
};

onMounted(loadMerchants);
</script>

<template>
  <GlassCard title="商家管理" subtitle="线上 / 线下店铺">
    <div v-if="loading" class="loading">加载中...</div>
    <p v-if="error" class="error">{{ error }}</p>
    <ul v-else class="merchant-list">
      <li v-for="merchant in merchants" :key="merchant.id">
        <div>
          <strong>{{ merchant.username }}</strong>
          <p>{{ merchant.headline || "暂无简介" }}</p>
        </div>
        <div class="meta">
          <span>邮箱：{{ merchant.email || "未绑定" }}</span>
          <span>最近登录：{{ merchant.last_login ? new Date(merchant.last_login).toLocaleDateString() : "—" }}</span>
        </div>
      </li>
      <li v-if="!merchants.length" class="empty">目前没有商家</li>
    </ul>
  </GlassCard>
</template>

<style scoped>
.merchant-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

li {
  border: 1px solid rgba(15, 45, 31, 0.12);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.85);
}

p {
  margin: 4px 0 0;
  color: #4d6359;
}

.meta {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: #4d6359;
}

.error {
  color: #b42318;
}

.loading {
  margin-bottom: 12px;
}

.empty {
  text-align: center;
  color: #6b7f73;
}
</style>
