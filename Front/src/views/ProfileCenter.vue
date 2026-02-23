<script setup>
import { computed, onMounted, ref, watch } from "vue";
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
const showWallet = computed(() => isConsumer.value || isMerchant.value);

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

const setDefaultAddress = async (address) => {
  addressError.value = "";
  addressSuccess.value = "";
  try {
    await addressApi.update(address.id, { is_default: true });
    addressSuccess.value = "已设为默认地址";
    await loadAddresses();
  } catch (err) {
    addressError.value = err?.response?.data?.detail || "设置默认地址失败";
  }
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
    if (showWallet.value) {
      loadWallet();
    } else {
      wallet.value = null;
    }
    if (isConsumer.value) {
      loadAddresses();
    } else {
      addresses.value = [];
    }
  },
);

onMounted(() => {
  syncPreview();
  if (showWallet.value) loadWallet();
  if (isConsumer.value) loadAddresses();
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
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>个人资料</v-card-title>
          <v-card-subtitle>同步自账号系统</v-card-subtitle>
          <v-card-text class="d-flex flex-column align-center">
            <v-avatar size="120" class="mb-4">
              <v-img v-if="avatarPreview" :src="avatarPreview"></v-img>
              <span v-else class="text-h4">{{ auth.user?.username?.slice(0, 1)?.toUpperCase() }}</span>
            </v-avatar>
            <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="handleFileChange" />
            <div class="d-flex ga-2">
              <v-btn color="primary" @click="triggerUpload" :loading="uploading">上传头像</v-btn>
              <v-btn text @click="clearAvatar" :loading="uploading">清空头像</v-btn>
            </div>
            <v-alert v-if="uploadError" type="error" class="mt-4">{{ uploadError }}</v-alert>
            <v-alert v-if="uploadSuccess" type="success" class="mt-4">{{ uploadSuccess }}</v-alert>
          </v-card-text>
          <v-list>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>用户名</v-list-item-title>
                <v-list-item-subtitle>{{ auth.user?.username }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>角色</v-list-item-title>
                <v-list-item-subtitle>{{ auth.user?.role }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>邮箱</v-list-item-title>
                <v-list-item-subtitle>{{ auth.user?.email || "未绑定" }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-list-item v-if="isMerchant">
              <v-list-item-content>
                <v-list-item-title>店铺名称</v-list-item-title>
                <v-list-item-subtitle>{{ auth.user?.store_name || "使用用户名" }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <div v-if="isMerchant" class="pa-4">
            <v-text-field
              v-model="storeName"
              label="店铺名称"
              counter="140"
              placeholder="给店铺起个名字"
            ></v-text-field>
            <div class="d-flex ga-2 align-center">
              <v-btn color="primary" :loading="storeNameSaving" @click="saveStoreName">保存店铺名称</v-btn>
              <v-alert v-if="storeNameError" type="error" dense class="ma-0 pa-2">{{ storeNameError }}</v-alert>
              <v-alert v-else-if="storeNameSuccess" type="success" dense class="ma-0 pa-2">{{ storeNameSuccess }}</v-alert>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card v-if="showWallet">
          <v-card-title>钱包</v-card-title>
          <v-card-subtitle>交易挡位 + 余额</v-card-subtitle>
           <v-card-text v-if="walletLoading">加载中...</v-card-text>
          <v-alert v-else-if="walletError" type="error">{{ walletError }}</v-alert>
          <v-card-text v-else-if="wallet">
            <div class="d-flex justify-space-between align-center">
              <div>
                <p class="text-h4">¥{{ wallet.balance.toFixed(2) }}</p>
                <p v-if="wallet.enable_tiers">低档 ≤ ¥{{ wallet.low_tier_limit }} 自动扣款；高档需审核后再扣款</p>
                <p v-else>挡位关闭：按余额直接扣款</p>
              </div>
              <div>
                <v-chip class="ma-2">{{ wallet.tier === "LOW" ? "低档" : "高档" }}</v-chip>
                <v-chip class="ma-2" :color="wallet.pending_review ? 'error' : 'success'">
                  {{ wallet.pending_review ? "有待审核交易" : "可用" }}
                </v-chip>
                <v-chip v-if="wallet.enable_tiers === false">挡位已关闭</v-chip>
              </div>
            </div>
            <v-text-field v-model="redeemCode" label="输入兑换码" class="mt-4"></v-text-field>
            <v-btn color="primary" @click="redeem" :loading="redeeming">{{ redeeming ? "兑换中..." : "兑换余额" }}</v-btn>
            <v-alert v-if="redeemError" type="error" class="mt-2">{{ redeemError }}</v-alert>
            <v-alert v-if="redeemMsg" type="success" class="mt-2">{{ redeemMsg }}</v-alert>
          </v-card-text>
        </v-card>
      </v-col>
       <v-col cols="12">
        <v-card v-if="isConsumer">
          <v-card-title>收货地址（宿舍）</v-card-title>
          <v-card-subtitle>用于下单结算</v-card-subtitle>
          <v-card-text>
            <v-progress-circular v-if="addressLoading" indeterminate></v-progress-circular>
            <v-alert v-if="addressError" type="error">{{ addressError }}</v-alert>
            <v-row v-if="addresses.length">
              <v-col v-for="addr in addresses" :key="addr.id" cols="12" sm="6">
                <v-card outlined :class="{'primary--border': addr.is_default}">
                  <v-card-title>
                    {{ addr.receiver_name }}
                    <v-chip v-if="addr.is_default" small class="ml-2">默认</v-chip>
                  </v-card-title>
                  <v-card-subtitle>{{ addr.phone }}</v-card-subtitle>
                  <v-card-text>
                    宿舍：{{ addr.dorm_building || "未填楼栋" }} {{ addr.dorm_room || "" }} {{ addr.detail }}
                  </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text color="primary" @click="setDefaultAddress(addr)" :disabled="addr.is_default">设为默认</v-btn>
                <v-btn text color="error" @click="removeAddress(addr)">删除</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
            <v-form @submit.prevent="submitAddress" class="mt-4">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="addressForm.receiver_name" label="收件人" required></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="addressForm.phone" label="手机号" required></v-text-field>
                </v-col>
              </v-row>
               <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="addressForm.dorm_building" label="宿舍楼栋" placeholder="XX楼/园区"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                   <v-text-field v-model="addressForm.dorm_room" label="寝室/房间" placeholder="xxx室"></v-text-field>
                </v-col>
              </v-row>
              <v-text-field v-model="addressForm.detail" label="详细信息" placeholder="可补充楼层/备注"></v-text-field>
              <div class="default-toggle mt-2">
                <v-switch
                  v-model="addressForm.is_default"
                  label="设为默认地址"
                  color="primary"
                  inset
                  hide-details
                ></v-switch>
              </div>
              <v-alert v-if="addressError" type="error">{{ addressError }}</v-alert>
              <v-alert v-else-if="addressSuccess" type="success">{{ addressSuccess }}</v-alert>
              <v-btn type="submit" color="primary">保存地址</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.default-toggle {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px 12px;
  background: #f9f9f9;
}
</style>
