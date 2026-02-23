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
    <v-container fluid>
        <v-card class="mb-4">
            <v-card-title>发现店铺 · 走进摊位</v-card-title>
            <v-card-subtitle>浏览各个店铺与摊位，点击卡片即可进入店铺详情与商品列表。</v-card-subtitle>
            <v-card-text>
                <v-row>
                    <v-col cols="12" md="6">
                        <v-text-field
                            v-model.trim="keyword"
                            label="输入店铺名称或简介关键字"
                            @keyup.enter="handleSearch"
                            clearable
                            append-inner-icon="mdi-magnify"
                            @click:append-inner="handleSearch"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6" class="d-flex align-center">
                         <v-chip>共 {{ total }} 家</v-chip>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
        <v-row v-else>
            <v-col v-for="store in stores" :key="store.id" cols="12" md="4">
                <v-card @click="goToStore(store)">
                    <v-card-title class="d-flex align-center">
                        <v-avatar color="primary" class="mr-4">
                            <span>{{ store.name?.slice(0, 1)?.toUpperCase() }}</span>
                        </v-avatar>
                        {{ store.name }}
                    </v-card-title>
                    <v-card-subtitle>{{ store.product_count || 0 }} 件商品</v-card-subtitle>
                    <v-card-text>{{ store.description || "这家店铺还没有写简介。" }}</v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn text color="primary" @click.stop="goToStore(store)">进入店铺 <v-icon right>mdi-arrow-right</v-icon></v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
            <v-col v-if="!stores.length && !loading && !error" cols="12">
                <p>暂无店铺，稍后再来看看。</p>
            </v-col>
        </v-row>
        <v-pagination v-if="pageCount > 1" v-model="page" :length="pageCount" @input="changePage" class="mt-4"></v-pagination>
    </v-container>
</template>
