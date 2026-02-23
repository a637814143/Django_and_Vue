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
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card flat>
          <v-card-title>选好物 · 全部店铺的商品一览</v-card-title>
          <v-card-subtitle>跨店铺收录所有上架商品，支持按店铺、分类和关键字筛选。</v-card-subtitle>
           <v-card-text>每页 {{ pageSize }} 条 · 当前共 {{ total }} 件商品</v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="resetFilters">重置筛选</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>筛选</v-card-title>
          <v-card-subtitle>分类 · 店铺 · 关键字</v-card-subtitle>
          <v-card-text>
            <p>分类</p>
            <v-chip-group v-model="activeCategory" mandatory>
              <v-chip value="全部">全部</v-chip>
              <v-chip v-for="category in categories" :key="category.id" :value="category.name">
                {{ category.name }}
              </v-chip>
            </v-chip-group>
            <p class="mt-4">店铺</p>
            <v-chip-group v-model="activeStore" mandatory>
              <v-chip value="全部">全部</v-chip>
              <v-chip v-for="store in stores" :key="store.id" :value="store.id">
                {{ store.name }}
              </v-chip>
            </v-chip-group>
            <p class="mt-4">关键字</p>
            <v-text-field
              v-model.trim="keyword"
              label="搜索商品名称 / 描述 / 店铺"
              @keyup.enter="applyKeywordSearch"
              clearable
            ></v-text-field>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="9">
        <v-card>
          <v-card-title>商品列表</v-card-title>
           <v-card-subtitle>结果</v-card-subtitle>
          <v-card-text>
            <v-alert v-if="error" type="error">{{ error }}</v-alert>
            <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
            <v-row v-else>
              <v-col v-for="item in products" :key="item.id || item.title" cols="12" sm="6" md="4">
                <v-card>
                  <v-img :src="item.hero_image" height="200px" cover>
                    <template v-slot:error>
                      <v-img src="https://via.placeholder.com/300x200.png?text=No+Image" height="200px" cover></v-img>
                    </template>
                  </v-img>
                  <v-card-title>{{ item.title }}</v-card-title>
                   <v-card-subtitle>{{ item.category?.name || "未分类" }}</v-card-subtitle>
                  <v-card-text>{{ item.description || "暂无描述" }}</v-card-text>
                  <v-divider></v-divider>
                  <v-card-actions>
                     <v-chip>库存 {{ item.inventory ?? 0 }}</v-chip>
                    <v-spacer></v-spacer>
                     <v-chip color="primary">¥{{ Number(item.price ?? 0).toFixed(2) }}</v-chip>
                    <v-btn size="small" variant="tonal" prepend-icon="mdi-cart-plus" @click="addToCart(item)">
                      加入购物车
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
               <v-col v-if="!products.length && !loading && !error" cols="12">
                <p>暂无符合条件的商品。</p>
              </v-col>
            </v-row>
          </v-card-text>
          <v-pagination v-if="total > 0" v-model="currentPage" :length="pageCount" @input="changePage"></v-pagination>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
