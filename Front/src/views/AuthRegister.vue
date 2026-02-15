<script setup>
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const auth = useAuthStore();

const form = reactive({
  username: "",
  email: "",
  password: "",
  role: "CONSUMER",
});

const loading = ref(false);
const error = ref("");

const formatError = (err) => {
  const fallback = "注册失败，请稍后再试";
  const data = err?.response?.data;
  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (Array.isArray(data) && data.length) return data[0];
  if (typeof data === "object") {
    if (typeof data.detail === "string") return data.detail;
    const keys = Object.keys(data);
    if (keys.length) {
      const value = data[keys[0]];
      if (Array.isArray(value) && value.length) return value[0];
      if (typeof value === "string") return value;
    }
  }
  return fallback;
};

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await auth.register({
      username: form.username,
      email: form.email,
      password: form.password,
      desired_role: form.role,
    });
    router.push("/");
  } catch (err) {
    error.value = formatError(err);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-screen">
    <section class="auth-card glass">
      <p class="eyebrow">创建账号</p>
      <h1>加入校园文创生态</h1>
      <p class="subtitle">消费者可以快速下单，商家可管理库存，管理员有终极权限</p>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label>用户名 <input v-model="form.username" required /></label>
        <label>邮箱 <input v-model="form.email" type="email" required /></label>
        <label>密码 <input v-model="form.password" type="password" required /></label>
        <label>
          选择角色
          <select v-model="form.role">
            <option value="CONSUMER">消费者</option>
            <option value="MERCHANT">商家</option>
          </select>
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary" type="submit" :disabled="loading">
          {{ loading ? "创建中..." : "注册并登录" }}
        </button>
      </form>

      <p class="switch">
        已有账号？
        <RouterLink to="/login">直接登录</RouterLink>
      </p>
    </section>
  </div>
</template>

<style scoped>
.auth-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px 16px;
  background: radial-gradient(circle at top, rgba(111, 207, 151, 0.4), rgba(232, 246, 238, 0.9));
}

.auth-card {
  width: min(520px, 100%);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 24px 0;
}

.error {
  color: #c53030;
}

.switch {
  text-align: center;
}
</style>
