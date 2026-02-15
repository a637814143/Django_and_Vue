<script setup>
import { onMounted, ref, watch } from "vue";
import { accountApi } from "../api";

const users = ref([]);
const loading = ref(true);
const error = ref("");
const filterRole = ref("ALL");
const search = ref("");

const roleOptions = [
  { title: "全部角色", value: "ALL" },
  { title: "管理员", value: "ADMIN" },
  { title: "商家", value: "MERCHANT" },
  { title: "消费者", value: "CONSUMER" },
];

const headers = [
  { title: "ID", key: "id" },
  { title: "用户名", key: "username" },
  { title: "角色", key: "role" },
  { title: "邮箱", key: "email" },
  { title: "最近登录", key: "last_login" },
  { title: "操作", key: "actions", sortable: false },
];

const resetDialog = ref(false);
const resetTarget = ref(null);
const newPassword = ref("");
const resetError = ref("");
const resetting = ref(false);

const fetchUsers = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = {};
    if (filterRole.value !== "ALL") params.role = filterRole.value;
    if (search.value.trim()) params.search = search.value.trim();
    const response = await accountApi.users(params);
    users.value = response.results ?? response;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载用户失败";
  } finally {
    loading.value = false;
  }
};

const formatRole = (value) => {
  switch (value) {
    case "ADMIN":
      return "管理员";
    case "MERCHANT":
      return "商家";
    case "CONSUMER":
      return "消费者";
    default:
      return value || "-";
  }
};

const openReset = (user) => {
  resetTarget.value = user;
  newPassword.value = "";
  resetError.value = "";
  resetDialog.value = true;
};

const submitReset = async () => {
  if (!resetTarget.value) return;
  if (!newPassword.value || newPassword.value.length < 6) {
    resetError.value = "请输入至少 6 位的新密码";
    return;
  }
  resetting.value = true;
  resetError.value = "";
  try {
    await accountApi.resetPassword({ user_id: resetTarget.value.id, password: newPassword.value });
    resetDialog.value = false;
  } catch (err) {
    resetError.value = err?.response?.data?.detail || "重置失败";
  } finally {
    resetting.value = false;
  }
};

watch(filterRole, fetchUsers);

onMounted(fetchUsers);
</script>

<template>
  <v-container fluid>
    <v-card>
      <v-card-title>用户管理</v-card-title>
      <v-card-subtitle>账号一览</v-card-subtitle>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select v-model="filterRole" :items="roleOptions" label="筛选角色"></v-select>
          </v-col>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="search"
              label="搜索用户名"
              append-inner-icon="mdi-magnify"
              @click:append-inner="fetchUsers"
              @keyup.enter="fetchUsers"
              clearable
            ></v-text-field>
          </v-col>
        </v-row>
        <v-alert v-if="error" type="error">{{ error }}</v-alert>
        <v-data-table :headers="headers" :items="users" :loading="loading" class="elevation-1">
          <template #item.role="{ item }">
            {{ formatRole(item.role) }}
          </template>
          <template #item.last_login="{ item }">
            {{ item.last_login ? new Date(item.last_login).toLocaleString() : "未登录" }}
          </template>
          <template #item.actions="{ item }">
            <v-btn size="small" variant="tonal" color="primary" @click="openReset(item)">重置密码</v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="resetDialog" max-width="400">
      <v-card>
        <v-card-title>重置密码</v-card-title>
        <v-card-text>
          <p v-if="resetTarget">正在重置：{{ resetTarget.username }}</p>
          <v-text-field v-model="newPassword" label="新密码" type="password" autofocus></v-text-field>
          <v-alert v-if="resetError" type="error" dense>{{ resetError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="resetDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="resetting" @click="submitReset">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
