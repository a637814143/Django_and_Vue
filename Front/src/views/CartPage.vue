<script setup>
import { computed, onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
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
  <div class="cart-layout">
    <GlassCard title="购物车" subtitle="已选商品">
      <div v-if="items.length" class="cart-table">
        <div class="cart-row cart-row--head">
          <span>商品</span>
          <span>数量</span>
          <span>金额</span>
        </div>
        <div v-for="item in items" :key="item.id || item.title" class="cart-row">
          <div class="item-info">
            <img v-if="item.hero_image" :src="item.hero_image" alt="商品图" />
            <div>
              <strong>{{ item.title }}</strong>
              <p class="muted" v-if="item.store_name">店铺：{{ item.store_name }}</p>
            </div>
          </div>
          <div class="qty">
            <button class="ghost" type="button" @click="dec(item)" :disabled="item.qty <= 1">-</button>
            <span>{{ item.qty }}</span>
            <button class="ghost" type="button" @click="inc(item)">+</button>
          </div>
          <div class="price">
            <strong>¥{{ (item.price * item.qty).toFixed(2) }}</strong>
            <button class="link" type="button" @click="removeItem(item.id)">移除</button>
          </div>
        </div>
      </div>
      <p v-else class="empty">购物车为空，去商品页挑选吧。</p>
    </GlassCard>

    <GlassCard title="结算信息" subtitle="暂未接入支付">
      <ul class="summary">
        <li><span>商品合计</span><strong>¥{{ total.toFixed(2) }}</strong></li>
        <li><span>配送</span><strong>¥0.00</strong></li>
        <li><span>折扣</span><strong>- ¥0.00</strong></li>
      </ul>
      <div class="total">
        <span>支付金额</span>
        <strong>¥{{ total.toFixed(2) }}</strong>
      </div>
      <button class="btn-primary" type="button" :disabled="!items.length || checkingOut" @click="showAddressPicker = true">
        {{ checkingOut ? "提交中..." : "去结算" }}
      </button>
      <p v-if="checkoutError" class="error">{{ checkoutError }}</p>
      <p v-if="checkoutMsg" class="success">{{ checkoutMsg }}</p>
    </GlassCard>

    <div v-if="showAddressPicker" class="modal">
      <div class="modal-content">
        <header>
          <h3>选择收货地址</h3>
          <button class="link" type="button" @click="showAddressPicker = false">关闭</button>
        </header>
        <p v-if="addressError" class="error">{{ addressError }}</p>
        <div v-if="!addresses.length" class="empty">暂无地址，请先在个人中心添加。</div>
        <div class="address-options">
          <label v-for="addr in addresses" :key="addr.id" class="address-option">
            <input type="radio" :value="addr.id" v-model="selectedAddressId" />
            <div>
              <strong>{{ addr.receiver_name }} {{ addr.phone }}</strong>
              <p class="muted">宿舍：{{ addr.dorm_building || "" }} {{ addr.dorm_room || "" }} {{ addr.detail }}</p>
              <span v-if="addr.is_default" class="pill">默认</span>
            </div>
          </label>
        </div>
        <div class="actions">
          <button class="btn-outline" type="button" @click="showAddressPicker = false">取消</button>
          <button class="btn-primary" type="button" :disabled="!selectedAddressId || checkingOut" @click="checkout">
            确认下单
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

@media (max-width: 960px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
}

.cart-table {
  display: flex;
  flex-direction: column;
}

.cart-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  padding: 16px 0;
  border-bottom: 1px solid rgba(15, 45, 31, 0.08);
}

.item-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.item-info img {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(15, 45, 31, 0.1);
}

.muted {
  color: #6b7280;
  margin: 4px 0 0;
}

.qty {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.price {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.cart-row--head {
  font-weight: 600;
  color: #4d6359;
}

.summary {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary li {
  display: flex;
  justify-content: space-between;
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 1.2rem;
}

.empty {
  color: #6b7280;
  padding: 12px 0;
}

.ghost {
  border: 1px solid rgba(15, 45, 31, 0.18);
  background: white;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
}

.link {
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
}

.btn-primary[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  width: min(520px, 100%);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-content header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.address-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.address-option {
  border: 1px solid rgba(15, 45, 31, 0.15);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.muted {
  color: #6b7280;
}

.pill {
  padding: 4px 10px;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
  font-size: 0.8rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-outline {
  border: 1px solid #0f172a;
  background: white;
  color: #0f172a;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
}
</style>
