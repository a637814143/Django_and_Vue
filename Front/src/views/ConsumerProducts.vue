<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { storefrontApi } from "../api";
import { useCartStore } from "../store/cart";

const route = useRoute();
const cart = useCartStore();

const loading = ref(true);
const error = ref("");
const products = ref([]);
const stores = ref([]);
const categories = ref([]);
const activeCategory = ref("全部");
const activeStore = ref("全部");
const keyword = ref("");
const currentPage = ref(1);
const pageSize = 12;
const total = ref(0);

const pageCount = computed(() => Math.max(1, Math.ceil((total.value || 0) / pageSize)));

const syncFromRoute = () => {
  const q = route.query.q;
  keyword.value = typeof q === "string" ? q : "";
};

const loadFilters = async () => {
  try {
    const [storeRes, categoryRes] = await Promise.all([
      storefrontApi.stores({ page_size: 100 }),
      storefrontApi.categories({ has_products: 1 }),
    ]);
    stores.value = storeRes.results ?? storeRes;
    categories.value = categoryRes.results ?? categoryRes;
  } catch (err) {
    // filters are optional for browsing; ignore failures
  }
};

const loadProducts = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = { page: currentPage.value, page_size: pageSize };
    if (keyword.value) params.search = keyword.value;
    if (activeCategory.value !== "全部") {
      const selected = categories.value.find((c) => c.name === activeCategory.value);
      if (selected) params.category = selected.id;
    }
    if (activeStore.value !== "全部") {
      params.store = activeStore.value;
    }
    const data = await storefrontApi.products(params);
    products.value = data.results ?? data;
    total.value = data.count ?? products.value.length;
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize));
    if (currentPage.value > maxPage) {
      currentPage.value = maxPage;
    }
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载商品失败";
  } finally {
    loading.value = false;
  }
};

const changePage = (page) => {
  if (page < 1 || page > pageCount.value || page === currentPage.value) return;
  currentPage.value = page;
};

const applyKeywordSearch = () => {
  currentPage.value = 1;
  loadProducts();
};

const resetFilters = () => {
  activeCategory.value = "全部";
  activeStore.value = "全部";
  keyword.value = "";
  currentPage.value = 1;
  loadProducts();
};

const addToCart = (item) => {
  cart.add(item);
};

watch(
  () => route.query.q,
  () => {
    syncFromRoute();
    currentPage.value = 1;
    loadProducts();
  },
  { immediate: true },
);

watch([activeCategory, activeStore], () => {
  currentPage.value = 1;
  loadProducts();
});

watch(currentPage, () => {
  loadProducts();
});

onMounted(() => {
  syncFromRoute();
  loadFilters();
});
</script>

<template>
  <div class="consumer-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Consumer Picks</p>
        <h1>选好物 · 全部店铺的商品一览</h1>
        <p class="lede">跨店铺收录所有上架商品，支持按店铺、分类和关键字筛选。</p>
        <p class="meta">每页 {{ pageSize }} 条 · 当前共 {{ total }} 件商品</p>
      </div>
      <div class="hero-actions">
        <button class="soft" @click="resetFilters">重置筛选</button>
      </div>
    </section>

    <div class="content-grid">
      <aside class="panel filter-panel">
        <div class="panel-head">
          <h3>筛选</h3>
          <small>分类 · 店铺 · 关键字</small>
        </div>
        <div class="block">
          <label class="label">分类</label>
          <div class="chips">
            <button
              :class="['chip', { active: activeCategory === '全部' }]"
              @click="activeCategory = '全部'"
            >
              全部
            </button>
            <button
              v-for="category in categories"
              :key="category.id"
              :class="['chip', { active: activeCategory === category.name }]"
              @click="activeCategory = category.name"
            >
              {{ category.name }}
            </button>
          </div>
        </div>
        <div class="block">
          <label class="label">店铺</label>
          <div class="chips">
            <button
              :class="['chip', { active: activeStore === '全部' }]"
              @click="activeStore = '全部'"
            >
              全部
            </button>
            <button
              v-for="store in stores"
              :key="store.id"
              :class="['chip', { active: String(activeStore) === String(store.id) }]"
              @click="activeStore = store.id"
            >
              {{ store.name }}
            </button>
          </div>
        </div>
        <div class="block">
          <label class="label">关键字</label>
          <input
            class="search"
            type="search"
            v-model.trim="keyword"
            placeholder="搜索商品名称 / 描述 / 店铺"
            @keyup.enter="applyKeywordSearch"
          />
        </div>
        <div class="block summary">
          <p>当前筛选</p>
          <strong>{{ activeCategory }}</strong>
          <span v-if="activeStore !== '全部'"> · 店铺 {{ stores.find((s) => String(s.id) === String(activeStore))?.name || activeStore }}</span>
          <span v-if="keyword"> · “{{ keyword }}”</span>
        </div>
      </aside>

      <section class="panel list-panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">结果</p>
            <h3>商品列表</h3>
          </div>
          <div class="page-inline" v-if="total">
            <button class="soft" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
              上一页
            </button>
            <span class="page-info">第 {{ currentPage }} / {{ pageCount }} 页</span>
            <button class="soft" @click="changePage(currentPage + 1)" :disabled="currentPage === pageCount">
              下一页
            </button>
          </div>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <div v-if="loading" class="skeleton-grid">
          <div class="skeleton-card" v-for="n in 6" :key="n"></div>
        </div>
        <div v-else class="product-grid">
          <article v-for="item in products" :key="item.id || item.title" class="product-card">
            <div
              class="cover"
              :style="{
                backgroundImage: item.hero_image ? `url(${item.hero_image})` : 'linear-gradient(135deg, #e2e8f0, #cbd5e1)'
              }"
            ></div>
            <header>
              <span class="pill-dark">{{ item.category?.name || "未分类" }}</span>
              <strong>¥{{ Number(item.price ?? 0).toFixed(2) }}</strong>
            </header>
            <h3>{{ item.title }}</h3>
            <p class="desc">{{ item.description || "暂无描述" }}</p>
            <footer>
              <div class="meta">
                <span>库存 {{ item.inventory ?? 0 }}</span>
                <span v-if="item.store?.name">店铺 {{ item.store.name }}</span>
              </div>
              <button class="soft" type="button" @click="addToCart(item)">加入购物车</button>
            </footer>
          </article>
          <p v-if="!products.length && !loading && !error" class="empty">暂无符合条件的商品。</p>
        </div>

        <div class="pagination" v-if="total">
          <button class="btn" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} / {{ pageCount }} 页</span>
          <button class="btn" @click="changePage(currentPage + 1)" :disabled="currentPage === pageCount">
            下一页
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.consumer-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: none;
}

.hero h1 {
  margin: 2px 0;
  font-size: 1.35rem;
  color: #111827;
}

.hero .lede {
  margin: 0;
  color: #475569;
}

.meta {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.soft {
  border: 1px solid #111827;
  background: #111827;
  color: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.1s ease;
}

.soft:active {
  transform: translateY(1px);
}

.content-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
}

.panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.filter-panel .block {
  margin-top: 14px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.panel-head h3 {
  margin: 0;
  font-size: 1.1rem;
}

.panel-head small {
  color: #94a3b8;
}

.label {
  display: block;
  margin-bottom: 6px;
  color: #475569;
  font-weight: 600;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  padding: 6px 12px;
  background: #f8fafc;
  cursor: pointer;
  color: #111827;
}

.chip.active {
  background: #111827;
  color: #f8fafc;
  border-color: #111827;
}

.search {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}

.summary {
  background: #f8fafc;
  padding: 10px 12px;
  border-radius: 10px;
  color: #334155;
}

.list-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
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
  min-height: 180px;
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

.desc {
  color: #475569;
  margin: 0;
}

.product-card footer {
  gap: 8px;
}

.product-card footer .meta {
  display: flex;
  gap: 10px;
}

.pill-dark {
  padding: 4px 10px;
  border-radius: 999px;
  background: #111827;
  color: #f8fafc;
  font-size: 0.85rem;
}

.error {
  color: #b91c1c;
}

.empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #6b7280;
}

.pagination {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
}

.page-info {
  color: #0f172a;
}

@media (max-width: 960px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
