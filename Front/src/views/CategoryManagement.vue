<script setup>
import { onMounted, reactive, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { catalogApi } from "../api";

const categories = ref([]);
const loading = ref(true);
const message = ref("");
const form = reactive({
  name: "",
  description: "",
});

const loadCategories = async () => {
  loading.value = true;
  message.value = "";
  try {
    const res = await catalogApi.categories();
    categories.value = res.results ?? res;
  } catch (err) {
    message.value = err?.response?.data?.detail || "加载分类失败";
  } finally {
    loading.value = false;
  }
};

const createCategory = async () => {
  if (!form.name.trim()) {
    message.value = "请填写分类名称";
    return;
  }
  message.value = "";
  try {
    await catalogApi.createCategory({
      name: form.name.trim(),
      description: form.description.trim(),
    });
    Object.assign(form, { name: "", description: "" });
    message.value = "分类已创建";
    await loadCategories();
  } catch (err) {
    message.value = err?.response?.data?.name?.[0] || err?.response?.data?.detail || "创建失败";
  }
};

onMounted(loadCategories);
</script>

<template>
  <div class="grid">
    <GlassCard title="分类列表" subtitle="最新创建在顶部">
      <div v-if="loading">加载中...</div>
      <ul v-else class="category-list">
        <li v-for="cat in categories" :key="cat.id">
          <div>
            <strong>{{ cat.name }}</strong>
            <p>{{ cat.description || "暂无描述" }}</p>
          </div>
          <small>创建人：{{ cat.created_by || "系统" }}</small>
        </li>
        <li v-if="!categories.length" class="empty">还没有分类</li>
      </ul>
    </GlassCard>

    <GlassCard title="新增分类" subtitle="商家 / 管理员">
      <form class="form" @submit.prevent="createCategory">
        <label>名称 <input v-model="form.name" placeholder="校园衍生系列" /></label>
        <label>描述 <textarea v-model="form.description" rows="3" placeholder="对外展示内容" /></label>
        <p v-if="message" class="hint">{{ message }}</p>
        <button class="btn-primary" type="submit">提交</button>
      </form>
    </GlassCard>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-list li {
  border: 1px solid rgba(15, 45, 31, 0.12);
  border-radius: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.category-list .empty {
  justify-content: center;
  text-align: center;
}

p {
  margin: 4px 0 0;
  color: #4d6359;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hint {
  color: #0f3d2e;
}
</style>
