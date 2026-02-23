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
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>创建账号</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <p class="text-h6 text-center mb-4">加入校园文创生态</p>
            <p class="text-subtitle-1 text-center mb-4">消费者可以快速下单，商家可管理库存，管理员有终极权限</p>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.username"
                label="用户名"
                required
                prepend-inner-icon="mdi-account"
              ></v-text-field>
              <v-text-field
                v-model="form.email"
                label="邮箱"
                type="email"
                required
                prepend-inner-icon="mdi-email"
              ></v-text-field>
              <v-text-field
                v-model="form.password"
                label="密码"
                type="password"
                required
                prepend-inner-icon="mdi-lock"
              ></v-text-field>
              <v-select
                v-model="form.role"
                :items="[{title:'消费者', value: 'CONSUMER'}, {title:'商家', value:'MERCHANT'}]"
                label="选择角色"
                required
                prepend-inner-icon="mdi-account-group"
              ></v-select>
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
                {{ loading ? "创建中..." : "注册并登录" }}
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
             <p class="text-center">
              已有账号？
              <RouterLink to="/login">直接登录</RouterLink>
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
