<script setup>
import { onMounted, reactive, ref } from "vue";
import { useAuthStore } from "../store/auth";
import { customizationApi } from "../api";

const wishes = ref([]);
const message = ref("");
const form = reactive({
  title: "",
  description: "",
  budget: 0,
  due_date: "",
});

const auth = useAuthStore();

const loadWishes = async () => {
  const res = await customizationApi.list();
  wishes.value = res.results ?? res;
};

const submitWish = async () => {
  message.value = "";
  try {
    await customizationApi.create(form);
    await loadWishes();
    Object.assign(form, { title: "", description: "", budget: 0, due_date: "" });
    message.value = "已提交定制请求";
  } catch (err) {
    message.value = err?.response?.data?.detail || "提交失败";
  }
};

const addNote = async (wish) => {
  const text = prompt("输入互动信息");
  if (!text) return;
  await customizationApi.addTimeline(wish.id, { message: text });
  await loadWishes();
};

const claimWish = async (wish) => {
  if (!["MERCHANT", "ADMIN"].includes(auth.role)) return;
  await customizationApi.assign(wish.id);
  await loadWishes();
};

onMounted(loadWishes);
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>定制请求</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="wish in wishes" :key="wish.id">
                <v-card class="mb-4" outlined>
                  <v-card-title class="d-flex justify-space-between">
                    {{ wish.title }}
                    <v-chip>{{ wish.status }}</v-chip>
                  </v-card-title>
                  <v-card-subtitle>{{ wish.consumer }}</v-card-subtitle>
                  <v-card-text>
                    <p>{{ wish.description }}</p>
                    <p>预算：¥{{ wish.budget || "待确认" }}</p>
                    <div class="timeline">
                      <p v-for="entry in wish.timeline" :key="entry.id">
                        <strong>{{ entry.author }}</strong>：{{ entry.message }}
                      </p>
                    </div>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn text @click="addNote(wish)">互动</v-btn>
                    <v-btn
                      v-if="['MERCHANT', 'ADMIN'].includes(auth.role)"
                      color="primary"
                      @click="claimWish(wish)"
                    >
                      认领
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-list-item>
              <v-list-item v-if="!wishes.length">
                <p>快来发布第一条定制心愿吧</p>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>创建新心愿</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submitWish">
              <v-text-field v-model="form.title" label="主题" required></v-text-field>
              <v-textarea v-model="form.description" label="描述" rows="4" required></v-textarea>
              <v-text-field v-model.number="form.budget" label="预算" type="number" min="0"></v-text-field>
              <v-text-field v-model="form.due_date" label="期望完成日期" type="date"></v-text-field>
              <v-btn type="submit" color="primary">提交</v-btn>
              <p v-if="message">{{ message }}</p>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
