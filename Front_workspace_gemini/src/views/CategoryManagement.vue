<script setup>
import { onMounted, reactive, ref } from "vue";
import { catalogApi } from "../api";

const categories = ref([]);
const loading = ref(false);
const error = ref("");

const form = reactive({
  name: "",
  description: "",
});
const saving = ref(false);

const editDialog = ref(false);
const editTarget = ref(null);
const editForm = reactive({ name: "", description: "" });
const editError = ref("");
const deletingId = ref(null);

const headers = [
  { title: "名称", key: "name" },
  { title: "描述", key: "description" },
  { title: "创建者", key: "created_by" },
  { title: "操作", key: "actions", sortable: false },
];

const loadCategories = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await catalogApi.categories();
    categories.value = res.results ?? res ?? [];
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载分类失败";
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.name = "";
  form.description = "";
};

const createCategory = async () => {
  if (!form.name.trim()) {
    error.value = "请填写分类名称";
    return;
  }
  saving.value = true;
  error.value = "";
  try {
    await catalogApi.createCategory({
      name: form.name.trim(),
      description: form.description.trim(),
    });
    resetForm();
    await loadCategories();
  } catch (err) {
    error.value = err?.response?.data?.name?.[0] || err?.response?.data?.detail || "创建失败";
  } finally {
    saving.value = false;
  }
};

const openEdit = (cat) => {
  editTarget.value = cat;
  editForm.name = cat.name;
  editForm.description = cat.description || "";
  editError.value = "";
  editDialog.value = true;
};

const submitEdit = async () => {
  if (!editTarget.value) return;
  if (!editForm.name.trim()) {
    editError.value = "请输入分类名称";
    return;
  }
  editError.value = "";
  try {
    await catalogApi.updateCategory(editTarget.value.id, {
      name: editForm.name.trim(),
      description: editForm.description.trim(),
    });
    editDialog.value = false;
    await loadCategories();
  } catch (err) {
    editError.value = err?.response?.data?.detail || "更新失败";
  }
};

const deleteCategory = async (cat) => {
  if (!confirm(`确定删除分类「${cat.name}」吗？`)) return;
  deletingId.value = cat.id;
  error.value = "";
  try {
    await catalogApi.deleteCategory(cat.id);
    await loadCategories();
  } catch (err) {
    error.value = err?.response?.data?.detail || "删除失败";
  } finally {
    deletingId.value = null;
  }
};

onMounted(loadCategories);
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>分类列表</v-card-title>
          <v-card-subtitle>支持增删改查</v-card-subtitle>
          <v-card-text>
            <v-alert v-if="error" type="error" class="mb-2">{{ error }}</v-alert>
            <v-data-table
              :headers="headers"
              :items="categories"
              :loading="loading"
              class="elevation-1"
              no-data-text="暂无分类"
            >
              <template #item.actions="{ item }">
                <v-btn size="small" variant="text" @click="openEdit(item)">编辑</v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  color="error"
                  :loading="deletingId === item.id"
                  @click="deleteCategory(item)"
                >
                  删除
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>新增分类</v-card-title>
          <v-card-subtitle>商家 / 管理员</v-card-subtitle>
          <v-card-text>
            <v-form @submit.prevent="createCategory">
              <v-text-field v-model="form.name" label="名称" placeholder="校园衍生周边"></v-text-field>
              <v-textarea v-model="form.description" label="描述" rows="3" placeholder="用于外部展示"></v-textarea>
              <v-btn type="submit" color="primary" :loading="saving">提交</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="editDialog" max-width="500">
      <v-card>
        <v-card-title>编辑分类</v-card-title>
        <v-card-text>
          <v-text-field v-model="editForm.name" label="名称"></v-text-field>
          <v-textarea v-model="editForm.description" label="描述" rows="3"></v-textarea>
          <v-alert v-if="editError" type="error" dense>{{ editError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="editDialog = false">取消</v-btn>
          <v-btn color="primary" @click="submitEdit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
