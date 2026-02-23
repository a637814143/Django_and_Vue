<script setup>
import { computed, onMounted, ref } from "vue";
import { useCartStore } from "../store/cart";
import { orderApi, addressApi } from "../api";

const cart = useCartStore();
const items = computed(() => cart.items);
const total = computed(() => cart.total);

const removeItem = (id) => cart.remove(id);
const inc = (item) => cart.setQty(item.id, item.qty + 1);
const dec = (item) => cart.setQty(item.id, item.qty - 1);

const addresses = ref([]);
const addressError = ref("");
const showAddressPicker = ref(false);
const selectedAddressId = ref(null);
const checkoutMsg = ref("");
const checkoutError = ref("");
const checkingOut = ref(false);

const loadAddresses = async () => {
  try {
    const res = await addressApi.list();
    addresses.value = res.results ?? res;
    if (!selectedAddressId.value && addresses.value.length) {
      const defaultAddr = addresses.value.find((a) => a.is_default);
      selectedAddressId.value = (defaultAddr || addresses.value[0]).id;
    }
  } catch (err) {
    addressError.value = err?.response?.data?.detail || "地址加载失败";
  }
};

const formatAddress = (addr) =>
  `${addr.receiver_name} ${addr.phone} | 宿舍：${addr.dorm_building || ""} ${addr.dorm_room || ""} ${addr.detail || ""}`.trim();

const checkout = async () => {
  checkoutMsg.value = "";
  checkoutError.value = "";
  if (!items.value.length) {
    checkoutError.value = "购物车为空";
    return;
  }
  const addr = addresses.value.find((a) => a.id === selectedAddressId.value);
  if (!addr) {
    checkoutError.value = "请选择收货地址";
    showAddressPicker.value = true;
    return;
  }
  checkingOut.value = true;
  try {
    const payload = {
      shipping_address: formatAddress(addr),
      items: items.value.map((i) => ({
        product_id: i.id,
        quantity: i.qty,
        custom_details: "",
      })),
    };
    await orderApi.create(payload);
    checkoutMsg.value = "下单成功";
    cart.clear();
  } catch (err) {
    checkoutError.value = err?.response?.data?.detail || "下单失败";
  } finally {
    checkingOut.value = false;
    showAddressPicker.value = false;
  }
};

onMounted(() => {
  loadAddresses();
});
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>购物车</v-card-title>
          <v-card-subtitle>已选商品</v-card-subtitle>
          <v-divider></v-divider>
          <v-list v-if="items.length">
            <v-list-item v-for="item in items" :key="item.id || item.title">
              <v-row align="center">
                <v-col cols="4" sm="3">
                  <v-img :src="item.hero_image" aspect-ratio="1" class="rounded"></v-img>
                </v-col>
                <v-col cols="8" sm="9">
                  <v-list-item-content>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                    <v-list-item-subtitle v-if="item.store_name">店铺：{{ item.store_name }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-col>
              </v-row>
               <v-row align="center" justify="end">
                <v-col cols="auto">
                  <v-btn size="small" variant="outlined" prepend-icon="mdi-minus" @click="dec(item)" :disabled="item.qty <= 1">
                    减少
                  </v-btn>
                  <span class="mx-2">{{ item.qty }}</span>
                  <v-btn size="small" variant="outlined" prepend-icon="mdi-plus" @click="inc(item)">
                    增加
                  </v-btn>
                </v-col>
                <v-col cols="auto">
                  <p class="text-h6">¥{{ (item.price * item.qty).toFixed(2) }}</p>
                </v-col>
                <v-col cols="auto">
                   <v-btn size="small" variant="text" color="error" prepend-icon="mdi-delete" @click="removeItem(item.id)">
                    移除
                  </v-btn>
                </v-col>
              </v-row>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-center">
            购物车为空，去商品页挑选吧。
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>结算信息</v-card-title>
          <v-card-subtitle>暂未接入支付</v-card-subtitle>
          <v-divider></v-divider>
          <v-list>
            <v-list-item>
              <v-list-item-content>商品合计</v-list-item-content>
              <v-list-item-action>¥{{ total.toFixed(2) }}</v-list-item-action>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>配送</v-list-item-content>
              <v-list-item-action>¥0.00</v-list-item-action>
            </v-list-item>
             <v-list-item>
              <v-list-item-content>折扣</v-list-item-content>
              <v-list-item-action>- ¥0.00</v-list-item-action>
            </v-list-item>
          </v-list>
          <v-divider></v-divider>
          <v-card-text class="text-h6 d-flex justify-space-between">
            <span>支付金额</span>
            <strong>¥{{ total.toFixed(2) }}</strong>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" block :disabled="!items.length || checkingOut" @click="showAddressPicker = true">
              {{ checkingOut ? "提交中..." : "去结算" }}
            </v-btn>
          </v-card-actions>
          <v-alert v-if="checkoutError" type="error" class="mt-4">{{ checkoutError }}</v-alert>
          <v-alert v-if="checkoutMsg" type="success" class="mt-4">{{ checkoutMsg }}</v-alert>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showAddressPicker" max-width="600">
      <v-card>
        <v-card-title class="d-flex justify-space-between">
          选择收货地址
          <v-btn variant="text" prepend-icon="mdi-close" @click="showAddressPicker = false">
            关闭
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-alert v-if="addressError" type="error">{{ addressError }}</v-alert>
          <p v-if="!addresses.length">暂无地址，请先在个人中心添加。</p>
          <div v-else class="d-flex flex-column ga-3">
            <v-card
              v-for="addr in addresses"
              :key="addr.id"
              :elevation="selectedAddressId === addr.id ? 6 : 1"
              :class="['address-card', selectedAddressId === addr.id ? 'address-card--active' : '']"
              role="button"
              tabindex="0"
              @click="selectedAddressId = addr.id"
            >
              <v-card-text class="d-flex align-center justify-space-between">
                <div>
                  <div class="d-flex align-center ga-2">
                    <strong>{{ addr.receiver_name }} {{ addr.phone }}</strong>
                    <v-chip v-if="addr.is_default" size="x-small" color="primary" variant="tonal">默认</v-chip>
                  </div>
                  <div class="text-body-2 text-medium-emphasis mt-1">
                    宿舍：{{ addr.dorm_building || "" }} {{ addr.dorm_room || "" }} {{ addr.detail }}
                  </div>
                </div>
                <v-icon :color="selectedAddressId === addr.id ? 'primary' : 'grey'">
                  {{ selectedAddressId === addr.id ? 'mdi-radiobox-marked' : 'mdi-radiobox-blank' }}
                </v-icon>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showAddressPicker = false">取消</v-btn>
          <v-btn color="primary" :disabled="!selectedAddressId || checkingOut" @click="checkout">
            确认下单
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.address-card {
  cursor: pointer;
  border: 1px solid #e0e0e0;
}
.address-card--active {
  border-color: var(--v-theme-primary);
}
</style>
