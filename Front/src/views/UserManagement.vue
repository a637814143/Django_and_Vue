<script setup>
import { onMounted, ref, watch } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { accountApi } from "../api";

const users = ref([]);
const loading = ref(true);
const error = ref("");
const filterRole = ref("ALL");
const search = ref("");
const roleOptions = [
  { label: "全部角色", value: "ALL" },
  { label: "管理员", value: "ADMIN" },
  { label: "商家", value: "MERCHANT" },
  { label: "消费者", value: "CONSUMER" },
];

const fetchUsers = async () => {
  loading.value = true;
  error.value = "";
  try {
    const params = {};
    if (filterRole.value !== "ALL") {
      params.role = filterRole.value;
    }
    if (search.value.trim()) {
      params.search = search.value.trim();
    }
    const response = await accountApi.users(params);
    users.value = response.results ?? response;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载用户失败";
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  fetchUsers();
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
      return value;
  }
};

watch(filterRole, () => {
  fetchUsers();
});

onMounted(fetchUsers);
</script>

<template>
  <GlassCard title="用户管理" subtitle="账号一览">
    <div class="controls">
      <select v-model="filterRole">
        <option v-for="option in roleOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <input
        v-model="search"
        placeholder="搜索用户名"
        @keyup.enter="handleSearch"
      />
      <button class="btn-outline" type="button" @click="handleSearch">搜索</button>
      <button class="btn-primary ghost" type="button" @click="fetchUsers">刷新</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="loading" class="loading">加载中...</div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>角色</th>
          <th>邮箱</th>
          <th>最近登录</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ formatRole(user.role) }}</td>
          <td>{{ user.email || "未绑定" }}</td>
          <td>{{ user.last_login ? new Date(user.last_login).toLocaleString() : "—" }}</td>
        </tr>
        <tr v-if="!users.length">
          <td colspan="5" class="empty">暂无数据</td>
        </tr>
      </tbody>
    </table>
  </GlassCard>
</template>

<style scoped>
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid rgba(15, 45, 31, 0.12);
  text-align: left;
}

.empty {
  text-align: center;
  color: #6b7f73;
}

.error {
  color: #b42318;
}

.loading {
  padding: 16px 0;
}

.ghost {
  background: transparent;
  border: 1px solid rgba(15, 45, 31, 0.3);
  color: #0f2d1f;
}
</style>
