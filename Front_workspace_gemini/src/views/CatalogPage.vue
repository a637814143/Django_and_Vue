<script setup>
import { computed, onMounted, reactive, ref } from "vue";
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
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>商品清单</v-card-title>
          <v-card-subtitle>商家视角</v-card-subtitle>
          <v-divider></v-divider>
          <v-card-text>
            <v-progress-circular v-if="loading" indeterminate color="primary"></v-progress-circular>
            <p v-else-if="!products.length">暂无商品，请在右侧表单发布。</p>
            <v-row v-else>
              <v-col v-for="product in products" :key="product.id" cols="12" sm="6" lg="4">
                <v-card>
                  <v-img
                    :src="product.hero_image"
                    height="200px"
                    cover
                  >
                    <template v-slot:error>
                      <v-img
                        src="https://via.placeholder.com/300x200.png?text=No+Image"
                        height="200px"
                        cover
                      ></v-img>
                    </template>
                  </v-img>
                  <v-card-title>{{ product.title }}</v-card-title>
                  <v-card-subtitle>{{ product.category?.name || "未分类" }}</v-card-subtitle>
                  <v-card-text>{{ product.description || "暂无描述" }}</v-card-text>
                  <v-divider></v-divider>
                  <v-card-actions>
                    <v-chip>库存 {{ product.inventory }}</v-chip>
                    <v-spacer></v-spacer>
                    <v-chip color="primary">¥{{ product.price }}</v-chip>
                    <v-btn size="small" variant="text" prepend-icon="mdi-pencil" @click="startEdit(product)">
                        编辑
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>{{ editingId ? '编辑商品' : '发布新品' }}</v-card-title>
              <v-card-subtitle>可修改商品属性</v-card-subtitle>
              <v-card-text>
                <v-form @submit.prevent="submitProduct">
                  <v-text-field v-model="form.title" label="名称" required placeholder="青柠手账套装..."></v-text-field>
                  <v-textarea v-model="form.description" label="描述" rows="3"></v-textarea>
                  <v-file-input @change="handleFile" label="封面图" accept="image/*"></v-file-input>
                   <v-text-field v-model="form.hero_image" label="或粘贴图片链接" placeholder="data:image/png;base64,..."></v-text-field>
                  <v-img v-if="heroPreview" :src="heroPreview" height="150" class="mb-4"></v-img>
                  <v-select
                    v-model="form.category_id"
                    :items="categories"
                    item-title="name"
                    item-value="id"
                    label="所属分类"
                    :disabled="!categories.length"
                  ></v-select>
                  <p v-if="!categories.length">暂无分类，请先在下方创建。</p>
                  <v-row>
                    <v-col>
                      <v-text-field v-model.number="form.price" label="价格" type="number" min="0" step="0.01"></v-text-field>
                    </v-col>
                    <v-col>
                      <v-text-field v-model.number="form.inventory" label="库存" type="number" min="0"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-alert v-if="creationError" type="error">{{ creationError }}</v-alert>
                  <v-card-actions>
                    <v-btn v-if="editingId" text @click="resetForm">取消编辑</v-btn>
                    <v-spacer></v-spacer>
                    <v-btn type="submit" color="primary" :disabled="!categories.length">
                      {{ editingId ? "保存修改" : "创建商品" }}
                    </v-btn>
                  </v-card-actions>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12">
            <v-card>
              <v-card-title>分类管理</v-card-title>
               <v-card-subtitle>管理员/商家可维护</v-card-subtitle>
              <v-card-text>
                <v-list>
                  <v-list-item v-if="!categories.length">
                    <v-list-item-content>
                      <v-list-item-title class="text-center">还没有分类，创建后即可在发布商品时选择。</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item v-for="cat in categories" :key="cat.id">
                    <v-list-item-content>
                      <v-list-item-title>{{ cat.name }}</v-list-item-title>
                      <v-list-item-subtitle>{{ cat.description || "暂无描述" }}</v-list-item-subtitle>
                    </v-list-item-content>
                     <v-list-item-action>
                      <small>由 {{ cat.created_by || "系统" }}</small>
                    </v-list-item-action>
                  </v-list-item>
                </v-list>
                <v-form @submit.prevent="createCategory" class="mt-4">
                  <v-text-field v-model="categoryForm.name" label="分类名称" placeholder="校园文创衍生"></v-text-field>
                  <v-textarea v-model="categoryForm.description" label="描述" rows="2" placeholder="展示给商家/消费者"></v-textarea>
                  <v-alert v-if="categoryError" type="error">{{ categoryError }}</v-alert>
                  <v-alert v-if="categorySuccess" type="success">{{ categorySuccess }}</v-alert>
                  <v-btn type="submit" color="secondary" :loading="categorySubmitting">
                    {{ categorySubmitting ? "创建中..." : "新增分类" }}
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>
