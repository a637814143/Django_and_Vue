<script setup>
import { computed, onMounted, ref, watch } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { useAuthStore } from "../store/auth";
import { accountApi, walletApi, addressApi } from "../api";

const auth = useAuthStore();
const avatarPreview = ref("");
const uploadError = ref("");
const uploadSuccess = ref("");
const uploading = ref(false);
const fileInput = ref(null);
const storeName = ref("");
const storeNameSaving = ref(false);
const storeNameError = ref("");
const storeNameSuccess = ref("");

const wallet = ref(null);
const walletLoading = ref(false);
const walletError = ref("");
const redeemCode = ref("");
const redeemMsg = ref("");
const redeemError = ref("");
const redeeming = ref(false);
const addresses = ref([]);
const addressForm = ref({
  receiver_name: "",
  phone: "",
  dorm_building: "",
  dorm_room: "",
  detail: "",
  is_default: true,
});
const addressError = ref("");
const addressSuccess = ref("");
const addressLoading = ref(false);
const isMerchant = computed(() => auth.user?.role === "MERCHANT");
const isConsumer = computed(() => auth.user?.role === "CONSUMER");

const syncPreview = () => {
  avatarPreview.value = auth.user?.avatar || auth.user?.avatar_url || "";
};

const refreshProfile = async () => {
  await auth.fetchProfile();
  syncPreview();
  storeName.value = auth.user?.store_name || "";
};

const loadWallet = async () => {
  walletLoading.value = true;
  walletError.value = "";
  try {
    const data = await walletApi.overview();
    wallet.value = {
      balance: Number(data.balance) || 0,
      tier: data.tier || "LOW",
      low_tier_limit: data.low_tier_limit ?? data.free_limit ?? 200,
      pending_review: Boolean(data.pending_review),
      enable_tiers: data.enable_tiers ?? true,
      high_tier_requires_review: data.high_tier_requires_review ?? true,
    };
  } catch (err) {
    walletError.value = err?.response?.data?.detail || "钱包信息获取失败";
  } finally {
    walletLoading.value = false;
  }
};

const loadAddresses = async () => {
  addressLoading.value = true;
  addressError.value = "";
  try {
    const res = await addressApi.list();
    addresses.value = res.results ?? res;
  } catch (err) {
    addressError.value = err?.response?.data?.detail || "地址获取失败";
  } finally {
    addressLoading.value = false;
  }
};

const triggerUpload = () => {
  fileInput.value?.click();
};

const handleFileChange = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  uploadError.value = "";
  uploadSuccess.value = "";
  if (!file.type.startsWith("image/")) {
    uploadError.value = "请上传图片格式文件";
    return;
  }
  const maxBytes = 5 * 1024 * 1024;
  if (file.size > maxBytes) {
    uploadError.value = "头像不能超过 5MB";
    return;
  }
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      uploading.value = true;
      await accountApi.updateProfile({ avatar_data: reader.result });
      uploadSuccess.value = "头像已更新";
      await refreshProfile();
      event.target.value = "";
    } catch (err) {
      uploadError.value = err?.response?.data?.detail || "上传失败";
    } finally {
      uploading.value = false;
    }
  };
  reader.readAsDataURL(file);
};

const clearAvatar = async () => {
  uploadError.value = "";
  uploadSuccess.value = "";
  try {
    uploading.value = true;
    await accountApi.updateProfile({ avatar_data: "" });
    uploadSuccess.value = "头像已清空";
    await refreshProfile();
  } catch (err) {
    uploadError.value = err?.response?.data?.detail || "清空失败";
  } finally {
    uploading.value = false;
  }
};

const redeem = async () => {
  redeemMsg.value = "";
  redeemError.value = "";
  if (!redeemCode.value.trim()) {
    redeemError.value = "请输入兑换码";
    return;
  }
  redeeming.value = true;
  try {
    const res = await walletApi.redeemVoucher({ code: redeemCode.value.trim() });
    redeemMsg.value = res.detail || `已兑入 ¥${res.amount}`;
    await loadWallet();
    redeemCode.value = "";
  } catch (err) {
    redeemError.value = err?.response?.data?.detail || "兑换失败";
  } finally {
    redeeming.value = false;
  }
};

const submitAddress = async () => {
  addressError.value = "";
  addressSuccess.value = "";
  const payload = { ...addressForm.value };
  try {
    await addressApi.create(payload);
    addressSuccess.value = "地址已保存";
    Object.assign(addressForm.value, {
      receiver_name: "",
      phone: "",
      dorm_building: "",
      dorm_room: "",
      detail: "",
      is_default: addresses.value.length === 0,
    });
    await loadAddresses();
  } catch (err) {
    addressError.value =
      err?.response?.data?.detail ||
      err?.response?.data?.receiver_name?.[0] ||
      "保存地址失败";
  }
};

const removeAddress = async (address) => {
  await addressApi.remove(address.id);
  await loadAddresses();
};

watch(
  () => auth.user,
  () => {
    syncPreview();
    storeName.value = auth.user?.store_name || "";
  },
  { immediate: true },
);

watch(
  () => auth.user?.role,
  (role, prev) => {
    if (role === prev) return;
    if (isConsumer.value) {
      loadWallet();
      loadAddresses();
    } else {
      wallet.value = null;
      addresses.value = [];
    }
  },
);

onMounted(() => {
  syncPreview();
  if (isConsumer.value) {
    loadWallet();
    loadAddresses();
  }
});

const saveStoreName = async () => {
  storeNameError.value = "";
  storeNameSuccess.value = "";
  const value = (storeName.value || "").trim();
  if (value.length > 140) {
    storeNameError.value = "店铺名称不能超过 140 个字符";
    return;
  }
  storeNameSaving.value = true;
  try {
    await accountApi.updateProfile({ store_name: value });
    storeNameSuccess.value = "店铺名称已更新";
    await refreshProfile();
  } catch (err) {
    storeNameError.value = err?.response?.data?.detail || "更新店铺名称失败";
  } finally {
    storeNameSaving.value = false;
  }
};
</script>

<template>
  <div class="profile-grid">
    <GlassCard title="个人资料" subtitle="同步自账号系统">
      <div class="avatar-panel">
        <div class="avatar-wrapper">
          <img v-if="avatarPreview" :src="avatarPreview" alt="头像" />
          <div v-else class="avatar-placeholder">{{ auth.user?.username?.slice(0, 1)?.toUpperCase() }}</div>
        </div>
        <div class="avatar-actions">
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileChange" />
          <button class="btn-primary" type="button" @click="triggerUpload" :disabled="uploading">上传头像</button>
          <button class="btn-outline" type="button" @click="clearAvatar" :disabled="uploading">清空头像</button>
        </div>
        <p v-if="uploadError" class="error">{{ uploadError }}</p>
        <p v-if="uploadSuccess" class="success">{{ uploadSuccess }}</p>
      </div>
      <ul class="profile-list">
        <li><strong>用户名</strong><span>{{ auth.user?.username }}</span></li>
        <li><strong>角色</strong><span>{{ auth.user?.role }}</span></li>
        <li><strong>邮箱</strong><span>{{ auth.user?.email || "未绑定" }}</span></li>
        <li v-if="auth.user?.role === 'MERCHANT'">
          <strong>店铺名称</strong><span>{{ auth.user?.store_name || "使用用户名" }}</span>
        </li>
      </ul>
      <div v-if="auth.user?.role === 'MERCHANT'" class="store-name-form">
        <label>
          店铺名称
          <input v-model="storeName" maxlength="140" placeholder="给店铺起个名字" />
        </label>
        <div class="form-actions">
          <button class="btn-primary" type="button" @click="saveStoreName" :disabled="storeNameSaving">
            {{ storeNameSaving ? "保存中..." : "保存店铺名称" }}
          </button>
          <p v-if="storeNameError" class="error">{{ storeNameError }}</p>
          <p v-else-if="storeNameSuccess" class="success">{{ storeNameSuccess }}</p>
        </div>
      </div>
    </GlassCard>

    <GlassCard v-if="isConsumer" title="钱包" subtitle="交易挡位 + 余额">
      <p v-if="walletLoading" class="hint">加载中...</p>
      <p v-else-if="walletError" class="error">{{ walletError }}</p>
      <div v-else-if="wallet" class="wallet-panel">
        <div>
          <p class="eyebrow">余额</p>
          <h2>¥{{ wallet.balance.toFixed(2) }}</h2>
          <p class="hint" v-if="wallet.enable_tiers">
            低档 ≤ ¥{{ wallet.low_tier_limit }} 自动扣款；高档需审核后再扣款
          </p>
          <p class="hint" v-else>挡位关闭：按余额直接扣款</p>
        </div>
        <div class="wallet-tags">
          <span class="pill">{{ wallet.tier === "LOW" ? "低档" : "高档" }}</span>
          <span class="pill" :class="{ danger: wallet.pending_review }">
            {{ wallet.pending_review ? "有待审核交易" : "可用" }}
          </span>
          <span class="pill" v-if="wallet.enable_tiers === false">挡位已关闭</span>
        </div>
        <div class="recharge">
          <input v-model="redeemCode" placeholder="输入兑换码" />
          <button class="btn-outline" type="button" :disabled="redeeming" @click="redeem">
            {{ redeeming ? "兑换中..." : "兑换余额" }}
          </button>
          <p v-if="redeemError" class="error">{{ redeemError }}</p>
          <p v-if="redeemMsg" class="success">{{ redeemMsg }}</p>
        </div>
      </div>
    </GlassCard>

    <GlassCard v-if="isConsumer" title="收货地址（宿舍）" subtitle="用于下单结算">
      <p v-if="addressLoading" class="hint">加载地址...</p>
      <p v-if="addressError" class="error">{{ addressError }}</p>
      <div class="address-list" v-if="addresses.length">
        <article v-for="addr in addresses" :key="addr.id" class="address-card">
          <div class="address-head">
            <div>
              <strong>{{ addr.receiver_name }}</strong>
              <span class="muted">{{ addr.phone }}</span>
            </div>
            <span v-if="addr.is_default" class="pill">默认</span>
          </div>
          <p class="muted">
            宿舍：{{ addr.dorm_building || "未填楼栋" }} {{ addr.dorm_room || "" }} {{ addr.detail }}
          </p>
          <button class="link" type="button" @click="removeAddress(addr)">删除</button>
        </article>
      </div>
      <form class="address-form" @submit.prevent="submitAddress">
        <div class="row">
          <label>收件人 <input v-model="addressForm.receiver_name" required /></label>
          <label>手机号 <input v-model="addressForm.phone" required /></label>
        </div>
        <div class="row">
          <label>宿舍楼栋 <input v-model="addressForm.dorm_building" placeholder="XX楼/园区" /></label>
          <label>寝室/房间 <input v-model="addressForm.dorm_room" placeholder="xxx室" /></label>
        </div>
        <label>详细信息 <input v-model="addressForm.detail" placeholder="可补充楼层/备注" /></label>
        <label class="checkbox">
          <input type="checkbox" v-model="addressForm.is_default" />
          设为默认地址
        </label>
        <p v-if="addressError" class="error">{{ addressError }}</p>
        <p v-else-if="addressSuccess" class="success">{{ addressSuccess }}</p>
        <button class="btn-primary" type="submit">保存地址</button>
      </form>
    </GlassCard>
  </div>
</template>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.profile-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-list li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed rgba(15, 45, 31, 0.12);
  padding-bottom: 8px;
}

.profile-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.store-name-form {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

.store-name-form input {
  width: 100%;
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(15, 45, 31, 0.12);
}

.form-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.avatar-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.avatar-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(15, 45, 31, 0.15);
  display: grid;
  place-items: center;
  background: rgba(15, 45, 31, 0.05);
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 2.6rem;
  color: #0f2d1f;
}

.avatar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hidden {
  display: none;
}

.error {
  color: #b42318;
}

.success {
  color: #117a42;
}

strong {
  color: #4d6359;
}

.muted {
  color: #6b7280;
}

.hint {
  color: #4d6359;
}

.wallet-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: rgba(15, 45, 31, 0.06);
  border-radius: 14px;
  padding: 14px;
  flex-wrap: wrap;
}

.wallet-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pill {
  padding: 6px 12px;
  border-radius: 999px;
  background: #0f3d2e;
  color: #fff;
  font-weight: 600;
}

.pill.danger {
  background: #b42318;
}

.recharge {
  display: grid;
  gap: 8px;
  width: 260px;
}

.recharge input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(15, 45, 31, 0.12);
}

.address-list {
  display: grid;
  gap: 10px;
  margin-bottom: 12px;
}

.address-card {
  border: 1px solid rgba(15, 45, 31, 0.12);
  border-radius: 12px;
  padding: 10px 12px;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.address-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.address-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox {
  display: flex;
  gap: 8px;
  align-items: center;
}

.link {
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
  align-self: flex-end;
}
</style>
