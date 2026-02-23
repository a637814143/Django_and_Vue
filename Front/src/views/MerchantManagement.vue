<script setup>
import { onMounted, ref } from "vue";
import { accountApi } from "../api";

const merchants = ref([]);
const loading = ref(true);
const error = ref("");

const headers = [
    { text: '用户名', value: 'username' },
    { text: '简介', value: 'headline' },
    { text: '邮箱', value: 'email' },
    { text: '最近登录', value: 'last_login' },
]

const loadMerchants = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await accountApi.users({ role: "MERCHANT" });
    merchants.value = response.results ?? response;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载商家失败";
  } finally {
    loading.value = false;
  }
};

onMounted(loadMerchants);
</script>

<template>
    <v-container fluid>
        <v-card>
            <v-card-title>商家管理</v-card-title>
            <v-card-subtitle>线上 / 线下店铺</v-card-subtitle>
            <v-card-text>
                <v-alert v-if="error" type="error">{{ error }}</v-alert>
                <v-data-table
                    :headers="headers"
                    :items="merchants"
                    :loading="loading"
                    class="elevation-1"
                >
                    <template v-slot:item.last_login="{ item }">
                        {{ item.last_login ? new Date(item.last_login).toLocaleDateString() : "—" }}
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-container>
</template>
