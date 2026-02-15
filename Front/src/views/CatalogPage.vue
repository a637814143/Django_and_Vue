<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { catalogApi } from "../api";

const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const creationError = ref("");
const categoryError = ref("");
const categorySuccess = ref("");
const categorySubmitting = ref(false);
const editingId = ref(null);

const form = reactive({
  title: "",
  description: "",
  price: 0,
  inventory: 0,
  category_id: null,
  hero_image: "",
});

const categoryForm = reactive({
  name: "",
  description: "",
});

const heroPreview = computed(() => form.hero_image || "");

const ensureSelectedCategory = () => {
  if (!categories.value.length) {
    form.category_id = null;
    return;
  }
  const exists = categories.value.some((cat) => cat.id === form.category_id);
  if (!exists) {
    form.category_id = categories.value[0].id;
  }
};

const applyCategories = (payload) => {
  categories.value = payload.results ?? payload;
  ensureSelectedCategory();
};

const refreshCategories = async () => {
  const categoryRes = await catalogApi.categories();
  applyCategories(categoryRes);
};

const loadCatalog = async () => {
  loading.value = true;
  try {
    const [productRes, categoryRes] = await Promise.all([catalogApi.products(), catalogApi.categories()]);
    products.value = productRes.results ?? productRes;
    applyCategories(categoryRes);
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    title: "",
    description: "",
    price: 0,
    inventory: 0,
    category_id: categories.value[0]?.id || null,
    hero_image: "",
  });
  creationError.value = "";
};

const startEdit = (product) => {
  editingId.value = product.id;
  Object.assign(form, {
    title: product.title,
    description: product.description,
    price: Number(product.price || 0),
    inventory: Number(product.inventory || 0),
    category_id: product.category?.id || product.category_id || categories.value[0]?.id || null,
    hero_image: product.hero_image || "",
  });
  creationError.value = "";
};

const handleFile = (event) => {
  const [file] = event.target.files || [];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    form.hero_image = e.target?.result || "";
  };
  reader.readAsDataURL(file);
};

const submitProduct = async () => {
  creationError.value = "";
  if (!form.category_id) {
    creationError.value = "请先创建分类";
    return;
  }
  const payload = {
    title: form.title,
    description: form.description,
    price: form.price,
    inventory: form.inventory,
    category_id: form.category_id,
    hero_image: form.hero_image,
  };
  try {
    if (editingId.value) {
      await catalogApi.updateProduct(editingId.value, payload);
    } else {
      await catalogApi.createProduct(payload);
    }
    await loadCatalog();
    resetForm();
  } catch (err) {
    creationError.value =
      err?.response?.data?.title?.[0] ||
      err?.response?.data?.category_id?.[0] ||
      err?.response?.data?.detail ||
      "保存商品失败";
  }
};

const createCategory = async () => {
  categoryError.value = "";
  categorySuccess.value = "";
  if (!categoryForm.name.trim()) {
    categoryError.value = "请填写分类名称";
    return;
  }
  categorySubmitting.value = true;
  try {
    await catalogApi.createCategory({
      name: categoryForm.name.trim(),
      description: categoryForm.description.trim(),
    });
    Object.assign(categoryForm, { name: "", description: "" });
    categorySuccess.value = "分类已创建";
    await refreshCategories();
  } catch (err) {
    categoryError.value =
      err?.response?.data?.name?.[0] ||
      err?.response?.data?.detail ||
      "分类创建失败";
  } finally {
    categorySubmitting.value = false;
  }
};

onMounted(loadCatalog);
</script>

<template>
  <div class="grid">
    <GlassCard title="商品清单" subtitle="商家视角">
      <div v-if="loading">加载中...</div>
      <div v-else-if="!products.length" class="empty-state">暂无商品，请在右侧表单发布。</div>
      <div v-else class="catalog-grid">
        <article v-for="product in products" :key="product.id" class="product-tile">
          <div
            class="tile-cover"
            :style="{
              backgroundImage: product.hero_image
                ? `url(${product.hero_image})`
                : 'linear-gradient(135deg, #e2e8f0, #cbd5e1)'
            }"
          ></div>
          <p class="eyebrow">{{ product.category?.name || "未分类" }}</p>
          <h3>{{ product.title }}</h3>
          <p>{{ product.description || "暂无描述" }}</p>
          <div class="meta">
            <span>库存 {{ product.inventory }}</span>
            <strong>¥{{ product.price }}</strong>
          </div>
          <button class="btn-outline" type="button" @click="startEdit(product)">编辑</button>
        </article>
      </div>
    </GlassCard>

    <div class="side-stack">
      <GlassCard :title="editingId ? '编辑商品' : '发布新品'" subtitle="可修改商品属性">
        <form class="form" @submit.prevent="submitProduct">
          <label>名称 <input v-model="form.title" required placeholder="青柠手账套装..." /></label>
          <label>描述 <textarea v-model="form.description" rows="3"></textarea></label>
          <label class="cover-field">
            <span>封面图（上传或粘贴 data:base64）</span>
            <input type="file" accept="image/*" @change="handleFile" />
            <input v-model="form.hero_image" placeholder="data:image/png;base64,..." />
          </label>
          <div v-if="heroPreview" class="preview">
            <span class="eyebrow">预览</span>
            <div class="tile-cover" :style="{ backgroundImage: `url(${heroPreview})` }"></div>
          </div>
          <label
            >所属分类
            <select v-model="form.category_id" :disabled="!categories.length">
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </label>
          <p v-if="!categories.length" class="helper">暂无分类，请先在下方创建。</p>
          <div class="row">
            <label>价格 <input v-model.number="form.price" type="number" min="0" step="0.01" /></label>
            <label>库存 <input v-model.number="form.inventory" type="number" min="0" /></label>
          </div>
          <p v-if="creationError" class="error">{{ creationError }}</p>
          <div class="actions">
            <button class="btn-outline" type="button" v-if="editingId" @click="resetForm">取消编辑</button>
            <button class="btn-primary" type="submit" :disabled="!categories.length">
              {{ editingId ? "保存修改" : "创建商品" }}
            </button>
          </div>
        </form>
      </GlassCard>

      <GlassCard title="分类管理" subtitle="管理员/商家可维护">
        <div class="category-panel">
          <ul class="category-list">
            <li v-if="!categories.length" class="category-empty">还没有分类，创建后即可在发布商品时选择。</li>
            <li v-for="cat in categories" :key="cat.id" class="category-item">
              <div>
                <strong>{{ cat.name }}</strong>
                <p>{{ cat.description || "暂无描述" }}</p>
              </div>
              <small class="category-meta">由 {{ cat.created_by || "系统" }}</small>
            </li>
          </ul>
          <form class="category-form" @submit.prevent="createCategory">
            <label>分类名称 <input v-model="categoryForm.name" placeholder="校园文创衍生" /></label>
            <label>描述 <textarea v-model="categoryForm.description" rows="2" placeholder="展示给商家/消费者"></textarea></label>
            <p v-if="categoryError" class="error">{{ categoryError }}</p>
            <p v-else-if="categorySuccess" class="success">{{ categorySuccess }}</p>
            <button class="btn-outline" type="submit" :disabled="categorySubmitting">
              {{ categorySubmitting ? "创建中..." : "新增分类" }}
            </button>
          </form>
        </div>
      </GlassCard>
    </div>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

.side-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.product-tile {
  border-radius: 16px;
  padding: 14px;
  border: 1px solid rgba(15, 45, 31, 0.08);
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tile-cover {
  width: 100%;
  height: 140px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  border: 1px solid #e2e8f0;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #5c6f63;
  margin: 0;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.empty-state {
  padding: 24px;
  text-align: center;
  color: #6b7280;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.cover-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cover-field input[type="file"] {
  padding: 6px 0;
}

.helper {
  font-size: 0.8rem;
  color: #6b7f73;
  margin-top: -6px;
}

.category-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  border-radius: 18px;
  border: 1px solid rgba(15, 45, 31, 0.08);
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.category-item p {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: #4c675b;
}

.category-item strong {
  font-size: 0.95rem;
}

.category-meta {
  font-size: 0.75rem;
  color: #82a091;
}

.category-empty {
  text-align: center;
  color: #6b7f73;
  padding: 12px;
  border-radius: 18px;
  border: 1px dashed rgba(15, 45, 31, 0.2);
}

.category-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error {
  color: #b42318;
}

.success {
  color: #117a42;
}

.preview {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form button[disabled],
.category-form button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
