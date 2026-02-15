<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storefrontApi } from "../api";

const route = useRoute();
const router = useRouter();

const stores = ref([]);
const loading = ref(false);
const error = ref("");
const keyword = ref("");
const page = ref(1);
const pageSize = 9;
const total = ref(0);

const pageCount = computed(() => Math.max(1, Math.ceil((total.value || 0) / pageSize)));

const syncFromRoute = () => {
  const q = route.query.q;
  keyword.value = typeof q === "string" ? q : "";
};

const loadStores = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = { page: page.value, page_size: pageSize };
    if (keyword.value) params.search = keyword.value;
    const data = await storefrontApi.stores(params);
    stores.value = data.results ?? data;
    total.value = data.count ?? stores.value.length;
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize));
    if (page.value > maxPage) {
      page.value = maxPage;
    }
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载店铺失败";
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
  const q = keyword.value.trim();
  const nextQuery = q ? { q } : {};
  if ((route.query.q || "") === (q || "")) {
    page.value = 1;
    loadStores();
    return;
  }
  await router.push({ name: "store", query: nextQuery });
};

const changePage = (next) => {
  if (next < 1 || next > pageCount.value || next === page.value) return;
  page.value = next;
};

const goToStore = (store) => {
  if (!store?.id) return;
  router.push({ name: "store-detail", params: { id: store.id } });
};

watch(
  () => route.query.q,
  () => {
    syncFromRoute();
    page.value = 1;
    loadStores();
  },
  { immediate: true },
);

watch(page, () => {
  loadStores();
});

onMounted(syncFromRoute);
</script>

<template>
  <div class="store-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Store Plaza</p>
        <h1>发现店铺 · 走进摊位</h1>
        <p class="lede">浏览各个店铺与摊位，点击卡片即可进入店铺详情与商品列表。</p>
      </div>
      <div class="hero-actions">
        <div class="search-box">
          <input
            type="search"
            v-model.trim="keyword"
            placeholder="输入店铺名称或简介关键字"
            @keyup.enter="handleSearch"
          />
          <button class="btn" type="button" @click="handleSearch">搜索</button>
        </div>
        <span class="pill">共 {{ total }} 家</span>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">浏览</p>
          <h3>店铺列表</h3>
        </div>
        <div class="pager" v-if="pageCount > 1">
          <button class="ghost" @click="changePage(page - 1)" :disabled="page === 1">上一页</button>
          <span class="page-info">第 {{ page }} / {{ pageCount }} 页</span>
          <button class="ghost" @click="changePage(page + 1)" :disabled="page === pageCount">下一页</button>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div v-if="loading" class="skeleton-grid">
        <div class="skeleton-card" v-for="i in 6" :key="i"></div>
      </div>

      <div v-else class="store-grid">
        <article
          v-for="store in stores"
          :key="store.id"
          class="store-card"
          @click="goToStore(store)"
        >
          <header class="card-head">
            <div class="store-meta">
              <div class="avatar">
                <span>{{ store.name?.slice(0, 1)?.toUpperCase() }}</span>
              </div>
              <div>
                <h3>{{ store.name }}</h3>
                <p class="muted">{{ store.product_count || 0 }} 件商品</p>
              </div>
            </div>
            <button class="text-link" type="button" @click.stop="goToStore(store)">
              进入店铺 →
            </button>
          </header>
          <p class="desc">{{ store.description || "这家店铺还没有写简介。" }}</p>
          <div class="preview" v-if="store.preview_products?.length">
            <span class="eyebrow">热卖</span>
            <div class="preview-list">
              <span
                v-for="item in store.preview_products"
                :key="item.id"
                class="chip"
              >
                {{ item.title }}
                <strong>¥{{ Number(item.price || 0).toFixed(2) }}</strong>
              </span>
            </div>
          </div>
        </article>
        <p v-if="!stores.length && !loading && !error" class="empty">暂无店铺，稍后再来看看。</p>
      </div>

      <div class="pagination" v-if="pageCount > 1">
        <button class="btn" @click="changePage(page - 1)" :disabled="page === 1">上一页</button>
        <span class="page-info">第 {{ page }} / {{ pageCount }} 页</span>
        <button class="btn" @click="changePage(page + 1)" :disabled="page === pageCount">下一页</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.store-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  background: linear-gradient(120deg, #ecfeff, #e0f2fe, #eef2ff);
  border: 1px solid #dbeafe;
}

.hero h1 {
  margin: 4px 0;
  color: #0f172a;
}

.hero .lede {
  margin: 0;
  color: #475569;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #2563eb;
  margin: 0;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.search-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-box input {
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 260px;
}

.pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: #0f172a;
  color: #f8fafc;
  font-weight: 600;
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

.ghost {
  border: 1px solid #e2e8f0;
  background: white;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
}

.ghost:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.store-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.store-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 180px;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.store-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.store-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #0f172a;
  color: #f8fafc;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.muted {
  color: #6b7280;
  margin: 0;
}

.desc {
  color: #475569;
  margin: 0;
  line-height: 1.5;
}

.preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border-radius: 12px;
  padding: 6px 10px;
  background: #0f172a;
  color: #f8fafc;
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.text-link {
  background: transparent;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-weight: 600;
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

.pagination {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
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
  height: 170px;
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

  .hero-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .search-box {
    width: 100%;
  }

  .search-box input {
    flex: 1;
    min-width: 0;
    width: 100%;
  }
}
</style>
