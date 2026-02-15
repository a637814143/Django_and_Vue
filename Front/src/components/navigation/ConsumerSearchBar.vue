<script setup>
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();

const searchType = ref("products");
const keyword = ref("");

const syncFromRoute = () => {
  const q = route.query.q;
  keyword.value = typeof q === "string" ? q : "";
  if (route.name === "store" || route.name === "store-detail") {
    searchType.value = "stores";
  } else if (route.name === "consumer-products") {
    searchType.value = "products";
  }
};

const submitSearch = () => {
  const q = keyword.value.trim();
  const targetName = searchType.value === "stores" ? "store" : "consumer-products";
  router.push({
    name: targetName,
    query: q ? { q } : {},
  });
};

const handleEnter = (event) => {
  if (event.key === "Enter") {
    submitSearch();
  }
};

onMounted(syncFromRoute);

watch(
  () => route.fullPath,
  () => {
    syncFromRoute();
  },
);
</script>

<template>
  <div class="search-bar" role="search">
    <div class="select-wrap">
      <select v-model="searchType">
        <option value="products">搜商品</option>
        <option value="stores">搜店铺</option>
      </select>
    </div>
    <input
      v-model="keyword"
      class="search-input"
      type="search"
      placeholder="输入关键词，如：清新手账"
      @keyup="handleEnter"
    />
    <button class="btn-primary" type="button" @click="submitSearch">搜索</button>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  gap: 12px;
  padding: 0 40px 16px;
}

.select-wrap {
  flex: 0 0 120px;
}

select {
  width: 100%;
  border-radius: 18px;
  border: 1px solid rgba(15, 45, 31, 0.18);
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.85);
}

.search-input {
  flex: 1;
  border-radius: 18px;
  border: 1px solid rgba(15, 45, 31, 0.18);
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.85);
  font-size: 1rem;
}

@media (max-width: 768px) {
  .search-bar {
    padding: 0 20px 16px;
    flex-direction: column;
  }

  .select-wrap {
    flex: 0 0 auto;
  }

  .btn-primary {
    width: 100%;
  }
}
</style>
