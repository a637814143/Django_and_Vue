<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storefrontApi } from "../api";
import { useCartStore } from "../store/cart";

const route = useRoute();
const router = useRouter();
const cart = useCartStore();

const store = ref(null);
const storeLoading = ref(false);
const storeError = ref("");

const products = ref([]);
const productLoading = ref(false);
const productError = ref("");
const productPage = ref(1);
const productPageSize = 12;
const productTotal = ref(0);

const productPageCount = computed(() =>
  Math.max(1, Math.ceil((productTotal.value || 0) / productPageSize)),
);

const fetchStore = async (id) => {
  storeLoading.value = true;
  storeError.value = "";
  try {
    store.value = await storefrontApi.storeDetail(id);
  } catch (err) {
    storeError.value = err?.response?.data?.detail || "加载店铺信息失败";
  } finally {
    storeLoading.value = false;
  }
};

const fetchProducts = async (id) => {
  productLoading.value = true;
  productError.value = "";
  try {
    const data = await storefrontApi.storeProducts(id, {
      page: productPage.value,
      page_size: productPageSize,
    });
    products.value = data.results ?? data;
    productTotal.value = data.count ?? products.value.length;
    const maxPage = Math.max(1, Math.ceil((productTotal.value || 0) / productPageSize));
    if (productPage.value > maxPage) {
      productPage.value = maxPage;
    }
  } catch (err) {
    productError.value = err?.response?.data?.detail || "加载商品失败";
  } finally {
    productLoading.value = false;
  }
};

const changePage = (next) => {
  if (next < 1 || next > productPageCount.value || next === productPage.value) return;
  productPage.value = next;
};

const addToCart = (item) => {
  cart.add(item);
};

const goBack = () => {
  router.push({ name: "store" });
};

watch(
  () => route.params.id,
  (id) => {
    if (!id) return;
    productPage.value = 1;
    fetchStore(id);
    fetchProducts(id);
  },
  { immediate: true },
);

watch(productPage, () => {
  const id = route.params.id;
  if (id) fetchProducts(id);
});

onMounted(() => {
  if (!route.params.id) {
    router.replace({ name: "store" });
  }
});
</script>

<template>
  <div class="store-detail">
    <section class="hero">
      <div class="hero-left">
        <button class="ghost" type="button" @click="goBack">← 返回店铺列表</button>
        <div class="store-header">
          <div class="avatar">
            <span>{{ store?.name?.slice(0, 1)?.toUpperCase() }}</span>
          </div>
          <div>
            <p class="eyebrow">Store</p>
            <h1 v-if="store">{{ store.name }}</h1>
            <div v-if="store" class="meta">
              <span>商品 {{ store.product_count || 0 }}</span>
            </div>
          </div>
        </div>
        <p class="desc" v-if="store">{{ store.description || "这家店铺暂未填写简介。" }}</p>
        <p v-if="storeError" class="error">{{ storeError }}</p>
      </div>
      <div class="hero-right" v-if="store">
        <div class="stat-card">
          <p class="label">在售商品</p>
          <strong>{{ store.product_count || 0 }}</strong>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">全部商品</p>
          <h3>店铺商品一览</h3>
        </div>
        <div class="pager" v-if="productPageCount > 1">
          <button class="ghost" @click="changePage(productPage - 1)" :disabled="productPage === 1">
            上一页
          </button>
          <span class="page-info">第 {{ productPage }} / {{ productPageCount }} 页</span>
          <button
            class="ghost"
            @click="changePage(productPage + 1)"
            :disabled="productPage === productPageCount"
          >
            下一页
          </button>
        </div>
      </div>

      <p v-if="productError" class="error">{{ productError }}</p>

      <div v-if="productLoading" class="skeleton-grid">
        <div class="skeleton-card" v-for="i in 6" :key="i"></div>
      </div>

      <div v-else class="product-grid">
        <article v-for="item in products" :key="item.id" class="product-card">
          <div
            class="cover"
            :style="{
              backgroundImage: item.hero_image ? `url(${item.hero_image})` : 'linear-gradient(135deg, #e2e8f0, #cbd5e1)'
            }"
          ></div>
          <header>
            <span class="pill-dark">{{ item.category?.name || "未分类" }}</span>
            <strong>¥{{ Number(item.price || 0).toFixed(2) }}</strong>
          </header>
          <h3>{{ item.title }}</h3>
          <p class="desc">{{ item.description || "暂无描述" }}</p>
          <footer>
            <div class="meta">
              <span>库存 {{ item.inventory ?? 0 }}</span>
              <span v-if="item.store?.name">店铺 {{ item.store.name }}</span>
            </div>
            <button class="ghost" type="button" @click="addToCart(item)">加入购物车</button>
          </footer>
        </article>
        <p v-if="!products.length && !productLoading && !productError" class="empty">暂无商品。</p>
      </div>

      <div class="pagination" v-if="productPageCount > 1">
        <button class="btn" @click="changePage(productPage - 1)" :disabled="productPage === 1">
          上一页
        </button>
        <span class="page-info">第 {{ productPage }} / {{ productPageCount }} 页</span>
        <button
          class="btn"
          @click="changePage(productPage + 1)"
          :disabled="productPage === productPageCount"
        >
          下一页
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.store-detail {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  background: linear-gradient(120deg, #f0fdf4, #ecfeff);
  border: 1px solid #dcfce7;
  align-items: center;
}

.hero-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.store-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #0f172a;
  color: #f8fafc;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #047857;
  margin: 0;
}

.meta {
  display: flex;
  gap: 10px;
  color: #475569;
}

.desc {
  color: #475569;
  margin: 0;
}

.hero-right {
  display: flex;
  gap: 12px;
}

.stat-card {
  border-radius: 14px;
  padding: 12px 14px;
  background: #0f172a;
  color: #f8fafc;
  min-width: 120px;
}

.stat-card .label {
  margin: 0 0 6px;
  color: #cbd5e1;
}

.ghost {
  border: 1px solid #e2e8f0;
  background: white;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
}

.panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pager {
  display: flex;
  gap: 10px;
  align-items: center;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.product-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 170px;
}

.cover {
  width: 100%;
  height: 140px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  border: 1px solid #e2e8f0;
}

.product-card header,
.product-card footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #475569;
}

.product-card h3 {
  margin: 0;
  color: #0f172a;
}

.product-card footer {
  gap: 10px;
}

.product-card footer .meta {
  display: flex;
  gap: 10px;
}

.pill-dark {
  padding: 4px 10px;
  border-radius: 999px;
  background: #0f172a;
  color: #f8fafc;
  font-size: 0.85rem;
}

.pagination {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
}

.btn {
  border: 1px solid #0f172a;
  background: #0f172a;
  color: #f8fafc;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #0f172a;
}

.error {
  color: #b91c1c;
}

.empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #6b7280;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.skeleton-card {
  height: 150px;
  border-radius: 12px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 960px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-right {
    width: 100%;
  }

  .panel-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
