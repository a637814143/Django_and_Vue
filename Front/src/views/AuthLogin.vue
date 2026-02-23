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
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>校园文创系统</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <p class="text-h6 text-center mb-4">欢迎回来</p>
            <p class="text-subtitle-1 text-center mb-4">请使用校园统一账号登录，继续创意之旅</p>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.username"
                label="用户名"
                placeholder="campus maker"
                autocomplete="username"
                required
                prepend-inner-icon="mdi-account"
              ></v-text-field>
              <v-text-field
                v-model="form.password"
                label="密码"
                type="password"
                placeholder="•••••••"
                autocomplete="current-password"
                required
                prepend-inner-icon="mdi-lock"
              ></v-text-field>
              <v-alert v-if="error" type="error" dense dismissible class="mb-4">
                {{ error }}
              </v-alert>
              <v-btn
                :loading="loading"
                :disabled="loading"
                type="submit"
                color="primary"
                block
                size="large"
              >
                {{ loading ? "登录中..." : "登录" }}
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
             <p class="text-center">
              尚未拥有账号？
              <RouterLink to="/register">立即注册</RouterLink>
            </p>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>
