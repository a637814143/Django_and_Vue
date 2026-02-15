<script setup>
import { reactive, ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const form = reactive({
  username: "",
  password: "",
});

const loading = ref(false);
const error = ref("");

const handleSubmit = async () => {
  if (loading.value) return;
  error.value = "";
  loading.value = true;
  try {
    await auth.login(form);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : null;
    const fallback = auth.role === "ADMIN" ? "/manage/users" : "/";
    router.push(redirect || fallback);
  } catch (err) {
    error.value = err?.response?.data?.detail || "登录失败，请检查账号密码";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-screen">
    <section class="auth-card glass">
      <p class="eyebrow">校园文创系统</p>
      <h1>欢迎回来</h1>
      <p class="subtitle">请使用校园统一账号登录，继续创意之旅</p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <label>
          用户名
          <input v-model="form.username" placeholder="campus maker" autocomplete="username" required />
        </label>
        <label>
          密码
          <input
            v-model="form.password"
            type="password"
            placeholder="•••••••"
            autocomplete="current-password"
            required
          />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary" type="submit" :disabled="loading">
          {{ loading ? "登录中..." : "登录" }}
        </button>
      </form>

      <p class="switch">
        尚未拥有账号？
        <RouterLink to="/register">立即注册</RouterLink>
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
  background: radial-gradient(circle at top, rgba(168, 230, 207, 0.5), rgba(232, 246, 238, 0.8));
}

.auth-card {
  width: min(480px, 100%);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 24px 0;
}

.subtitle {
  color: #4d6359;
}

.error {
  color: #c53030;
  margin: 0;
}

.switch {
  text-align: center;
  color: #4d6359;
}

.switch a {
  font-weight: 600;
}
</style>
