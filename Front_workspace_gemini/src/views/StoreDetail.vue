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
  <v-container fluid>
    <v-btn text @click="goBack" class="mb-4">
      <v-icon left>mdi-arrow-left</v-icon>
      返回店铺列表
    </v-btn>

    <v-card v-if="store" class="mb-4">
      <v-card-title>
        <v-avatar color="primary" class="mr-4">
          <span>{{ store?.name?.slice(0, 1)?.toUpperCase() }}</span>
        </v-avatar>
        {{ store.name }}
      </v-card-title>
      <v-card-subtitle>商品 {{ store.product_count || 0 }}</v-card-subtitle>
      <v-card-text>{{ store.description || "这家店铺暂未填写简介。" }}</v-card-text>
      <v-alert v-if="storeError" type="error">{{ storeError }}</v-alert>
    </v-card>

    <v-card>
      <v-card-title>全部商品</v-card-title>
      <v-card-subtitle>店铺商品一览</v-card-subtitle>
      <v-divider></v-divider>
      <v-card-text>
        <v-alert v-if="productError" type="error">{{ productError }}</v-alert>
        <v-row v-if="productLoading">
          <v-col v-for="i in 6" :key="i" cols="12" sm="6" md="4">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
        </v-row>
        <v-row v-else-if="products.length">
          <v-col v-for="item in products" :key="item.id" cols="12" sm="6" md="4">
            <v-card>
              <v-img :src="item.hero_image" height="200px" cover>
                 <template v-slot:error>
                    <v-img
                      src="https://via.placeholder.com/300x200.png?text=No+Image"
                      height="200px"
                      cover
                    ></v-img>
                  </template>
              </v-img>
              <v-card-title>{{ item.title }}</v-card-title>
               <v-card-subtitle>{{ item.category?.name || "未分类" }}</v-card-subtitle>
              <v-card-text>{{ item.description || "暂无描述" }}</v-card-text>
              <v-divider></v-divider>
              <v-card-actions>
                <v-chip>库存 {{ item.inventory ?? 0 }}</v-chip>
                <v-spacer></v-spacer>
                <v-chip color="primary">¥{{ Number(item.price || 0).toFixed(2) }}</v-chip>
                <v-btn size="small" variant="tonal" prepend-icon="mdi-cart-plus" @click="addToCart(item)">
                  加入购物车
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        <p v-else>暂无商品。</p>
      </v-card-text>
      <v-pagination
        v-if="productPageCount > 1"
        v-model="productPage"
        :length="productPageCount"
        @input="changePage"
      ></v-pagination>
    </v-card>
  </v-container>
</template>
